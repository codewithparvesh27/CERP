from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CorrectionSession, CorrectionWorkItem, AuditLog
from app.api.schemas import CreateSessionRequest, CreateSessionResponse, SubmitCorrectionRequest, GenerateResponse
from app.services.parser import parse_request, parse_response
from app.services.config_loader import load_error_config
from app.services.correlation import build_work_items
from app.services.patcher import validate_value, generate_revised_request, ValidationError

router = APIRouter(tags=["correction-sessions"])

def to_item_response(item: CorrectionWorkItem) -> dict:
    return {
        "id": str(item.id),
        "conditionCode": item.condition_code,
        "severityCode": item.severity_code,
        "narrativeText": item.narrative_text,
        "scope": item.scope,
        "viewName": item.view_name,
        "sectionName": item.section_name,
        "uiFieldName": item.ui_field_name,
        "uiLabel": item.ui_label,
        "recordId": item.record_id,
        "requestLineNumber": item.request_line_number,
        "requestLineNo": item.request_line_no,
        "fieldName": item.field_name,
        "fieldStart": item.field_start,
        "fieldEnd": item.field_end,
        "currentValue": item.current_value,
        "correctedValue": item.corrected_value,
        "status": item.status,
        "validation": item.validation or {},
    }

@router.post("/correction-sessions", response_model=CreateSessionResponse)
def create_session(req: CreateSessionRequest, db: Session = Depends(get_db)):
    parsed_req = parse_request(req.aceRequestMessage)
    parsed_resp = parse_response(req.aceResponseMessage)
    config = load_error_config()
    items = build_work_items(parsed_req, parsed_resp, config)

    entry_number = None
    if parsed_resp["records"]:
        for r in parsed_resp["records"]:
            if r["record_id"] == "E1" and r["fields"].get("entry_number"):
                entry_number = r["fields"]["entry_number"]
                break

    session = CorrectionSession(entry_number=entry_number, original_request=req.aceRequestMessage, original_response=req.aceResponseMessage)
    db.add(session)
    db.flush()

    db_items = []
    for i in items:
        wi = CorrectionWorkItem(session_id=session.id, **i)
        db.add(wi)
        db_items.append(wi)
    db.add(AuditLog(session_id=session.id, action="SESSION_CREATED", details={"work_item_count": len(items)}))
    db.commit()
    for wi in db_items:
        db.refresh(wi)
    return {"sessionId": str(session.id), "entryNumber": entry_number, "status": session.status, "corrections": [to_item_response(w) for w in db_items]}

@router.get("/correction-sessions/{session_id}/corrections")
def get_corrections(session_id: str, db: Session = Depends(get_db)):
    items = db.query(CorrectionWorkItem).filter(CorrectionWorkItem.session_id == session_id).order_by(CorrectionWorkItem.created_at).all()
    return [to_item_response(i) for i in items]

@router.patch("/correction-sessions/{session_id}/corrections/{item_id}")
def submit_correction(session_id: str, item_id: str, req: SubmitCorrectionRequest, db: Session = Depends(get_db)):
    item = db.query(CorrectionWorkItem).filter(CorrectionWorkItem.id == item_id, CorrectionWorkItem.session_id == session_id).first()
    if not item:
        raise HTTPException(404, "Correction item not found")
    if not item.field_start or not item.field_end:
        raise HTTPException(400, "Correction item is not mapped to a request field")
    try:
        validate_value(req.newValue, item.validation or {}, item.field_start, item.field_end)
    except ValidationError as ex:
        raise HTTPException(400, str(ex))
    old = item.corrected_value or item.current_value
    item.corrected_value = req.newValue
    item.status = "CORRECTED"
    db.add(AuditLog(session_id=session_id, work_item_id=item.id, action="FIELD_CORRECTED", old_value=old, new_value=req.newValue))
    db.commit()
    db.refresh(item)
    return to_item_response(item)

@router.post("/correction-sessions/{session_id}/generate", response_model=GenerateResponse)
def generate(session_id: str, db: Session = Depends(get_db)):
    session = db.query(CorrectionSession).filter(CorrectionSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    items = db.query(CorrectionWorkItem).filter(CorrectionWorkItem.session_id == session_id).all()
    dict_items = [
        {
            "status": i.status,
            "request_line_number": i.request_line_number,
            "field_start": i.field_start,
            "field_end": i.field_end,
            "corrected_value": i.corrected_value,
        }
        for i in items
    ]
    revised = generate_revised_request(session.original_request, dict_items)
    session.revised_request = revised
    session.status = "READY_FOR_RESUBMISSION"
    db.add(AuditLog(session_id=session.id, action="REVISED_REQUEST_GENERATED", details={"corrected_count": sum(1 for i in items if i.status == 'CORRECTED')}))
    db.commit()
    return {"sessionId": str(session.id), "status": session.status, "revisedAceRequestMessage": revised}

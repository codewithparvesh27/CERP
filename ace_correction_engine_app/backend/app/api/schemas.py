from pydantic import BaseModel
from typing import Any

class CreateSessionRequest(BaseModel):
    aceRequestMessage: str
    aceResponseMessage: str

class CorrectionItemResponse(BaseModel):
    id: str
    conditionCode: str
    severityCode: str | None
    narrativeText: str | None
    scope: str | None
    viewName: str | None
    sectionName: str | None
    uiFieldName: str | None
    uiLabel: str | None
    recordId: str | None
    requestLineNumber: int | None
    requestLineNo: str | None
    fieldName: str | None
    fieldStart: int | None
    fieldEnd: int | None
    currentValue: str | None
    correctedValue: str | None
    status: str
    validation: dict[str, Any]

class CreateSessionResponse(BaseModel):
    sessionId: str
    entryNumber: str | None
    status: str
    corrections: list[CorrectionItemResponse]

class SubmitCorrectionRequest(BaseModel):
    newValue: str

class GenerateResponse(BaseModel):
    sessionId: str
    status: str
    revisedAceRequestMessage: str

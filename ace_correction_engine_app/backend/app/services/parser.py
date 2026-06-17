from app.domain.field_specs import RECORD_LENGTH, REQUEST_SPECS, RESPONSE_SPECS, FieldSpec

class ParseError(Exception):
    pass

def normalize_payload(payload: str) -> list[str]:
    lines = payload.splitlines()
    normalized = []
    for idx, line in enumerate(lines, start=1):
        if len(line) > RECORD_LENGTH:
            raise ParseError(f"Line {idx} length {len(line)} exceeds {RECORD_LENGTH}")
        normalized.append(line.ljust(RECORD_LENGTH))
    return normalized

def detect_record_id(line: str) -> str:
    if line[:2] in {"E0", "E1"}:
        return line[:2]
    if line[:1] in {"A", "B", "Y", "Z"}:
        return line[:1]
    return line[:2]

def parse_record(line: str, line_number: int, specs: dict[str, list[FieldSpec]]) -> dict:
    rid = detect_record_id(line)
    if rid not in specs:
        raise ParseError(f"Unsupported record {rid} at line {line_number}")
    fields = {s.name: s.extract(line) for s in specs[rid]}
    definitions = {s.name: {"start": s.start, "end": s.end, "description": s.description} for s in specs[rid]}
    return {"record_id": rid, "line_number": line_number, "raw": line, "fields": fields, "field_definitions": definitions}

def parse_request(payload: str) -> dict:
    records = [parse_record(line, i, REQUEST_SPECS) for i, line in enumerate(normalize_payload(payload), start=1)]
    return {"records": records, "indexes": build_request_indexes(records)}

def parse_response(payload: str) -> dict:
    records = [parse_record(line, i, RESPONSE_SPECS) for i, line in enumerate(normalize_payload(payload), start=1)]
    events = []
    ctx = []
    for rec in records:
        if rec["record_id"] == "E0":
            ctx.append(rec)
        elif rec["record_id"] == "E1":
            events.append({"context": ctx, "condition": rec})
            ctx = []
    if ctx:
        events.append({"context": ctx, "condition": None})
    return {"records": records, "events": events}

def build_request_indexes(records: list[dict]) -> dict:
    by_record_id = {}
    line_groups = {}
    current_line = None
    for rec in records:
        rid = rec["record_id"]
        by_record_id.setdefault(rid, []).append(rec)
        if rid == "40":
            current_line = rec["fields"].get("line_item_identifier")
            line_groups[current_line] = {"40": rec, "44": [], "47": [], "50": [], "54": []}
        elif current_line and rid in {"44", "47", "50", "54"}:
            line_groups[current_line][rid].append(rec)
    return {"by_record_id": by_record_id, "line_groups": line_groups}

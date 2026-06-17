from app.domain.field_specs import REQUEST_SPECS

def _e0_value(event: dict, ref_type: str) -> str | None:
    for ctx in event.get("context", []):
        if ctx["fields"].get("reference_data_type_code") == ref_type:
            return ctx["fields"].get("reference_data_text") or ctx["fields"].get("occurrence_position")
    return None

def _line_no(event: dict) -> str | None:
    value = _e0_value(event, "LINITM")
    if not value:
        return None
    return value.strip()[-3:].zfill(3)

def find_rule(event: dict, config: list[dict]) -> dict | None:
    cond = event.get("condition")
    if not cond:
        return None
    code = cond["fields"].get("condition_code")
    severity = cond["fields"].get("severity_code")
    context_types = {c["fields"].get("reference_data_type_code") for c in event.get("context", [])}
    for rule in config:
        if rule.get("errorCode") != code:
            continue
        if rule.get("severity") and rule.get("severity") != severity:
            continue
        expected_ref = rule.get("responseContext", {}).get("e0ReferenceType")
        if expected_ref and expected_ref not in context_types:
            continue
        return rule
    return None

def locate_request_record(parsed_request: dict, event: dict, rule: dict) -> tuple[dict | None, str | None]:
    locator = rule.get("requestLocator", {})
    record_id = locator.get("recordId")
    field_name = locator.get("fieldName")
    line_no = _line_no(event)
    indexes = parsed_request["indexes"]

    if record_id in {"40", "44", "47", "50", "54"} and line_no:
        group = indexes["line_groups"].get(line_no)
        if not group:
            return None, line_no
        candidates = group.get(record_id, []) if record_id != "40" else [group["40"]]
        if record_id == "50":
            hts = _e0_value(event, "TARIFF")
            if hts:
                for rec in candidates:
                    if rec["fields"].get("hts_number") == hts.strip():
                        return rec, line_no
        if record_id == "47" and locator.get("partyType"):
            for rec in candidates:
                if rec["fields"].get("party_type") == locator["partyType"]:
                    return rec, line_no
        return candidates[0] if candidates else None, line_no

    candidates = indexes["by_record_id"].get(record_id, [])
    return (candidates[0] if candidates else None), line_no

def build_work_items(parsed_request: dict, parsed_response: dict, config: list[dict]) -> list[dict]:
    items = []
    for event in parsed_response["events"]:
        cond = event.get("condition")
        if not cond:
            continue
        rule = find_rule(event, config)
        if not rule:
            items.append({
                "condition_code": cond["fields"].get("condition_code"),
                "severity_code": cond["fields"].get("severity_code"),
                "disposition_type_code": cond["fields"].get("disposition_type_code"),
                "narrative_text": cond["fields"].get("narrative_text"),
                "scope": "UNMAPPED",
                "status": "MANUAL_REVIEW",
                "raw_response_context": event.get("context", []),
                "raw_response_condition": cond,
                "validation": {},
            })
            continue
        rec, line_no = locate_request_record(parsed_request, event, rule)
        field_name = rule["requestLocator"].get("fieldName")
        spec = next((s for s in REQUEST_SPECS[rule["requestLocator"]["recordId"]] if s.name == field_name), None)
        current_value = rec["fields"].get(field_name) if rec else None
        items.append({
            "condition_code": cond["fields"].get("condition_code"),
            "severity_code": cond["fields"].get("severity_code"),
            "disposition_type_code": cond["fields"].get("disposition_type_code"),
            "narrative_text": cond["fields"].get("narrative_text"),
            "scope": rule.get("scope"),
            "view_name": rule.get("uiTarget", {}).get("view"),
            "section_name": rule.get("uiTarget", {}).get("section"),
            "ui_field_name": rule.get("uiTarget", {}).get("field"),
            "ui_label": rule.get("uiTarget", {}).get("label"),
            "record_id": rule["requestLocator"].get("recordId"),
            "request_line_number": rec.get("line_number") if rec else None,
            "request_line_no": line_no,
            "field_name": field_name,
            "field_start": spec.start if spec else None,
            "field_end": spec.end if spec else None,
            "current_value": current_value,
            "status": "PENDING" if rec else "MANUAL_REVIEW",
            "raw_response_context": event.get("context", []),
            "raw_response_condition": cond,
            "validation": rule.get("validation", {}),
        })
    return items

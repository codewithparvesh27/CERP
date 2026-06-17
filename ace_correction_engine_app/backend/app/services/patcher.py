from app.domain.field_specs import RECORD_LENGTH

class ValidationError(Exception):
    pass

def validate_value(value: str, validation: dict, field_start: int, field_end: int):
    max_len = field_end - field_start + 1
    if validation.get("required") and value == "":
        raise ValidationError("Value is required")
    if len(value) > validation.get("maxLength", max_len):
        raise ValidationError(f"Value exceeds max length {validation.get('maxLength', max_len)}")
    if validation.get("length") and len(value) != validation["length"]:
        raise ValidationError(f"Value must be exactly {validation['length']} characters")

def patch_line(raw: str, start: int, end: int, new_value: str, pad_char: str = " ", pad_direction: str = "right") -> str:
    length = end - start + 1
    if len(new_value) > length:
        raise ValidationError(f"Value length {len(new_value)} exceeds field length {length}")
    padded = new_value.rjust(length, pad_char) if pad_direction == "left" else new_value.ljust(length, pad_char)
    new_raw = raw[:start - 1] + padded + raw[end:]
    if len(new_raw) != RECORD_LENGTH:
        raise ValidationError("Patched line is not 80 characters")
    return new_raw

def generate_revised_request(original_request: str, work_items: list[dict]) -> str:
    lines = [line.ljust(RECORD_LENGTH) for line in original_request.splitlines()]
    for item in work_items:
        if item.get("status") != "CORRECTED":
            continue
        idx = item["request_line_number"] - 1
        lines[idx] = patch_line(lines[idx], item["field_start"], item["field_end"], item["corrected_value"])
    return "\r\n".join(lines) + "\r\n"

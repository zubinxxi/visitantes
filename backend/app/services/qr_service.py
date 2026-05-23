import re
import json

CEDULA_REGEX = re.compile(r"^(\d{1,2})-(\d{3,4})-(\d{4,7})$")


def parse_cedula_qr(raw_data: str) -> dict:
    trimmed = raw_data.strip()

    if "]" in trimmed:
        cedula = trimmed.split("]")[0].strip().replace("'", "-")
        if CEDULA_REGEX.match(cedula):
            return {"cedula": cedula, "format": "panama_cedula"}
        return {"cedula": cedula, "format": "raw"}

    match = CEDULA_REGEX.match(trimmed)
    if match:
        return {
            "cedula": trimmed,
            "provincia": match.group(1),
            "tomo": match.group(2),
            "numero": match.group(3),
            "format": "panama_cedula",
        }

    if trimmed.startswith("{"):
        try:
            data = json.loads(trimmed)
            return {**data, "format": "json"}
        except json.JSONDecodeError:
            pass

    return {"cedula": trimmed, "format": "raw"}


def validate_cedula(cedula: str) -> bool:
    return bool(CEDULA_REGEX.match(cedula.strip()))

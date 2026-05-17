import re


COMPATIBLE_TYPES = {
    "real": ["real", "float", "double"],
    "float": ["real", "float", "double"],
    "word": ["word", "int", "integer"],
    "int": ["word", "int", "integer"],
    "bool": ["bool", "boolean"],
}


def normalize(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', text.lower())


def compatible_type(type1: str, type2: str) -> bool:
    t1 = type1.lower()
    t2 = type2.lower()

    if t1 == t2:
        return True

    return t2 in COMPATIBLE_TYPES.get(t1, [])


def calculate_schema_compatibility(source_schema, target_schema):
    score = 0
    reasons = []

    source_block = normalize(source_schema["block_type"])
    target_block = normalize(target_schema["block_type"])

    if source_block in target_block or target_block in source_block:
        score += 40
        reasons.append("Block types are similar")

    source_pins = source_schema.get("pins", [])
    target_pins = target_schema.get("pins", [])

    source_params = source_schema.get("parameters", [])
    target_params = target_schema.get("parameters", [])

    if source_pins and target_pins:
        score += 20
        reasons.append("Both schemas contain pins")

    if source_params and target_params:
        score += 20
        reasons.append("Both schemas contain parameters")

    type_matches = 0

    for source_pin in source_pins:
        for target_pin in target_pins:
            if compatible_type(
                source_pin.get("type", ""),
                target_pin.get("type", ""),
            ):
                type_matches += 1
                break

    if type_matches > 0:
        score += 20
        reasons.append(f"Found {type_matches} compatible field types")

    if score >= 80:
        status = "Compatible"
    elif score >= 50:
        status = "Possibly Compatible"
    else:
        status = "Likely Incompatible"

    return {
        "score": score,
        "status": status,
        "reasons": reasons,
    }
def _is_state(line: str) -> bool:
    valid_states = ['offline', 'disabled', 'detached', 'child', 'router', 'leader']
    cleaned = line.strip()
    for s in valid_states:
        if s in cleaned:
            return True

    return False

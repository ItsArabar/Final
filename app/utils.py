def validate_number_input(value: str) -> float:
    """Convert string input to float.
    Raises:
        ValueError: If input cannot be converted to float
    """
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number input: {value}")

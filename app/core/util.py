def list_apply_defaults(values, defaults):
    """
    Apply default values to a list on the first
    n elements that are not yet defined.
    """
    return values + defaults[len(values):]

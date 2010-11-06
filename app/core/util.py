def list_apply_defaults(values, defaults):
    """
    Apply default values to a list on the first
    n elements that are not yet defined.
    """
    return values + defaults[len(values):]

class ValueObject(object):
    """
    Create object containing attributes
    without the possibility to change them
    afterwards.
    """
    def __init__(self, a_dict):
        self._dict = a_dict.copy()

    def __getattr__(self, name):
        return self._dict[name]

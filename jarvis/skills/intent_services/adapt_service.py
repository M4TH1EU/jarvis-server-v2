from adapt.intent import IntentBuilder


class AdaptIntent(IntentBuilder):
    """Wrapper for IntentBuilder setting a blank name.
    Args:
        name (str): Optional name of intent
    """
    def __init__(self, name=''):
        super().__init__(name)
# Original : https://github.com/MycroftAI/mycroft-core/blob/dev/mycroft/skills/mycroft_skill/decorators.py

"""Decorators for use with JarvisSkill methods"""


def intent_handler(intent_parser):
    """Decorator for adding a method as an intent handler."""

    def real_decorator(func):
        # Store the intent_parser inside the function
        # This will be used later to call register_intent
        if not hasattr(func, 'intents'):
            func.intents = []
        func.intents.append(intent_parser)
        return func

    return real_decorator


def intent_file_handler(intent_file):
    """Decorator for adding a method as an intent file handler.
    This decorator is deprecated, use intent_handler for the same effect.
    """

    def real_decorator(func):
        # Store the intent_file inside the function
        # This will be used later to call register_intent_file
        if not hasattr(func, 'intent_files'):
            func.intent_files = []
        func.intent_files.append(intent_file)
        return func

    return real_decorator


def resting_screen_handler(name):
    """Decorator for adding a method as an resting screen handler.
    If selected will be shown on screen when device enters idle mode.
    """

    def real_decorator(func):
        # Store the resting information inside the function
        # This will be used later in register_resting_screen
        if not hasattr(func, 'resting_handler'):
            func.resting_handler = name
        return func

    return real_decorator


def skill_api_method(func):
    """Decorator for adding a method to the skill's public api.
    Methods with this decorator will be registered on the message bus
    and an api object can be created for interaction with the skill.
    """
    # tag the method by adding an api_method member to it
    if not hasattr(func, 'api_method') and hasattr(func, '__name__'):
        func.api_method = True
    return func

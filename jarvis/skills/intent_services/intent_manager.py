import importlib
import types

from adapt.engine import DomainIntentDeterminationEngine

from jarvis import api

adapt_engine = DomainIntentDeterminationEngine()

intents_handlers_adapt = dict()


def register_entity_adapt(entity_value, entity_type, domain):
    adapt_engine.register_entity(entity_value=entity_value, entity_type=entity_type, domain=domain)
    print("[Adapt]: Added entity with type " + entity_type + " for " + domain)


def register_regex_adapt(regex, domain):
    adapt_engine.register_regex_entity(regex, domain)
    print("[Adapt]: Added new regex for " + domain)


def register_intent_adapt(intent, domain):
    adapt_engine.register_intent_parser(intent, domain=domain)
    print("[Adapt]: Registered new intent " + intent.name + " for skill " + domain + ".")


def load_all_skills():
    for handler in intents_handlers_adapt:
        function_handler = intents_handlers_adapt.get(handler)
        intent_builder = getattr(function_handler[0], "_data", [])[0]
        skill_name = function_handler[1]
        register_intent_adapt(intent_builder.build(), domain=skill_name)
        print("Loaded " + skill_name)


def look_for_matching_skill(sentence):
    if len(intents_handlers_adapt) > 0:
        try:
            best_intents = adapt_engine.determine_intent(sentence, 100)
            best_intent = next(best_intents)

            if (get_confidence(best_intent) > 0.2):
                return best_intent

        except StopIteration:
            pass

    return None  # No match (Adapt)


def get_confidence(intent):
    if intent is None:
        return 0

    if 'confidence' in intent:
        return intent['confidence']
    elif hasattr(intent, 'conf'):
        return intent.conf
    else:
        return 0


def handle_adapt_intent(data, intent):
    for key, val in intent.items():
        if key != 'intent_type' and key != 'target' and key != 'confidence':
            data[key] = val
    handle(intent['intent_type'], data=data)
    return intent


def handle(intent_name, data):
    module_path_str = None
    handler_method_name = None

    if intent_name in intents_handlers_adapt:
        handler_method_name = intents_handlers_adapt.get(intent_name)[2]
        module_path_str = intents_handlers_adapt.get(intent_name)[3]

    if module_path_str is not None and handler_method_name is not None:
        # import the create_skill method from the skill using the skill module path
        create_skill_method = import_method_from_string(module_path_str, "create_skill")

        skill_init_data = {'client_ip': data['client_ip'], 'client_port': data['client_port']}

        # create a new object of the right skill for the utterance
        skill = create_skill_method(skill_init_data)

        # import and call the handler method from the skill
        getattr(skill, handler_method_name)(data=data)


def import_method_from_string(file, method_name):
    """
    Add the possibility to import method dynamically using a string like "skill.daily.date_and_time.intent" as file and
    "what_time_is_it" as method_name
    """
    mod = importlib.import_module(file)
    met = getattr(mod, method_name)

    return met


def recognise(sentence, uuid=None):
    print("RECOGNISE " + sentence)
    # TODO: find why not working
    api.send_jarvis_message_to_room("Not implemented that yet, please wait.", uuid)


class SkillRegistering(type):
    def __init__(cls, name, bases, attrs):
        for key, val in attrs.items():
            if type(val) is types.FunctionType and not str(val).__contains__("__"):
                intent_type = getattr(val, "_type", None)

                if intent_type is not None:
                    properties = getattr(val, "_data", None)

                    if properties is not None:
                        if intent_type == 'adapt':
                            intent = properties[0]
                            intent_name = intent.name

                            intents_handlers_adapt[f"{intent_name}"] = [getattr(cls, key), name, key,
                                                                                       attrs['__module__']]

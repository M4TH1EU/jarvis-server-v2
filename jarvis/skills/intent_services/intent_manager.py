import importlib
import json
import types

from adapt.engine import DomainIntentDeterminationEngine
from padatious import IntentContainer

from jarvis import api

adapt_engine = DomainIntentDeterminationEngine()
padatious_intents_container = IntentContainer('intent_cache')

intents_handlers_adapt = dict()
intents_handlers_padatious = dict()


def register_entity_adapt(entity_value, entity_type, domain):
    adapt_engine.register_entity(entity_value=entity_value, entity_type=entity_type, domain=domain)
    print("[Adapt]: Added entity with type " + entity_type + " for " + domain)


def register_regex_adapt(regex, domain):
    adapt_engine.register_regex_entity(regex, domain)
    print("[Adapt]: Added new regex for " + domain)


def register_intent_adapt(intent, domain):
    adapt_engine.register_intent_parser(intent, domain=domain)
    print("[Adapt]: Registered new intent " + intent.name + " for skill " + domain + ".")


def register_entity_padatious(entity_name, file_lines_list):
    padatious_intents_container.add_entity(entity_name, file_lines_list)
    # print("[Padatious]: Added entity with name " + entity_name + " with " str(len(list)) + "examples.")


def register_intent_padatious(intent_name, list_of_intent_examples):
    padatious_intents_container.add_intent(intent_name, list_of_intent_examples)
    print("[Padatious]: Registered new intent " + intent_name + " with " + str(
        len(list_of_intent_examples)) + " examples.")


def train_padatious():
    print("Training PADATIOUS intents models, can take a few minutes (first time) or a few seconds (startup)")
    padatious_intents_container.train(timeout=120)


def load_all_skills():
    for handler in intents_handlers_adapt:
        function_handler = intents_handlers_adapt.get(handler)
        intent_builder = getattr(function_handler[0], "_data", [])[0]
        skill_name = function_handler[1]
        register_intent_adapt(intent_builder.build(), domain=skill_name)
        print("Loaded " + skill_name)

    for handler in intents_handlers_padatious:
        function_handler = intents_handlers_padatious.get(handler)
        intent_data_examples = function_handler[1]
        register_intent_padatious(handler, intent_data_examples)
        print("Loaded " + intent_data_examples)


def look_for_matching_intent(sentence):
    best_intent_adapt = get_best_intent_adapt(sentence)
    best_intent_padatious = get_best_intent_padatious(sentence)

    confidence_adapt = get_confidence(best_intent_adapt)
    confidence_padatious = get_confidence(best_intent_padatious)

    return best_intent_adapt if confidence_adapt > confidence_padatious else best_intent_padatious


def get_best_intent_adapt(sentence):
    if len(intents_handlers_adapt) > 0:
        try:
            best_intents = adapt_engine.determine_intent(sentence, 100)
            best_intent = next(best_intents)

            return best_intent

        except StopIteration:
            pass

    return None  # No match (Adapt)


def get_best_intent_padatious(sentence):
    if len(intents_handlers_padatious) > 0:
        result = padatious_intents_container.calc_intent(sentence)
        return result
    else:
        return None  # No match (Padatious)


def get_confidence(intent):
    if intent is None:
        return 0

    if 'confidence' in intent:
        return intent['confidence']
    elif hasattr(intent, 'conf'):
        return intent.conf
    else:
        return 0


def handle_intent(data, intent):
    # Handle Adapt
    if 'intent_type' in intent:
        for key, val in intent.items():
            if key != 'intent_type' and key != 'target' and key != 'confidence':
                data[key] = val
        launch_intent(intent['intent_type'], data=data)
        return intent

    # Handle padatious
    elif hasattr(intent, 'name'):
        data.update(intent.matches)  # adding the matches from padatious to the data
        launch_intent(intent.name, data)
        return json.dumps(str(intent))


def launch_intent(intent_name, data):
    module_path_str = None
    handler_method_name = None

    if intent_name in intents_handlers_adapt:
        handler_method_name = intents_handlers_adapt.get(intent_name)[2]
        module_path_str = intents_handlers_adapt.get(intent_name)[3]

    if intent_name in intents_handlers_padatious:
        handler_method_name = intents_handlers_padatious.get(intent_name)[0]
        module_path_str = intents_handlers_padatious.get(intent_name)[2]

    if module_path_str is not None and handler_method_name is not None:
        # import the create_skill method from the skill using the skill module path
        create_skill_method = import_method_from_string(module_path_str, "create_skill")

        # create a new object of the right skill for the utterance
        skill = create_skill_method(data)

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

    launch_intent(look_for_matching_intent(sentence))

    # TODO: find why not working
    api.send_jarvis_message_to_room("Not implemented that yet, please wait.", uuid)


class SkillRegistering(type):
    def __init__(cls, name, bases, attrs):
        for key, val in attrs.items():
            if type(val) is types.FunctionType and not str(val).__contains__("__"):
                intent_type = getattr(val, "_type", None)
                properties = None

                if intent_type is not None:
                    properties = getattr(val, "_data", None)

                if properties is not None:
                    if intent_type == 'adapt':
                        intent = properties[0]
                        intent_name = intent.name

                        intents_handlers_adapt[f"{intent_name}"] = [getattr(cls, key), name, key,
                                                                    attrs['__module__']]

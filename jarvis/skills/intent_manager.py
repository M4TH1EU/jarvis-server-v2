import importlib

from adapt.engine import DomainIntentDeterminationEngine

adapt_engine = DomainIntentDeterminationEngine()

intents_handlers_adapt = dict()
intents_handlers_padatious = dict()


def register_entity_adapt(entity_value, entity_type, domain):
    adapt_engine.register_entity(entity_value=entity_value, entity_type=entity_type, domain=domain)
    # print("[Adapt]: Added entity with type " + entity_type + " for " + domain)


def register_regex_adapt(regex, domain):
    adapt_engine.register_regex_entity(regex, domain)
    # print("[Adapt]: Added new regex for " + domain)


def register_intent_adapt(intent, domain):
    adapt_engine.register_intent_parser(intent, domain=domain)
    print("[Adapt]: Registered new intent " + intent.name + " for skill " + domain + ".")


def load_all_skills():
    for handler in intents_handlers_adapt:
        function_handler = intents_handlers_adapt.get(handler)
        intent_builder = getattr(function_handler[0], "_data", [])[0]
        skill_name = function_handler[1]
        register_intent_adapt(intent_builder.build(), domain=skill_name)


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
    Add the possibility to import method dynamically using a string like "skills.daily.date_and_time.intent" as file and
    "what_time_is_it" as method_name
    """
    mod = importlib.import_module(file)
    met = getattr(mod, method_name)

    return met


def recognise(sentence, client_ip=None, client_port=None):
    sentence = sentence.lower()
    print(sentence)

    data = dict()
    data['client_ip'] = client_ip
    data['client_port'] = client_port
    data['utterance'] = sentence

    best_intent_adapt = get_best_intent_adapt(sentence)

    confidence_adapt = get_confidence(best_intent_adapt)

    if confidence_adapt < 0.2:

        # TODO: implement fallback to something like wolfram alpha or smart assistant
        # Nothing found at all
        return "I didn't understand..."
    else:
        return handle_adapt_intent(data, best_intent_adapt)


def get_confidence(intent):
    if intent is None:
        return 0

    if 'confidence' in intent:
        return intent['confidence']
    elif hasattr(intent, 'conf'):
        return intent.conf
    else:
        return 0


def get_best_intent_adapt(sentence):
    if len(intents_handlers_adapt) > 0:
        try:
            best_intents = adapt_engine.determine_intent(sentence, 100)
            best_intent = next(best_intents)

            return best_intent

        except StopIteration:
            pass

    return None  # No match (Adapt)


def handle_adapt_intent(data, intent):
    for key, val in intent.items():
        if key != 'intent_type' and key != 'target' and key != 'confidence':
            data[key] = val
    handle(intent['intent_type'], data=data)
    return intent

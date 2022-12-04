import os

from jarvis import get_path_file
from jarvis.skills.intent_services import intent_manager
from jarvis.utils import languages_utils, file_utils


class JarvisSkill:

    def __init__(self, name=None):
        self.name = name or self.__class__.__name__

        path = self.__module__.split(".")
        self.skill_folder = path[2]
        self.path = os.path.dirname(get_path_file.__file__) + "/skills/" + self.skill_folder

    def register(self):
        self.register_entities_adapt()
        self.register_regex()
        print("[" + self.name + "] Registered entity/entities and regex(s)")

    def register_entities_adapt(self):
        path = self.path + "/vocab/" + languages_utils.get_language() + "/*.voc"

        all_lines_by_file_dict = file_utils.read_all_files_in_folder(path, return_as_dict_with_filename=True)

        for filename in all_lines_by_file_dict:
            for line in all_lines_by_file_dict.get(filename):
                intent_manager.register_entity_adapt(line, filename, self.name)

    def register_regex(self):
        path = self.path + "/regex/" + languages_utils.get_language() + "/*.rx"

        result = file_utils.read_all_files_in_folder(path)
        for line in result:
            intent_manager.register_regex_adapt(line, self.name)

    def speak(self, utterance, expect_response=False, wait=False, meta=None):
        print("SPEAK : " + utterance)
        pass

    def speak_dialog(self, key, data=None, expect_response=False, wait=False):
        print("SPEAK DIALOG : " + key + " data : " + data)

        pass

    def set_context(self, context, word='', origin=''):
        pass
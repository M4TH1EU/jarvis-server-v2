import api
import lingua_franca

from jarvis.skills.cocktails import CocktailSkill
from jarvis.skills.intent_services import intent_manager

if __name__ == '__main__':

    # Load lingua franca in the memory
    lingua_franca.load_language(lang="fr")

    # Register each skills
    CocktailSkill().register()

    # Load the skills
    intent_manager.load_all_skills()

    # Start the api endpoint
    api.start_server()

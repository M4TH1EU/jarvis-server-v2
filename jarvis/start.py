import api
import lingua_franca


if __name__ == '__main__':

    # Load lingua franca in the memory
    lingua_franca.load_language(lang="fr")

    # Load skills
    # JokesSkill().register()

    # Start the api endpoint
    api.start_server()

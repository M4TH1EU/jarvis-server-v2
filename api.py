import json
import tempfile

import requests
from flask import request, Flask

app = Flask(__name__)


# .WAV (i.e.) FILE REQUEST
@app.route("/process_audio_request_file", methods=['POST'])
def process_audio_request_android():
    print("[" + request.remote_addr + "] - New STT request")

    audio_temp_file = tempfile.NamedTemporaryFile(prefix='jarvis-audio_', suffix='_client')
    audio_temp_file.write(request.data)
    print(audio_temp_file.name)

    return {"transcription": text_recognition_whisperasr(audio_temp_file.name), "answer": "WIP"}


# send request to whisper-asr server (docker)
def text_recognition_whisperasr(audio_file):
    headers = {
        'accept': 'application/json',
        # 'Content-Type': 'multipart/form-data',
    }

    params = {
        'task': 'transcribe',
        # TODO: add to config
        'language': 'fr',
        'output': 'json',
    }

    files = {
        'audio_file': open(audio_file, 'rb'),
    }

    # TODO: add to config
    response = requests.post('http://192.168.1.208:9000/asr', params=params, headers=headers, files=files)
    return json.loads(response.text)['text']


# NOT IMPLEMENTED RIGHT NOW / to use with local whisper cpp (cpu)
"""
def local_recognition(audio_file, time_of_request):
    path = os.path.dirname(get_path_file.__file__)

    print("Loading model and recognition")
    model = path + "/whisper/models/" + "ggml-small.bin"
    os.system(path + "/whisper/main -l fr -t 8 -m " + model + " -f " + audio_file + " -otxt")  # + "> /dev/null 2>&1")

    output = open(audio_file + ".txt").read()

    # time_of_resolution = time.perf_counter()
    # print(output + f" - {time_of_resolution - time_of_request:0.4f} seconds")

    return jsonify(transcription=output, time=5, answer="WIP...")
"""


def start_server():
    app.config['JSON_AS_ASCII'] = False
    # TODO: add to config
    app.run(port=5000, debug=False, host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    start_server()

import json
import sys
import tempfile
from threading import Lock

import openai
import requests
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    rooms
from pywhispercpp.model import Model

from jarvis.utils.chatgpt_utils import chatgpt_recognise

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
model = Model('base', n_threads=16, suppress_non_speech_tokens=True)
openai.api_key = sys.argv[1]


@app.route('/')
def index():
    return "Welcome to Jarvis Server API !"


@socketio.event
def process_message(message):
    message = json.loads(message)
    print("New PROCESS request from room " + message['uuid'])

    print("Message : " + message['data'])
    # TODO: maybe implement grammar check ?

    # intent_manager.recognise(message['data'], message['uuid'])
    send_jarvis_message_to_room("I don't know how to respond to that...", message['uuid'])

    response = chatgpt_recognise(message['data'])
    if 'comment' in response:
        send_user_message_to_room(response['comment'], message['uuid'])
    else:
        send_jarvis_message_to_room("I don't know how to respond to that...", message['uuid'])


@socketio.event
def join(message):
    message = json.loads(message)
    print("New client joined room " + message['uuid'])
    join_room(message['uuid'])


@socketio.event
def leave(message):
    leave_room(message['uuid'])
    emit('my_response', 'In rooms: ' + ', '.join(rooms()))


@socketio.event
def connect():
    global thread
    emit('my_response', {'data': 'Connected', 'count': 0})


def send_user_message_to_room(text, room_id):
    socketio.emit('message_from_user', {'data': text, "uuid": room_id}, to=room_id)


def send_jarvis_message_to_room(text, room_id):
    socketio.emit('message_from_jarvis', {'data': text, "uuid": room_id}, to=room_id)


# .WAV (i.e.) FILE REQUEST
@app.route("/get_text_from_audio", methods=['POST'])
def get_text_from_audio():
    print("[" + request.remote_addr + "] - New STT request")

    audio_temp_file = tempfile.NamedTemporaryFile(prefix='jarvis-audio_', suffix='_client')
    audio_temp_file.write(request.data)

    # text = whisper_stt(audio_temp_file.name)
    text = whisper_cpp_stt(audio_temp_file.name)
    print(text)

    return {"data": text, "uuid": "null"}


"""
@app.route("/process_text", methods=['POST'])
def process_text():
    print("[" + request.remote_addr + "] - New TXT request")

    text = request.values['text']

    answer = intent_manager.recognise(text, request.headers.get('Client-Ip'), request.headers.get('Client-Port'))

    return {"transcription": text, "answer": answer}"""


# send request to whisper-asr server (docker)
def whisper_stt(audio_file):
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
    response = requests.post('https://whisper.broillet.ch/asr', params=params, headers=headers, files=files)
    return json.loads(response.text)['text']


def whisper_cpp_stt(audio_file):
    segments = model.transcribe(audio_file, speed_up=False, translate=False)

    # combines all segments in one string
    text = ''
    for segment in segments:
        text += segment.text + ' '

    return text


def start_server():
    socketio.run(app, host='0.0.0.0', port=6000, allow_unsafe_werkzeug=True)

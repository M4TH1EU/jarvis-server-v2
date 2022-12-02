import json
import tempfile
from threading import Lock

import requests
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@app.route('/')
def index():
    # return render_template('index.html', async_mode=socketio.async_mode)
    return "Welcome to Jarvis Server API !"


@socketio.event
def process_message(message):
    message = json.loads(message)

    text = message['data']

    send_jarvis_message_to_room(text, message['uuid'])

    emit('my_response', message)


@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.event
def join(message):
    message = json.loads(message)
    join_room(message['uuid'])


@socketio.event
def leave(message):
    leave_room(message['uuid'])
    emit('my_response','In rooms: ' + ', '.join(rooms()))


@socketio.on('close_room')
def on_close_room(message):
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response', {'data': 'Disconnected!', 'count': session['receive_count']}, callback=can_disconnect)


@socketio.event
def connect():
    global thread
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


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
    print(audio_temp_file.name)

    text = whisper_stt(audio_temp_file.name)

    # TODO: send to each skill to answer the questions

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


def start_server():
    socketio.run(app, host='0.0.0.0', port=6000, allow_unsafe_werkzeug=True)

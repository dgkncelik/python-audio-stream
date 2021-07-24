# -*- coding: utf-8 -*-
import io
from flask import Flask
from flask import render_template
import pyaudio
import wave
from flask_socketio import SocketIO
import json

app = Flask(__name__, static_folder="js",
            template_folder="templates")
app.config['SECRET_KEY'] = 'test'


class jhandler(object):

    def loads(self, o, **kwargs):
        print('TEST')
        print(o)
        return o

    def dumps(self, o, **kwargs):
        print('TEST')
        print(o)
        return json.dumps(o)


jo = jhandler()

skt = SocketIO(app, engineio_logger=True, logger=True)
p = pyaudio.PyAudio()
AUDIO_CHUNK = 4096


@app.route('/js/<path:path>')
def send_js(path):
    return app.send_static_file(path)


@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


def play_audio_chunk(audio_chunk):
    file_object = io.BytesIO()
    # b = list(audio_chunk)
    # ac = bytes(b)
    # ac = bytes(audio_chunk, encoding="raw_unicode_escape")
    # BINARYIN NUNE WAVE ETIKETINI EKLE O SEKILDE GONDER
    file_object.write(audio_chunk)
    file_object.seek(0)

    wave_file = wave.open(file_object, "rb")
    # instantiate PyAudio

    # open stream
    stream = p.open(format=p.get_format_from_width(wave_file.getsampwidth()),
                    channels=wave_file.getnchannels(),
                    rate=wave_file.getframerate(),
                    output=True)
    # read data
    data = wave_file.readframes(AUDIO_CHUNK)

    # play stream
    while data:
        stream.write(data)
        data = wave_file.readframes(AUDIO_CHUNK)

    stream.stop_stream()
    stream.close()

    return "OK"


# @skt.default_exception_handler()
# def error_handler(e):
#     print('An error has occurred: ' + str(e))


# @skt.on_error()
# def test(test22):
#     print('test')
#
# skt.default_exception_handler = test
#

@skt.on('audio')
def handle_audio_chunk(data):
    #print("data retrieved")
    #print(str(data))
    return play_audio_chunk(data)


if __name__ == "__main__":
    skt.run(app)


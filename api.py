# -*- coding: utf-8 -*-
import io

from flask import Flask
from flask import request
from flask import render_template
import os
import pyaudio
import wave
import soundfile

app = Flask(__name__, static_folder="js",
            template_folder="templates")

p = pyaudio.PyAudio()


@app.route('/js/<path:path>')
def send_js(path):
    return app.send_static_file(path)


@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


@app.route("/upload.php", methods=['POST', 'GET'])
def upload():
    file_object = io.BytesIO()
    # file_object = open('inMemoryFileObject', 'rwb')
    request.files['audio_data'].save(file_object)
    # file_object.close()
    file_object.seek(0)
    chunk = 4096

    # open a wav format music
    f = wave.open(file_object, "rb")
    # instantiate PyAudio

    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)

        # stop stream
    stream.stop_stream()
    stream.close()

    return "OK"


if __name__ == "__main__":
    app.run()

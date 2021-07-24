var gumStream; // Stream from getUserMedia()
var rec; // Recorder.js object
var input; // MediaStreamAudioSourceNode we'll be recording
var recordingNotStopped; // User pressed record button and keep talking, still not stop button pressed
const trackLengthInMS = 1000; // Length of audio chunk in miliseconds
const maxNumOfSecs = 1000; // Number of mili seconds we support per recording (1 second)

// Shim for AudioContext when it's not available.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");

var socket = io();
socket.connect();

//Event handlers for above 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

//Asynchronous function to stop the recoding in each second and export blob to a wav file
const sleep = time => new Promise(resolve => setTimeout(resolve, time));

const asyncFn = async () => {
    for (let i = 0; i < maxNumOfSecs; i++) {
        if (recordingNotStopped) {
            rec.record();
            await sleep(trackLengthInMS);
            rec.stop();

            //stop microphone access
            //gumStream.getAudioTracks()[0].stop();

            //Create the wav blob and pass it on to createWaveBlob
            rec.exportWAV(createWaveBlob);
            rec.step();
        }
    }
}

function startRecording() {
    console.log("recordButton clicked");
    recordingNotStopped = true;
    var constraints = {
        audio: true,
        video: false
    }

    recordButton.disabled = true;
    stopButton.disabled = false;

    //Using the standard promise based getUserMedia()
    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {

        //Create an audio context after getUserMedia is called
        audioContext = new AudioContext();

        // Assign to gumStream for later use
        gumStream = stream;

        //Use the stream
        input = audioContext.createMediaStreamSource(stream);

        //Create the Recorder object and configure to record mono sound (1 channel)
        Recorder.prototype.step = function () {
            this.clear();
        };

        rec = new Recorder(input, {
            numChannels: 1
        });

        //Call the asynchronous function to split and export audio
        asyncFn();
        console.log("Recording started");

    }).catch(function (err) {
        //Enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
    });
}

function stopRecording() {
    console.log("stopButton clicked");
    recordingNotStopped = false;

    //disable the stop button and enable the record button to  allow for new recordings
    stopButton.disabled = true;
    recordButton.disabled = false;

    //Set the recorder to stop the recording
    rec.stop();

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();
    socket.disconnect();
}

async function createWaveBlob(blob) {
    // let tempBuffer = await new Response(blob).arrayBuffer();
    // var bufView = new Uint8Array(tempBuffer);
    // // var b64encoded = btoa(String.fromCharCode.apply(null, bufView));
    // var array = [].slice.call(bufView)
    // ILK 19 KARAKTERI KALDIR BINARY OLARAK GORSUN SONRA BUNU PYTHON TARAFINDA BIRLESTIR
    var newBlob = blob.slice(19, blob.size)
    socket.emit('audio', newBlob);
    //socket.emit('message', array)
}
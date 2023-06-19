from flask import Flask, render_template, request,jsonify, redirect, url_for
from wtforms import Form, TextAreaField, FileField, SelectField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_socketio import SocketIO, emit
from scipy.io import wavfile
import numpy as np
import os, re, json, sys, queue, threading, uuid, logging
import torch, torchaudio, pathlib
from audiocraft.models import MusicGen
from operator import itemgetter
import librosa
import soundfile as sf
from audio import predict
from audiocraft.data.audio import audio_write

app = Flask(__name__)
unload = False
socketio = SocketIO(app, cors_allowed_origins="*")
pending_queue = queue.Queue()

logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)

def worker_process_queue():
    while True:
        form, files = pending_queue.get()  # Get the files from the queue
        output = handle_submit(form, files)
        socketio.emit('new_file', {'output_filename': os.path.basename(output)})
        pending_queue.task_done()

if len(sys.argv) > 1:
    if sys.argv[1] == "--unload-after-gen":
        unload = True
        
def sanitize_filename(filename):
    """
    Takes a filename and returns a sanitized version safe for filesystem operations.
    """
    return re.sub(r'[^\w\d-]', ' ', filename)


def save_output(output, sample_rate, text):
    """
    Save output to a WAV file with the filename based on the input text.
    If a file with the same name already exists, append a number in parentheses.
    """
    i = 1
    base_filename = f"static/audio/{sanitize_filename(text)}"
    output_filename = f"{base_filename}.wav"
    
    # Convert to absolute path
    absolute_path = os.path.abspath(output_filename)
    
    # Check if the absolute path is too long
    max_length = 255  # Maximum path length for most file systems
    if len(absolute_path) > max_length:
        # If the path is too long, truncate the filename
        base_filename = base_filename[:max_length - len(os.path.abspath(f"static/audio/")) - 10]  # Reserve space for extension and potential index
        output_filename = f"{base_filename}.wav"
    
    while os.path.exists(output_filename):
        output_filename = f"{base_filename}({i}).wav"
        i += 1
        
    audio_write(
        output_filename, output.squeeze(), sample_rate, strategy="loudness",
        loudness_headroom_db=16, loudness_compressor=True, add_suffix=False)
    return output_filename
        
def handle_submit(form, files):
    model = form.model.data
    prompt = form.text.data
    model_parameters = {
        "duration": form.duration.data,
        "top_k": form.topk.data,
        "top_p": form.topp.data,
        "temperature": form.temperature.data,
        "cfg_coef": form.cfg_coef.data,
    }
    melody_parameters = {
        "melody": None,
        "sample_rate": None,
    }
    extension_parameters = {
        "segments": form.segments.data,
        "overlap": form.overlap.data
    }
    
    extra_settings_parameters = {
        "unload": unload,
    }

    if files and 'melody' in files and files['melody'] != '':
        temp_filename = files['melody']
        if form.model.data != 'melody':
            pass
        else:
            melody_parameters['melody'], melody_parameters['sample_rate'] = librosa.load(temp_filename, sr=None)
            print(f"Using melody file: {temp_filename}")
            os.remove(temp_filename)  # Delete the temporary file

    for name, value in {**model_parameters, **extension_parameters}.items():
        print(f"{name}: {value}")

    sample_rate, output_tensors = predict(socketio, model, prompt, model_parameters, melody_parameters, extension_parameters, extra_settings_parameters)
    if output_tensors is None:
        return None
    output_filename = save_output(output_tensors, sample_rate, prompt)

    return output_filename

class MusicForm(Form):
    text = TextAreaField('Input Text', [DataRequired()])
    melody = FileField('Optional Melody')
    model = SelectField('Model', choices=[('melody', 'melody'), ('medium', 'medium'), ('small', 'small'), ('large', 'large')], default='large')
    duration = IntegerField('Duration', default=10, validators=[NumberRange(min=1, max=1000)])
    topk = IntegerField('Top-k', default=0)
    topp = FloatField('Top-p', default=0)
    temperature = FloatField('Temperature', default=1.0)
    cfg_coef = FloatField('Classifier Free Guidance', default=4.5)
    segments = IntegerField('Segments', default=1, validators=[NumberRange(min=1, max=10)])
    overlap = FloatField('Overlap', default=5.0) 
    submit = SubmitField('Submit')

@app.route('/api/audio-files', methods=['GET'])
def get_audio_files():
    audio_files = [(f, f, os.path.getmtime(f'static/audio/{f}')) for f in os.listdir('static/audio')]
    audio_files_dicts = [{'text': text, 'audio_file': audio_file, 'timestamp': timestamp} for text, audio_file, timestamp in audio_files]
    return jsonify(audio_files_dicts)

@app.route('/', methods=['GET', 'POST'])
def home_and_submit():
    form = MusicForm(request.form)
    output_filename = None  # Initialize output_filename here

    if request.method == 'POST' and form.validate():
        files = None
        if 'melody' in request.files and request.files['melody'].filename != '':
            melody_file = request.files['melody']
            extension = os.path.splitext(melody_file.filename)[1]
            temp_filename = f"/tmp/{uuid.uuid4()}{extension}"
            melody_file.save(temp_filename)
            files = {'melody': temp_filename}
        pending_queue.put((form, files))
        return redirect(url_for('home_and_submit'))
        
    audio_dir = pathlib.Path('static/audio')
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_files_dicts = [
        {'text': audio_file.name, 'audio_file': audio_file.name, 'timestamp': audio_file.stat().st_mtime}
        for audio_file in audio_dir.glob('*')
    ]
    
    if request.method == 'GET':
        return render_template('form.html', form=form, audio_files=audio_files_dicts)

if __name__ == '__main__':
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    threading.Thread(target=worker_process_queue, daemon=True).start()
    socketio.run(app)
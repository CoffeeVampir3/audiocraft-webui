from flask import Flask, render_template, request,jsonify, redirect, url_for
from wtforms import Form, TextAreaField, FileField, SelectField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_socketio import SocketIO, emit
from scipy.io import wavfile
import numpy as np
import os, re, json, sys, queue, threading, uuid
import torch, torchaudio, pathlib
from audiocraft.models import MusicGen
from operator import itemgetter
import librosa
import soundfile as sf
from audio import predict
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
unload = False
bootstrap = Bootstrap5(app)
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'slate'
socketio = SocketIO(app, cors_allowed_origins="*")
pending_queue = queue.Queue()

def worker_process_queue():
    while True:
        form, files = pending_queue.get()  # Get the files from the queue
        output = handle_submit(form, files)
        socketio.emit('new_file', {'output_filename': os.path.basename(output), 'timestamp': os.path.getmtime(output)})
        pending_queue.task_done()

if len(sys.argv) > 1:
    if sys.argv[1] == "--unload-after-gen":
        unload = True
        
def sanitize_filename(filename):
    """
    Takes a filename and returns a sanitized version safe for filesystem operations.
    """
    return re.sub(r'[^\w\d-]', ' ', filename)

def save_output(output, text):
    """
    Save output to a WAV file with the filename based on the input text.
    If a file with the same name already exists, append a number in parentheses.
    """
    i = 1
    base_filename = f"static/audio/{sanitize_filename(text)}.wav"
    output_filename = base_filename
    while os.path.exists(output_filename):
        output_filename = f"{base_filename.rsplit('.', 1)[0]}({i}).wav"
        i += 1

    wavfile.write(output_filename, output[0], np.array(output[1], dtype=np.float32))
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
        "id": form.id.data
    }

    if files and 'melody' in files and files['melody']:
        if form.model.data != 'melody':
            pass
        else:
            extension = os.path.splitext(files['melody'])[1]
            if extension.lower() in ['.wav', '.mp3']:
                melody_parameters['melody'], melody_parameters['sample_rate'] = librosa.load(files['melody'], sr=None)
                print(f"Using melody file: {files['melody']}")
            else:
                print(f"Unsupported file extension: {extension}")

    for name, value in {**model_parameters, **extension_parameters}.items():
        print(f"{name}: {value}")

    output = predict(socketio, model, prompt, model_parameters, melody_parameters, extension_parameters, extra_settings_parameters)
    if output is None:
        return None
    output_filename = save_output(output, prompt)

    return output_filename

class MusicForm(Form):
    text = TextAreaField('Input Text', [DataRequired()])
    id = TextAreaField('Job Id', [DataRequired()])
    melody = FileField('Optional Melody')
    model = SelectField('Model', choices=[('melody', 'melody'), ('medium', 'medium'), ('small', 'small'), ('large', 'large')], default='large')
    duration = IntegerField('Duration', default=10, validators=[NumberRange(min=1, max=30)])
    topk = IntegerField('Top-k', default=250)
    topp = FloatField('Top-p', default=0)
    temperature = FloatField('Temperature', default=1.0)
    cfg_coef = FloatField('Classifier Free Guidance', default=7.0)
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
    socketio.run(app, use_reloader = True, debug = True)

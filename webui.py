from flask import Flask, render_template, request,jsonify
from wtforms import Form, TextAreaField, FileField, SelectField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from scipy.io import wavfile
import numpy as np
import os
import torch
from audiocraft.models import MusicGen
import re
from operator import itemgetter
import json
import librosa
import soundfile as sf

MODEL = None

def load_model(version):
    print("Loading model", version)
    return MusicGen.get_pretrained(version)

def load_and_process_audio(melody_data, sr, model):
    if melody_data is not None:
        melody = torch.from_numpy(melody_data).to(model.device).float().t().unsqueeze(0)
        if melody.dim() == 2:
            melody = melody[None]
        melody = melody[..., :int(sr * model.lm.cfg.dataset.segment_duration)]
        return melody
    else:
        return None
    

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


def predict(model, text, melody, sr, duration, topk, topp, temperature, cfg_coef):
    global MODEL
    topk = int(topk)
    if MODEL is None or MODEL.name != model:
        if MODEL is not None:
            del MODEL
            torch.cuda.empty_cache()
        MODEL = load_model(model)
        print(MODEL)
        return predict(model, text, melody, sr, duration, topk, topp, temperature, cfg_coef)

    #if duration > MODEL.lm.cfg.dataset.segment_duration:
    #    raise gr.Error("MusicGen currently supports durations of up to 30 seconds!")
    MODEL.set_generation_params(
        use_sampling=True,
        top_k=topk,
        top_p=topp,
        temperature=temperature,
        cfg_coef=cfg_coef,
        duration=duration,
    )
    
    melody = load_and_process_audio(melody, sr, MODEL)

    if melody is not None:
        output = MODEL.generate_with_chroma(
            descriptions=[text],
            melody_wavs=melody,
            melody_sample_rate=sr,
            progress=False
        )
    else:
        output = MODEL.generate(descriptions=[text], progress=False)

    output = output.detach().cpu().numpy()
    return MODEL.sample_rate, output

class MusicForm(Form):
    text = TextAreaField('Input Text', [DataRequired()])
    melody = FileField('Optional Melody')
    model = SelectField('Model', choices=[('melody', 'melody'), ('medium', 'medium'), ('small', 'small'), ('large', 'large')], default='large')
    duration = IntegerField('Duration', default=10, validators=[NumberRange(min=1, max=30)])
    topk = IntegerField('Top-k', default=250)
    topp = FloatField('Top-p', default=0)
    temperature = FloatField('Temperature', default=3.0)
    cfg_coef = FloatField('Classifier Free Guidance', default=3.0)
    submit = SubmitField('Submit')

app = Flask(__name__)

@app.route('/api/audio-files', methods=['GET'])
def get_audio_files():
    audio_files = [(f, f, os.path.getmtime(f'static/audio/{f}')) for f in os.listdir('static/audio')]
    audio_files_dicts = [{'text': text, 'audio_file': audio_file, 'timestamp': timestamp} for text, audio_file, timestamp in audio_files]
    return jsonify(audio_files_dicts)

@app.route('/', methods=['GET', 'POST'])
def home_and_submit():
    form = MusicForm(request.form)

    if request.method == 'POST' and form.validate():
        model = form.model.data
        text = form.text.data
        duration = form.duration.data
        topk = form.topk.data
        topp = form.topp.data
        temperature = form.temperature.data
        cfg_coef = form.cfg_coef.data

        melody = None
        sr = None
        if 'melody' in request.files and request.files['melody'].filename != '':
            if form.model.data != 'melody':
                pass
            else:
                melody_file = request.files['melody']
                extension = os.path.splitext(melody_file.filename)[1]
                if extension.lower() in ['.wav', '.mp3']:
                    melody, sr = librosa.load(melody_file, sr=None)
                else:
                    print(f"Unsupported file extension: {extension}")

        output = predict(model, text, melody, sr, duration, topk, topp, temperature, cfg_coef)
        output_filename = save_output(output, form.text.data)
        
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')

    audio_files = [(f, f, os.path.getmtime(f'static/audio/{f}')) for f in os.listdir('static/audio')]
    audio_files_dicts = [{'text': text, 'audio_file': audio_file, 'timestamp': timestamp} for text, audio_file, timestamp in audio_files]
    
    if request.method == 'POST':
        return jsonify({'audio_files': audio_files_dicts})
    else:
        return render_template('form.html', form=form, audio_files=audio_files_dicts)

if __name__ == '__main__':
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    app.run()
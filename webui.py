from flask import Flask, render_template, request, send_file
from wtforms import Form, StringField, FileField, RadioField, IntegerField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from scipy.io import wavfile
import numpy as np
import io
import torch
from audiocraft.models import MusicGen
import json

MODEL = None

def load_model(version):
    print("Loading model", version)
    return MusicGen.get_pretrained(version)

def load_and_process_audio(melody, model):
    if melody is not None:
        try:
            sr, melody = melody[0], torch.from_numpy(melody[1]).to(model.device).float().t().unsqueeze(0)
        except json.JSONDecodeError:
            sr, melody = wavfile.read(melody)
            melody = torch.from_numpy(melody).to(model.device).float().t().unsqueeze(0)

        print(melody.shape)
        if melody.dim() == 2:
            melody = melody[None]
        melody = melody[..., :int(sr * model.lm.cfg.dataset.segment_duration)]
        return melody, sr
    else:
        return None, None

def predict(model, text, melody, duration, topk, topp, temperature, cfg_coef):
    global MODEL
    topk = int(topk)
    if MODEL is None or MODEL.name != model:
        MODEL = load_model(model)
        return predict(model, text, melody, duration, topk, topp, temperature, cfg_coef)

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
    
    melody, sr = load_and_process_audio(melody, MODEL)
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
    text = StringField('Input Text', [DataRequired()])
    melody = FileField('Melody Condition (optional)')
    model = SelectField('Model', choices=[('melody', 'melody'), ('medium', 'medium'), ('small', 'small'), ('large', 'large')], default='large')
    duration = IntegerField('Duration', default=10, validators=[NumberRange(min=1, max=30)])
    topk = IntegerField('Top-k', default=250)
    topp = FloatField('Top-p', default=0)
    temperature = FloatField('Temperature', default=1.0)
    cfg_coef = FloatField('Classifier Free Guidance', default=3.0)
    submit = SubmitField('Submit')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    form = MusicForm(request.form)
    if request.method == 'POST' and form.validate():
        # Use the form data to call the predict function
        model = form.model.data
        text = form.text.data
        duration = form.duration.data
        topk = form.topk.data
        topp = form.topp.data
        temperature = form.temperature.data
        cfg_coef = form.cfg_coef.data

        # Load and process the audio file if one was uploaded
        melody = None
        if 'melody' in request.files and request.files['melody'].filename != '':
            melody_file = request.files['melody']
            melody = wavfile.read(melody_file)

        # Call the predict function
        output = predict(model, text, melody, duration, topk, topp, temperature, cfg_coef)

        # Convert the output to a WAV file and send it
        output_wav = io.BytesIO()
        wavfile.write(output_wav, output[0], np.array(output[1], dtype=np.float32))
        output_wav.seek(0)
        return send_file(output_wav, mimetype='audio/wav')

    return render_template('form.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
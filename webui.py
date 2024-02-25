from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request, jsonify, send_from_directory
import logging, os, queue, threading, json
import torchaudio
from mechanisms.generator_backend import generate_audio

app = Flask(__name__)
pending_queue = queue.Queue()
socketio = SocketIO(app, cors_allowed_origins="*")
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)

def worker_process_queue():
    while True:
        model_type, prompt, slider_data, melody_data = pending_queue.get()
        filename, json_filename = generate_audio(socketio, model_type, prompt, slider_data, melody_data)
        socketio.emit('on_finish_audio', {"prompt":prompt, "filename":filename, "json_filename":json_filename})
        pending_queue.task_done()
        
def save_last_gen_settings(model_type, prompt, audio_gen_params):
    os.makedirs("settings", exist_ok=True)
    output_filename = "settings/last_run.json"
    write_data = {"model":model_type, "prompt":prompt, "parameters":audio_gen_params}
    
    with open(output_filename, 'w') as outfile:
        json.dump(write_data, outfile, indent=4)
        
def load_last_gen_settings():
    input_filename = "settings/last_run.json"
    if not os.path.exists(input_filename):
        return None, None, None
    
    with open(input_filename, 'r') as infile:
        settings = json.load(infile)
        model = settings["model"]
        prompt = settings["prompt"]
        topp = settings["parameters"]["top_p"]
        duration = settings["parameters"]["duration"]
        cfg_coef = settings["parameters"]["cfg_coef"]
        topk = settings["parameters"]["top_k"]
        temperature = settings["parameters"]["temperature"]
        return model, prompt, topp, duration, cfg_coef, topk, temperature
    
    
@socketio.on('submit_sliders')
def handle_submit_sliders(json):
    slider_data = json['values']
    prompt = json['prompt']
    model_type = json['model']
    if not prompt:
        return
    
    slider_data = {key: float(value) for key, value in slider_data.items()}
    
    melody_data = None
    
    melody_url = json.get('melodyUrl', None)
    if melody_url:
        melody_data = torchaudio.load(melody_url)

    save_last_gen_settings(model_type, prompt, slider_data)
    socketio.emit('add_to_queue', {"prompt":prompt})
    pending_queue.put((model_type, prompt, slider_data, melody_data))
    
@socketio.on('connect')
def handle_connect():
    audio_json_pairs = get_audio_json_pairs("static/audio")
    # Send the list of pairs to the connected client
    socketio.emit('audio_json_pairs', audio_json_pairs)
    
def get_audio_json_pairs(directory):
    files = os.listdir(directory)
    wav_files = [f for f in files if f.endswith('.wav')]
    json_files = [f for f in files if f.endswith('.json')]
    
    pairs = []
    for wav_file in wav_files:
        base_name = os.path.splitext(wav_file)[0]
        json_file = f"{base_name}.json"
        if json_file in json_files:
            full_wav_path = os.path.join(directory, wav_file)
            full_json_path = os.path.join(directory, json_file)
            pairs.append((full_wav_path, full_json_path))
            
    for pair in pairs:
        print(pair)
    
    return pairs
    
@app.route('/upload_melody', methods=['POST'])
def upload_audio():
    dir = "static/temp"
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
            
    if 'melody' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['melody']
    if not file or file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file.content_type.startswith('audio/'):
        filename = file.filename
        file_path = os.path.join(dir, filename)
        file.save(file_path)
        return jsonify({'filePath': file_path}), 200

@app.route('/')
def index():
    model, prompt, topk, duration, cfg_coef, topp, temperature = load_last_gen_settings()
    if model is not None:
        return render_template('index.html', 
                               topk=topk, 
                               duration=duration, 
                               cfg_coef=cfg_coef, 
                               topp=topp, 
                               temperature=temperature, 
                               default_model=model,
                               default_text=prompt)
    topk = 250
    duration = 30
    cfg_coef = 4.0
    topp = .67
    temperature = 1.2
    default_model = "large"
    default_text = ""
    return render_template('index.html', 
                           topk=topk, 
                           duration=duration, 
                           cfg_coef=cfg_coef, 
                           topp=topp, 
                           temperature=temperature, 
                           default_model=default_model,
                           default_text=default_text)

if __name__ == '__main__':
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    if not os.path.exists('static/temp'):
        os.makedirs('static/temp')
    threading.Thread(target=worker_process_queue, daemon=True).start()
    socketio.run(app)
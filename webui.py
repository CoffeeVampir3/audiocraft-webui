from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request, jsonify
import logging, os, queue, threading
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

    socketio.emit('add_to_queue', {"prompt":prompt})
    pending_queue.put((model_type, prompt, slider_data, melody_data))
    
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
    topk = 250
    duration = 30
    cfg_coef = 4.0
    topp = .67
    temperature = 1.2
    overlap = 3
    return render_template('index.html', topk=topk, duration=duration, cfg_coef=cfg_coef, topp=topp, temperature=temperature, overlap=overlap)

if __name__ == '__main__':
    if not os.path.exists('static/audio'):
        os.makedirs('static/audio')
    if not os.path.exists('static/temp'):
        os.makedirs('static/temp')
    threading.Thread(target=worker_process_queue, daemon=True).start()
    socketio.run(app, debug=True)
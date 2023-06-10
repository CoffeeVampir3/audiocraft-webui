import gradio as gr
import torchaudio
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

def generate_music(description: str):
    model = MusicGen.get_pretrained('large')
    model.set_generation_params(duration=8)
    wav = model.generate([description])
    audio_path = 'output.wav'
    audio_write(audio_path, wav[0].cpu(), model.sample_rate, strategy="loudness")
    return audio_path

iface = gr.Interface(
    fn=generate_music,
    inputs="text",
    outputs=gr.outputs.Audio(type="file", label="Generated Music"),
    title="Music Generator",
    description="Enter a description to generate a unique piece of music!",
)

iface.launch()
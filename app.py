import gradio as gr
import os, json
from generator import HijackedMusicGen
from audiocraft.data.audio import audio_write
from audio import predict
from itertools import zip_longest

def split_prompt(bigly_prompt, num_segments):
    prompts = bigly_prompt.split(',,')
    num_segments = int(num_segments)  # Assuming 'segment' comes as a string from Gradio slider
    # repeat last prompt to fill in the rest
    if len(prompts) < num_segments:
        prompts += [prompts[-1]] * (num_segments - len(prompts))
    elif len(prompts) > num_segments:
        prompts = prompts[:num_segments]
    return prompts

loaded_model = None
audio_files = []
def model_interface(model_name, top_k, top_p, temperature, cfg_coef, segments, overlap, duration, optional_audio, prompt):
    global loaded_model

    if loaded_model is None or loaded_model.name != model_name:
        loaded_model = HijackedMusicGen.get_pretrained(None, name=model_name)
        
    print(optional_audio)
        
    loaded_model.set_generation_params(
        use_sampling=True,
        duration=duration,
        top_p=top_p,
        top_k=top_k,
        temperature=temperature,
        cfg_coef=cfg_coef,
    )
    
    extension_parameters = {"segments":segments, "overlap":overlap}
    optional_audio_parameters = {"optional_audio":optional_audio, "sample_rate":loaded_model.sample_rate}
    
    prompts = split_prompt(prompt, segments)
    first_prompt = prompts[0]

    sample_rate, audio = predict(loaded_model, prompts, duration, optional_audio_parameters, extension_parameters)
    
    counter = 1
    audio_path = "static/"
    audio_name = first_prompt
    while os.path.exists(audio_path + audio_name + ".wav"):
        audio_name = f"{first_prompt}({counter})"
        counter += 1
        
    file = audio_write(audio_path + audio_name, audio.squeeze(), sample_rate, strategy="loudness")
    audio_files.append(file)

    audio_list_html = "<br>".join([
        f'''
        <div style="border:1px solid #000; padding:10px; margin-bottom:10px;">
            <div>{os.path.splitext(os.path.basename(file))[0]}</div>
            <audio controls><source src="/file={file}" type="audio/wav"></audio>
        </div>
        ''' 
        for file in reversed(audio_files)
    ])

    return audio_list_html

slider_param = {
    "top_k": {"minimum": 0, "maximum": 1000, "value": 0, "label": "Top K"},
    "top_p": {"minimum": 0.0, "maximum": 1.0, "value": 0.0, "label": "Top P"},
    "temperature": {"minimum": 0.1, "maximum": 10.0, "value": 1.0, "label": "Temperature"},
    "cfg_coef": {"minimum": 0.0, "maximum": 10.0, "value": 4.0, "label": "CFG Coefficient"},
    "segments": {"minimum": 1, "maximum": 10, "value": 1, "step": 1, "label": "Number of Segments"},
    "overlap": {"minimum": 0.0, "maximum": 10.0, "value": 1.0, "label": "Segment Overlap"},
    "duration": {"minimum": 1, "maximum": 300, "value": 10, "label": "Duration"},
}

slider_params = {
    key: gr.components.Slider(**params) 
    for key, params in slider_param.items()
}

with gr.Blocks() as interface:
    with gr.Row():

        with gr.Column():
            with gr.Row():
                model_dropdown = gr.components.Dropdown(choices=["small", "medium", "large", "melody"], label="Model Size", value="large")
                optional_audio = gr.components.Audio(source="upload", type="numpy", label="Optional Audio", interactive=True)

            slider_keys = list(slider_param.keys())
            slider_pairs = list(zip_longest(slider_keys[::2], slider_keys[1::2]))

            for key1, key2 in slider_pairs:
                with gr.Row():
                    with gr.Column():
                        slider_params[key1] = gr.components.Slider(**slider_param[key1])
                    if key2 is not None:
                        with gr.Column():
                            slider_params[key2] = gr.components.Slider(**slider_param[key2])

            prompt_box = gr.components.Textbox(lines=5, placeholder="""Insert a double comma ,, to indicate this should prompt a new segment. For example: 
    Rock Opera,,Dueling Banjos
    This allows you to prompt each segment individually. If you only provide one prompt, every segment will use that one prompt. If you provide multiple prompts but less than the number of segments, then the last prompt will be used to fill in the rest.
    """)
            submit = gr.Button("Submit")

        with gr.Column():
            output = gr.outputs.HTML()

    inputs_list = [model_dropdown] + list(slider_params.values()) + [optional_audio] + [prompt_box]
    submit.click(model_interface, inputs=inputs_list, outputs=[output])
    
interface.queue()
interface.launch(enable_queue=True)
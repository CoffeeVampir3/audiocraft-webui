import numpy as np
import os, re, json, sys
import torch, torchaudio, pathlib
from operator import itemgetter
from generator import HijackedMusicGen

global MODEL
MODEL = None

def load_model(version, socketio):
    print("Loading model", version)
    model = None
    try:
        model = HijackedMusicGen.get_pretrained(socketio, version)
    except Exception as e:
        print(f"Failed to load model due to error: {e}, you probably need to pick a smaller model.")
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        return None
    return model

def load_and_process_audio(model, melody, sample_rate):
    if melody is not None:
        return melody[None]
    else:
        return None

#From https://colab.research.google.com/drive/154CqogsdP-D_TfSF9S2z8-BY98GN_na4?usp=sharing#scrollTo=exKxNU_Z4i5I
#Thank you DragonForged for the link
def extend_audio(model, prompt_waveform, prompt, prompt_sr, segments=5, overlap=2):
    # Calculate the number of samples corresponding to the overlap
    overlap_samples = int(overlap * prompt_sr)

    device = model.device
    prompt_waveform = prompt_waveform.to(device)

    for _ in range(segments):
        # Grab the end of the waveform
        end_waveform = prompt_waveform[...,-overlap_samples:]

        # Process the trimmed waveform using the model
        new_audio = model.generate_continuation(end_waveform, descriptions=[prompt], prompt_sample_rate=prompt_sr, progress=True)
            
        # Cut the seed audio off the newly generated audio
        new_audio = new_audio[...,overlap_samples:]

        prompt_waveform = torch.cat([prompt_waveform, new_audio], dim=2)

    return prompt_waveform

def predict(socketio, model, prompt, model_parameters, melody_parameters, extension_parameters, extra_settings_parameters):
    global MODEL
    if not MODEL or MODEL.name != f"facebook/musicgen-{model}":
        if MODEL:
            del output
            import gc
            del MODEL
            MODEL = None
            gc.collect() 
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        MODEL = load_model(model, socketio)
        if MODEL is None:
            return None

    MODEL.set_generation_params(
        use_sampling=True,
        **model_parameters,
    )
    
    melody = load_and_process_audio(MODEL, **melody_parameters)

    if melody is not None:
        output = MODEL.generate_with_chroma(
            descriptions=[prompt],
            melody_wavs=melody,
            melody_sample_rate=melody_parameters['sample_rate'],
            progress=True
        )
    else:
        output = MODEL.generate(descriptions=[prompt], progress=True)

    sample_rate = MODEL.sample_rate
    
    if extension_parameters['segments'] > 1:
        output_tensors = extend_audio(MODEL, output, prompt, sample_rate, **extension_parameters).detach().cpu().float()
    else:
        output_tensors = output.detach().cpu().float()
        
    print(output_tensors)
    
    if extra_settings_parameters['unload']:
        del output
        import gc
        del MODEL
        MODEL = None
        gc.collect() 
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    
    return sample_rate, output_tensors
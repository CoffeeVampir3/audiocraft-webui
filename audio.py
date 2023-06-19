import numpy as np
import os, re, json, sys
import torch, torchaudio, pathlib
from audiocraft.data.audio_utils import convert_audio

def load_and_process_audio(model, duration, optional_audio, sample_rate):
    if optional_audio is None:
        return None
    sr, optional_audio = optional_audio[0], torch.from_numpy(optional_audio[1]).to(model.device).float().t()
    if optional_audio.dim() == 1:
        optional_audio = optional_audio[None]
    optional_audio = optional_audio[..., :int(sr * duration)]
    optional_audio = convert_audio(optional_audio, sr, sr, 1)
    return optional_audio

#From https://colab.research.google.com/drive/154CqogsdP-D_TfSF9S2z8-BY98GN_na4?usp=sharing#scrollTo=exKxNU_Z4i5I
#Thank you DragonForged for the link
def extend_audio(model, prompt_waveform, prompts, prompt_sr, segments=5, overlap=2):
    # Calculate the number of samples corresponding to the overlap
    overlap_samples = int(overlap * prompt_sr)

    device = model.device
    prompt_waveform = prompt_waveform.to(device)

    for i in range(1, segments):
        # Grab the end of the waveform
        end_waveform = prompt_waveform[...,-overlap_samples:]

        # Process the trimmed waveform using the model
        new_audio = model.generate_continuation(end_waveform, descriptions=[prompts[i]], prompt_sample_rate=prompt_sr, progress=True)
            
        # Cut the seed audio off the newly generated audio
        new_audio = new_audio[...,overlap_samples:]

        prompt_waveform = torch.cat([prompt_waveform, new_audio], dim=2)

    return prompt_waveform

def predict(model, prompts, duration, melody_parameters, extension_parameters):
    melody = load_and_process_audio(model, duration, **melody_parameters)

    if melody is not None:
        output = model.generate_with_chroma(
            descriptions=[prompts[0]],
            melody_wavs=melody,
            melody_sample_rate=melody_parameters['sample_rate'],
            progress=False
        )
    else:
        output = model.generate(descriptions=[prompts[0]], progress=True)

    sample_rate = model.sample_rate
    
    if extension_parameters['segments'] > 1:
        output_tensors = extend_audio(model, output, prompts, sample_rate, **extension_parameters).detach().cpu().float()
    else:
        output_tensors = output.detach().cpu().float()
    
    return sample_rate, output_tensors
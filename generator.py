import torch
import time
import typing as tp
from audiocraft.models import MusicGen
from audiocraft.modules.conditioners import ConditioningAttributes

class HijackedMusicGen(MusicGen):
    def __init__(self, socketio=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socketio = socketio
        self._progress_callback = self._timed_progress_callback if socketio is not None else None
        self._last_update_time = time.time()
        
    def _timed_progress_callback(self, generated_tokens: int, tokens_to_generate: int):
        current_time = time.time()
        if current_time - self._last_update_time >= 0.1:  # 0.1 seconds have passed
            self.socketio.emit('progress', {'generated_tokens': generated_tokens, 'tokens_to_generate': tokens_to_generate})
            self._last_update_time = current_time
        
    @staticmethod
    def get_pretrained(socketio, name: str = 'melody', device='cuda'):
        music_gen = MusicGen.get_pretrained(name, device)
        return HijackedMusicGen(socketio, music_gen.name, music_gen.compression_model, music_gen.lm)
    
    @property
    def progress_callback(self):
        raise Exception("Progress callback is write-only")

    @progress_callback.setter
    def progress_callback(self, callback):
        self._progress_callback = callback
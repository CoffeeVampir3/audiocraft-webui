import torch
import typing as tp
import os
from audiocraft.models import MusicGen
from audiocraft.modules.conditioners import ConditioningAttributes
from audiocraft.models.encodec import CompressionModel
from audiocraft.models.lm import LMModel
from audiocraft.models.builders import get_debug_compression_model, get_debug_lm_model
from audiocraft.models.loaders import load_compression_model, load_lm_model, HF_MODEL_CHECKPOINTS_MAP


class HijackedMusicGen(MusicGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._progress_callback = None  # direct assignment here
        
    @staticmethod
    def get_pretrained(name: str = 'melody', device='cuda'):
        """Return pretrained model, we provide four models:
        - small (300M), text to music, # see: https://huggingface.co/facebook/musicgen-small
        - medium (1.5B), text to music, # see: https://huggingface.co/facebook/musicgen-medium
        - melody (1.5B) text to music and text+melody to music, # see: https://huggingface.co/facebook/musicgen-melody
        - large (3.3B), text to music, # see: https://huggingface.co/facebook/musicgen-large
        """

        if name == 'debug':
            # used only for unit tests
            compression_model = get_debug_compression_model(device)
            lm = get_debug_lm_model(device)
            return MusicGen(name, compression_model, lm)

        if name not in HF_MODEL_CHECKPOINTS_MAP:
            raise ValueError(
                f"{name} is not a valid checkpoint name. "
                f"Choose one of {', '.join(HF_MODEL_CHECKPOINTS_MAP.keys())}"
            )

        cache_dir = os.environ.get('MUSICGEN_ROOT', None)
        compression_model = load_compression_model(name, device=device, cache_dir=cache_dir)
        lm = load_lm_model(name, device=device, cache_dir=cache_dir)

        return HijackedMusicGen(name, compression_model, lm)

    def _generate_tokens(self, attributes: tp.List[ConditioningAttributes],
                         prompt_tokens: tp.Optional[torch.Tensor], progress: bool = False) -> torch.Tensor:

        if prompt_tokens is not None:
            assert self.generation_params['max_gen_len'] > prompt_tokens.shape[-1], \
                "Prompt is longer than audio to generate"

        # generate by sampling from LM
        with self.autocast:
            gen_tokens = self.lm.generate(prompt_tokens, attributes, callback=self._progress_callback, **self.generation_params)

        # generate audio
        assert gen_tokens.dim() == 3
        with torch.no_grad():
            gen_audio = self.compression_model.decode(gen_tokens, None)
        return gen_audio

    @property
    def progress_callback(self):
        raise Exception("Progress callback is write-only")

    @progress_callback.setter
    def progress_callback(self, callback):
        self._progress_callback = callback
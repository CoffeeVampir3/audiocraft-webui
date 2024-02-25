[![Discord](https://img.shields.io/discord/232596713892872193?logo=discord)](https://discord.gg/2JhHVh7CGu)

# audiocraft-webui
Local webui for Facebook's Audiocraft model: <https://github.com/facebookresearch/audiocraft>

![](https://github.com/CoffeeVampir3/audiocraft-webui/blob/1a1390e2842a7eaa8de376503abb51fbfad233ca/preview.png)

## Features:

- **Long Audio**: Make audio as long as you like.
- **Segmented audio**: Generate audio in segments (potentially faster than longer audio)
- **Processing Queue**: Add as many different prompts to the processing queue as you like, go have a cup of coffee, come back to sweet sweet audio.

- **Segmented Prompting**: *On the gradio version <https://github.com/CoffeeVampir3/audiocraft-webui/tree/gradio-version>* Use multiple different prompts per audio segment.

## Install:

If you'd like gpu acceleration and do not have torch installed, visit https://pytorch.org/get-started/locally/ for instructions on installing gpu torch correctly.

`pip install -r requirements.txt`
(If you encounter errors with audiocraft installing, please refer to their docs here: <https://github.com/facebookresearch/audiocraft>)

## Run:
`python webui.py`

There's no need to download any external models, pick a model in the dropdown and when you hit run for the first time it will be automatically downloaded via audiocraft. If you want to use the melody mode, select the Melody model and a selector for your melody audio file will appear.

## Notes:
Files are saved to the `statc/audio/` directory.

The currently active model stays loaded in memory by default, if you want it to be unloaded after each generation, launch with `python webui.py --unload-after-gen`

The UI is in desperate need of an actual UI design if anyone wants to take on the task.

## Parameters:

- **Top-K**: Higher top-k increases the amount of possible instrumentation/continuations will happen. Higher top-k combines with higher temperature to make more interesting music but could make things really odd. I generally tune this in combination with temperature.
- **Top-P**: Recommended around 0.7, this means we are sampling from the top 70% of the possible continuations. Higher top-p will be less interesting and creative, and might also introduce static and noise. Recommendation is to leave this around 0.7 and not think about it much.
- **Duration**: Length of generated music.
- **CFG/Classifier Free Guidance**: The higher this is, the more strongly it will match what you prompted. Generally recommend this between 3-5.
- **Temperature**: How much randomness to introduce, recommended around 1.05-1.5, if you want chaotic music this should be higher, more regular/repition like club beats this should be lower.

## Changelog:

### Feb-25-2024:
- Rewrote everything.
- Added a history of generation parameters for generated music
- Removed a bunch of garbage dependencies
- Removed overlap and segments as they were antiquated parameters.

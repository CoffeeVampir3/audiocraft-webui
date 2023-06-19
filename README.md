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

- **Top-K**: Unclear how it affects generation, needs more testing.
- **Top-P**: Same as above.
- **Duration**: Length of generated music.
- **Classifier Free Guidance**: Controls creativity, lower number = "more creative freedom" in theory at least.
- **Temperature**: Also a sort of creativity guide, your outputs will be terrible if this is too high.
- **Segments**: Number of segments to generate. Each segment will be (duration-overlap) long, so if duration is 30 seconds and overlap is 5 seconds, with 3 segments, you will get 75 seconds of audio out.
- **Overlap**: The overlap for the segment, as explained above. More overlap = more consistent music between segments.

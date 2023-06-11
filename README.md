# audiocraft-webui
Local webui for Facebook's Audiocraft model: <https://github.com/facebookresearch/audiocraft>

![](https://github.com/CoffeeVampir3/audiocraft-webui/blob/289065e48cf08a772b62746133b54ad6b5db0451/image.png)

## Install:
`pip install -r requirements.txt`
(If you encounter errors with audiocraft installing, please refer to their docs here: <https://github.com/facebookresearch/audiocraft>)

## Run:
`python webui.py`

## Notes:
Files are saved to the `statc/audio/` directory.

The currently active model stays loaded in memory by default, if you want it to be unloaded after each generation, launch with `python webui.py --unload-after-gen`

The UI is in desperate need of an actual UI design if anyone wants to take on the task.

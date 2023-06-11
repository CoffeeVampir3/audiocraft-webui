# audiocraft-webui
Local webui for Facebook's Audiocraft model: <https://github.com/facebookresearch/audiocraft>

![](https://github.com/CoffeeVampir3/audiocraft-webui/blob/289065e48cf08a772b62746133b54ad6b5db0451/image.png)

## Features:

More than 30 seconds of audio generation by using segments. It's basically the biggest deal of all time ever.

## Install:
`pip install -r requirements.txt`
(If you encounter errors with audiocraft installing, please refer to their docs here: <https://github.com/facebookresearch/audiocraft>)

## Run:
`python webui.py`

## Notes:
Files are saved to the `statc/audio/` directory.

The currently active model stays loaded in memory by default, if you want it to be unloaded after each generation, launch with `python webui.py --unload-after-gen`

The UI is in desperate need of an actual UI design if anyone wants to take on the task.

## Parameters:

    Top-K: Unclear how it affects generation, needs more testing.
    Top-P: Same as above.
    Duration: Length of generated music.
    Classifier Free Guidance: Controls creativity, lower number = "more creative freedom" in theory at least.
    Temperature: Also a sort of creativity guide, your outputs will be terrible if this is too high.
    Segments: Number of segments to generate. Each segment will be (duration-overlap) long, so if duration is 30 seconds and overlap is 5 seconds, with 3 segments, you will get 75 seconds of audio out.
    Overlap: The overlap for the segment, as explained above. More overlap = more consistent music between segments.

[![Discord](https://img.shields.io/discord/232596713892872193?logo=discord)](https://discord.gg/2JhHVh7CGu)

# audiocraft-webui v2.0!
Local web UI for Facebook's Audiocraft model: <https://github.com/facebookresearch/audiocraft>

![](https://github.com/CoffeeVampir3/audiocraft-webui/blob/1a1390e2842a7eaa8de376503abb51fbfad233ca/preview.png)

## Features:

- **Long Audio**: Generate audio as long as you like.
- **Processing Queue**: Add multiple prompts to the queue and process them automatically.
- **Generation History**: Replay generated audio and view the settings used for each.

## Install:

If you'd like GPU acceleration and do not have torch installed, visit [PyTorch Installation Guide](https://pytorch.org/get-started/locally/) for instructions on installing GPU-enabled torch correctly.

### **Option 1: Manual Installation (Classic Method)**
If you prefer manual installation, install dependencies using:
```bash
pip install -r requirements.txt
```
(If you encounter errors with **audiocraft**, please refer to their [official documentation](https://github.com/facebookresearch/audiocraft)).

### **Option 2: Using the Install Script (Automated Setup)**
To automate installation and environment setup, use the provided script:
- **Linux/macOS:**
  ```bash
  ./install.sh
  ```
- **Windows:**
  ```cmd
  install.bat
  ```
This will check for **Python 3.10**, create a virtual environment (`venv`), and install all required dependencies automatically. If Conda is available, it can be used instead of venv.

---

## Run:

### **Option 1: Manual Run (Classic Method)**
Start the web UI manually using:
```bash
python webui.py
```

### **Option 2: Using the Run Script (Automated Execution)**
Alternatively, use the run script for easier execution:
- **Linux/macOS:**
  ```bash
  ./run.sh
  ```
- **Windows:**
  ```cmd
  run.bat
  ```
This will automatically activate the appropriate environment (virtualenv or Conda) and start `webui.py`. Once the script is stopped, it ensures the environment is properly deactivated.

---

There's no need to download any external models. Simply pick a model from the dropdown menu, and when you run it for the first time, it will be automatically downloaded via **Audiocraft**.

If you want to use **Melody Mode**, select the **Melody model**, and an option to upload your melody audio file will appear.

---

## Notes:
- Generated files are saved in the `static/audio/` directory.
- The currently active model remains loaded in memory by default. To unload it after each generation, launch with:
  ```bash
  python webui.py --unload-after-gen
  ```
- The UI could use an improved design—contributors are welcome!

---

## Parameters:

- **Top-K**: Affects the variety of generated audio. Higher values lead to more diverse results but may increase randomness.
- **Top-P**: Recommended around 0.7. Controls sampling diversity, with lower values producing more stable results.
- **Duration**: Length of generated audio.
- **CFG (Classifier Free Guidance)**: Determines how strictly the output follows the prompt (recommended 3-5).
- **Temperature**: Controls randomness. Higher values (1.05-1.5) create more chaotic results, while lower values yield structured outputs.

---

## Troubleshooting:
- **Torch Installation Issues:**
  Ensure you have the correct **CPU/GPU version** installed ([PyTorch Guide](https://pytorch.org/get-started/locally/)).
- **Virtual Environment Issues:**
  If activation fails, try:
  ```bash
  source venv/bin/activate  # Linux/macOS
  venv\Scripts\activate    # Windows
  ```
- **Conda Not Found?**
  Ensure Conda is installed and added to `PATH`. Verify by running:
  ```bash
  conda --version
  ```
- **Installation Script Issues?**
  Ensure scripts have execution permissions:
  ```bash
  chmod +x install.sh run.sh
  ```

---

## Changelog:

### Feb-25-2024:
- Rewrote everything.
- Added generation history for audio outputs.
- Removed outdated dependencies.
- Removed deprecated parameters (`overlap` and `segments`).

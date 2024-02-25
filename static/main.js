var socket = io.connect('http://' + document.domain + ':' + location.port);

// SLIDERS

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('input[type="range"]').forEach(function(slider) {
        updateSliderValue(slider.id, slider.value);
    });
});

function submitSliders() {
    var slidersData = {};
    var textData = document.getElementById('text').value;

    var modelSelector = document.getElementById('modelSelector')
    var modelSize = modelSelector.value;

    var audioElement = document.getElementById('audio-preview');
    audioSrc = audioElement.src;

    if (modelSize !== "melody" || audioSrc === "") {
        document.querySelectorAll('input[type="range"]').forEach(function(slider) {
            slidersData[slider.id] = slider.value;
        });
        socket.emit('submit_sliders', {values: slidersData, prompt:textData, model:modelSize});
        return;
    }

    document.querySelectorAll('input[type="range"]').forEach(function(slider) {
        slidersData[slider.id] = slider.value;
    });
    socket.emit('submit_sliders', {values: slidersData, prompt:textData, model:modelSize, melodyUrl:audioSrc});
}

// ADD TO QUEUE

socket.on('add_to_queue', function(data) {
    addPromptToQueue(data.prompt);
});

function addPromptToQueue(prompt_data) {
    const promptListDiv = document.querySelector('.prompt-queue');

    const promptItemDiv = document.createElement('div');
    promptItemDiv.className = 'audio-item';
    promptItemDiv.setAttribute('completed-segments', '0');
    promptItemDiv.setAttribute('data-max-tokens', '0');

    promptItemDiv.style.background = 'linear-gradient(to right, blue 0%, transparent 0%)';
    const promptItemTextDiv = document.createElement('div');
    promptItemTextDiv.className = 'audio-item-text';
    promptItemTextDiv.textContent = prompt_data;

    promptItemDiv.appendChild(promptItemTextDiv);
    promptListDiv.appendChild(promptItemDiv);
}

// AUDIO RENDERED

socket.on('on_finish_audio', function(data) {
    const promptListDiv = document.querySelector('.prompt-queue');
    const firstPromptItem = promptListDiv.querySelector('.audio-item');
    if (firstPromptItem) {
        promptListDiv.removeChild(firstPromptItem);
    }

    addAudioToList(data.prompt, data.filename, data.json_filename);
});

function addAudioToList(prompt, filename, json_filename) {
    fetch(json_filename)
    .then(response => response.json())
    .then(json_data => {
        const audioListDiv = document.querySelector('.audio-list');

        const audioItemDiv = document.createElement('div');
        audioItemDiv.className = 'audio-item';

        const promptDiv = document.createElement('div');
        promptDiv.className = 'audio-item-text';
        promptDiv.textContent = `${json_data.prompt}`;

        const parametersDiv = document.createElement('div');
        parametersDiv.className = 'audio-item-params';

        const modelDiv = document.createElement('div');
        modelDiv.className = 'audio-item-text';
        modelDiv.textContent = `Model: ${json_data.model}`;
        parametersDiv.appendChild(modelDiv);

        for (const key in json_data.parameters) {
            const paramDiv = document.createElement('div');
            paramDiv.className = 'audio-item-text';
            paramDiv.textContent = `${key}: ${json_data.parameters[key]}`;
            parametersDiv.appendChild(paramDiv);
        }

        const audio = document.createElement('audio');
        audio.controls = true;

        const source = document.createElement('source');
        source.src = filename;
        source.type = 'audio/wav';

        audioItemDiv.appendChild(promptDiv);
        audio.appendChild(source);
        audioItemDiv.appendChild(audio);
        audioItemDiv.appendChild(parametersDiv);

        if (audioListDiv.firstChild) {
            audioListDiv.insertBefore(audioItemDiv, audioListDiv.firstChild);
        } else {
            // If .audio-list has no children yet, appendChild works the same as insertBefore
            audioListDiv.appendChild(audioItemDiv);
        }
    })
}

// PROGRESS
const rootStyles = getComputedStyle(document.documentElement);  
const completionColor = rootStyles.getPropertyValue('--hamster').trim();  

socket.on('progress', function(data) {
    progress_value = data.progress * 100;

    const promptListDiv = document.querySelector('.prompt-queue');
    const firstPromptItem = promptListDiv.querySelector('.audio-item');

    if (firstPromptItem) {
        firstPromptItem.style.background = `linear-gradient(to right, ${completionColor} ${progress_value}%, transparent ${progress_value}%)`;
        firstPromptItem.querySelector('.audio-item-text').style.textShadow = '1px 3px 6px black';
    }
});
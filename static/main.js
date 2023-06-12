const sliderNames = ['duration', 'topp', 'temperature', 'topk', 'cfg_coef', 'segments', 'overlap'];

sliderNames.forEach(name => {
    const slider = document.querySelector(`#${name}`);
    const textField = document.querySelector(`#${name}-text`);

    slider.oninput = function() {
        textField.value = this.value;
    }

    textField.oninput = function() {
        slider.value = this.value;
    }
});

document.getElementById("text").addEventListener("keydown", function(e) {
    if (e.keyCode === 13) {  // checks whether the pressed key is "Enter"
        e.preventDefault();  // prevent the default action (i.e., inserting a new line)
        document.getElementById("submit").click();  // trigger the submit button click event
    }
});

var socket = io.connect('http://localhost:5000');
socket.on('new_file', function(data) {
    var output_filename = data.output_filename;
    var new_file = {
        text: output_filename,
        audio_file: output_filename
    };
    appendNewAudioFile(new_file);

    const promptListDiv = document.querySelector('.prompt-queue');
    const firstPromptItem = promptListDiv.querySelector('.audio-item');
    if (firstPromptItem) {
        promptListDiv.removeChild(firstPromptItem);
    }
});

const rootStyles = getComputedStyle(document.documentElement);  
const completionColor = rootStyles.getPropertyValue('--hamster').trim();  

socket.on('progress', function(data) {
    const promptListDiv = document.querySelector('.prompt-queue');
    const firstPromptItem = promptListDiv.querySelector('.audio-item');
    let segments = parseInt(firstPromptItem.getAttribute('data-segments'), 10);
    let maxTokens = parseInt(firstPromptItem.getAttribute('data-max-tokens'), 10);
    let completedSegments = parseInt(firstPromptItem.getAttribute('completed-segments'), 10);

    if (firstPromptItem) {
        if (data.generated_tokens < maxTokens && maxTokens != 0) {
            // A new segment has started
            completedSegments++;
            firstPromptItem.setAttribute('data-max-tokens', '0');
            maxTokens = 0;
        } else {
            // We're still in the same segment
            maxTokens = data.generated_tokens;
            firstPromptItem.setAttribute('data-max-tokens', maxTokens.toString());
        }

        let completionPercentage = ((completedSegments * data.tokens_to_generate + data.generated_tokens) / (segments * data.tokens_to_generate)) * 100;  // calculate the completion percentage
        
        firstPromptItem.style.background = `linear-gradient(to right, ${completionColor} ${completionPercentage}%, transparent ${completionPercentage}%)`;
        firstPromptItem.querySelector('.audio-item-text').style.textShadow = '1px 3px 6px black';
        firstPromptItem.setAttribute('completed-segments', completedSegments.toString());
    }
});

$(document).ready(function() {
    function toggleMelodyField() {
        let model = $("#model").val();
        if (model === "melody") {

            $("#melody-field").show();
        } else {

            $("#melody-field").hide();
        }
    }

    toggleMelodyField();

    $("#model").change(toggleMelodyField);

    $('form').on('submit', function(event) {
        event.preventDefault(); 

        // serialize form data
        var formData = new FormData(this);
        var submitButton = $('#submit');

        submitButton.addClass('loading');
        addPromptToQueue(formData)

        $.ajax({
            type: 'POST',
            url: '/',
            data: formData,
            contentType: false,
            processData: false,
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.error('Error:', errorThrown);
        })
        .always(function() {
            submitButton.removeClass('loading');
        });
    });
});

async function loadInitialAudioList() {
    try {
        const response = await fetch('/api/audio-files');
        const audioFiles = await response.json();
        
        const audioListDiv = document.querySelector('.audio-list');
        audioFiles.sort((a, b) => a.timestamp - b.timestamp);

        // Clear the existing audio list
        audioListDiv.innerHTML = '<div class="audio-padding"></div>';

        for (const file of audioFiles) {
            appendNewAudioFile(file, audioListDiv, false);
        }

        // Add the padding div
        const audioPaddingDiv = document.createElement('div');
        audioPaddingDiv.className = 'audio-padding';
        audioListDiv.appendChild(audioPaddingDiv);

    } catch (error) {
        console.error('Error:', error);
    }
}

function appendNewAudioFile(file, audioListDiv = null, prepend = true) {
    if (!audioListDiv) {
        audioListDiv = document.querySelector('.audio-list');
    }

    const audioItemDiv = document.createElement('div');
    audioItemDiv.className = 'audio-item';

    const audioItemTextDiv = document.createElement('div');
    audioItemTextDiv.className = 'audio-item-text';
    audioItemTextDiv.textContent = file.text;
    audioItemDiv.appendChild(audioItemTextDiv);

    const audio = document.createElement('audio');
    audio.controls = true;

    const source = document.createElement('source');
    source.src = '/static/audio/' + file.audio_file;
    source.type = 'audio/wav';

    audio.appendChild(source);
    audioItemDiv.appendChild(audio);

    const firstAudioItem = audioListDiv.querySelector('.audio-item');
    
    // If there's an audio item, insert the new one before it.
    // Otherwise, just append the new audio item.
    if (firstAudioItem) {
        audioListDiv.insertBefore(audioItemDiv, firstAudioItem);
    } else {
        audioListDiv.appendChild(audioItemDiv);
    }
}

function addPromptToQueue(formData) {
    const promptListDiv = document.querySelector('.prompt-queue');
    const promptItemDiv = document.createElement('div');
    promptItemDiv.className = 'audio-item';
    promptItemDiv.setAttribute('completed-segments', '0');
    promptItemDiv.setAttribute('data-max-tokens', '0');

    // Add an initial gradient to the item
    promptItemDiv.style.background = 'linear-gradient(to right, blue 0%, transparent 0%)';  // initial gradient (0% completion)

    const promptItemTextDiv = document.createElement('div');
    promptItemTextDiv.className = 'audio-item-text';

    for (let [key, value] of formData.entries()) {
        // Append all parameters as attributes
        promptItemDiv.setAttribute(`data-${key}`, value);
        if (key === 'text') {
            const formEntry = document.createElement('p');
            formEntry.textContent = `${value}`;
            promptItemTextDiv.appendChild(formEntry);
        }
    }

    let segments = parseInt(promptItemDiv.getAttribute('data-segments'), 10);
    if (segments !== 1) {
        segments += 1;
    }
    promptItemDiv.setAttribute('data-segments', segments.toString());    

    promptItemDiv.appendChild(promptItemTextDiv);
    promptListDiv.appendChild(promptItemDiv);
}

loadInitialAudioList();

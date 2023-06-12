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

var socket = io.connect('http://localhost:5000');  // replace with your server address
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

        submitButton.addClass('loading');  // add the loading class to the submit button
        addPromptToQueue(formData.get('text'))

        $.ajax({
            type: 'POST',
            url: '/',  // the endpoint where the form data should be POSTed
            data: formData,
            contentType: false,
            processData: false,
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.error('Error:', errorThrown);
        })
        .always(function() {
            submitButton.removeClass('loading');  // remove the loading class from the submit button
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

        // Create a new audio list
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

    // Get the first audio-item in the list
    const firstAudioItem = audioListDiv.querySelector('.audio-item');
    
    // If there's an audio item, insert the new one before it.
    // Otherwise, just append the new audio item.
    if (firstAudioItem) {
        audioListDiv.insertBefore(audioItemDiv, firstAudioItem);
    } else {
        audioListDiv.appendChild(audioItemDiv);
    }
}

function addPromptToQueue(prompt) {
    const promptListDiv = document.querySelector('.prompt-queue');
    const promptItemDiv = document.createElement('div');
    promptItemDiv.className = 'audio-item';

    const promptItemTextDiv = document.createElement('div');
    promptItemTextDiv.className = 'audio-item-text';
    console.log(prompt)
    promptItemTextDiv.textContent = prompt;
    promptItemDiv.appendChild(promptItemTextDiv);

    promptListDiv.appendChild(promptItemDiv);
}

// Call the function when the page loads
loadInitialAudioList();
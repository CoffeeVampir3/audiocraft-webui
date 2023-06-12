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

        $.ajax({
            type: 'POST',
            url: '/',  // the endpoint where the form data should be POSTed
            data: formData,
            contentType: false,
            processData: false,
        })
        .done(function(response) {
            console.log(response);
            appendNewAudioFile(response);
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

// Call the function when the page loads
loadInitialAudioList();
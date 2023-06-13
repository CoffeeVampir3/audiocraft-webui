const socket = io.connect('http://localhost:5000');

socket.on('new_file', function (data) {
    const output_filename = data.output_filename;
    const new_file = {
        text: output_filename,
        audio_file: output_filename,
    };
    addNewAudioItem(new_file, { append: false, isNew: true });
});

socket.on('progress', function (data) {
    handleQueueProgress(data);
});

$(document).ready(function () {
    //melody
    function toggleMelodyField() {
        let model = $('#model').val();
        if (model === 'melody') {
            $('.form__pick-melody').show();
        } else {
            $('.form__pick-melody').hide();
        }
    }

    toggleMelodyField();

    $('#model').change(toggleMelodyField);

    document.getElementById('pick-melody')?.addEventListener('click', function (e) {
        e.preventDefault();
        document.getElementById('melody')?.click();
    });
    document.getElementById('remove-melody')?.addEventListener('click', function (e) {
        e.preventDefault();
        const input = document.getElementById('melody');
        if (input != null) {
            input.value = '';
        }
        onMelodyPicked(undefined);
    });

    //melody preview
    const onMelodyPicked = (file) => {
        const preview = document.getElementById('melody-preview');

        if (preview?.src != null && preview.src !== '') {
            URL.revokeObjectURL(preview.src);
            preview.src = undefined;
        }
        if (file != null && preview != null) {
            preview.src = URL.createObjectURL(file);
        }
        const pickMelody = document.getElementById('pick-melody');
        if (pickMelody != null) {
            pickMelody.innerText = file != null ? 'Pick Another Melody' : 'Pick Optional Melody';
        }
        const removeMelody = document.getElementById('remove-melody');
        toggleElementDisplay(removeMelody, file != null);
    };
    onMelodyPicked(undefined);

    document.getElementById('melody')?.addEventListener('change', (e) => {
        onMelodyPicked(e.target.files && e.target.files.length > 0 ? e.target.files.item(0) : undefined);
    });

    //prompt input and submit
    document.getElementById('prompt-input')?.addEventListener('keydown', function (e) {
        if (e.keyCode === 13) {
            // checks whether the pressed key is "Enter"
            e.preventDefault(); // prevent the default action (i.e., inserting a new line)
            document.getElementById('prompt-submit')?.click(); // trigger the submit button click event
        }
    });

    $('form').on('submit', function (event) {
        event.preventDefault();

        // serialize form data
        const formData = new FormData(this);
        formData.append('id', (Math.random() + 1).toString(16).substring(2, 12)); //assign random id
        const submitButton = document.getElementById('prompt-submit');

        submitButton.innerHTML = `<div class="spinner-border spinner-border-sm" role="status">
                                        <span class="sr-only visually-hidden">Loading...</span>
                                    </div>`;

        $.ajax({
            type: 'POST',
            url: '/',
            data: formData,
            contentType: false,
            processData: false,
        })
            .then(() => {
                handleQueueProgress({ segments: formData.get('segments'), id: formData.get('id'), prompt: formData.get('text') });
                document.getElementById('prompt-input').value = '';
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                console.error('Error:', errorThrown);
                removeQueueItem(formData.get('id'), { finish: false });
            })
            .always(function () {
                submitButton.innerHTML = 'Submit';
            });
    });

    loadInitialAudioList();
});

async function loadInitialAudioList() {
    try {
        const response = await fetch('/api/audio-files');
        const audioFiles = await response.json();
        audioItems.splice(0, audioItems.length);
        audioItems.push(...audioFiles);
        rebuildSidebarDom();
    } catch (error) {
        console.error('Error:', error);
    }
}

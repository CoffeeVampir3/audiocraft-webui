//elements
let audioElement = null;
let playbackTitleElement = null;
let playElement = null;
let pauseElement = null;
let restartElement = null;
let errorElement = null;
let playbackTextElement = null;
let seekElement = null;
$(document).ready(function () {
    audioElement = document.querySelector('.playback audio');
    playbackTitleElement = document.querySelector('.playback__title');
    playElement = document.querySelector('.playback__play-btn');
    pauseElement = document.querySelector('.playback__pause-btn');
    restartElement = document.querySelector('.playback__restart-btn');
    errorElement = document.querySelector('.playback__error-btn');
    playbackTextElement = document.querySelector('.playback__time label');
    seekElement = document.querySelector('.playback__seek');

    //handlers
    playElement.addEventListener('click', () => setPlaying(true));
    pauseElement.addEventListener('click', () => setPlaying(false));
    restartElement.addEventListener('click', () => setPlaying(true));

    audioElement.addEventListener('pause', () => updatePlayback({ playing: false }));
    audioElement.addEventListener('play', () => updatePlayback({ playing: true }));
    audioElement.addEventListener('ended', () => updatePlayback({ ended: true }));
    audioElement.addEventListener('play', () => updatePlayback({ playing: true }));
    audioElement.addEventListener('canplay', onAudioReadyStateChange);
    audioElement.addEventListener('error', onAudioReadyStateChange);
    audioElement.addEventListener('loadeddata', onAudioReadyStateChange);
    audioElement.addEventListener('loadedmetadata', onAudioReadyStateChange);
    audioElement.addEventListener('timeupdate', onTimeupdate);
    audioElement.addEventListener('durationchange', onTimeupdate);

    seekElement.addEventListener('change', e => audioElement.currentTime = (e.target.value));

    selectAudioFile(undefined);
});

//handlers

function onTimeupdate(event) {
    if(Number.isNaN(event.target.duraton) || Number.isNaN(event.target.currentTime)) {
        updatePlayback({time: null});
    } else {
        updatePlayback({time: event.target.currentTime, duration: event.target.duration});
    }
}

function onAudioReadyStateChange(event) {
    updatePlayback({ canPlay: event.target.readyState >= 2, error: event.target.error != null });
}

function enableControl(control) {
    toggleElementDisplay(playElement, control === 'play');
    toggleElementDisplay(pauseElement, control === 'pause');
    toggleElementDisplay(restartElement, control === 'restart');
    toggleElementDisplay(errorElement, control === 'error');
}

//control methods
function updatePlayback({ title, playing, canPlay, src, error, ended, time, duration }) {
    if (playing !== undefined) {
        enableControl(playing ? 'pause' : 'play');
    }

    if(time !== undefined || duration !== undefined) {
        const invalid = time == null || duration == null;
        seekElement.min = 0;
        seekElement.max = invalid ? 0 : duration + 1;
        seekElement.value = invalid ? 0 : time;
        playbackTextElement.innerText = invalid ? '' : secondsToDuration(time) + ' / ' + secondsToDuration(duration);
        toggleElementDisplay(seekElement, !invalid);
    }

    if (ended === true) {
        enableControl('restart');
    }

    if(error === true) {
        enableControl('error');
    }

    if (canPlay !== undefined) {
        const elements = [playElement, pauseElement, restartElement, errorElement];
        if (canPlay) {
            elements.forEach((el) => el.removeAttribute('disabled'));
        } else {
            elements.forEach((el) => el.setAttribute('disabled', true));
        }
    }
    if (src !== undefined && audioElement != null) {
        audioElement.src = src;
    }
    if (title !== undefined) {
        playbackTitleElement.innerText = title ?? playbackTitle.innerText;
    }
}

function resetPlayback() {
    updatePlayback({ playing: false, canPlay: false, title: '', time: null, duration: null});
}

function setPlaying(playing = true) {
    if (playing === true && (selectedAudioFile == null || audioElement == null)) {
        setPlaying(false);
        return;
    }

    if (audioElement != null) {
        if (playing) {
            //start playback
            audioElement.play();
        } else {
            audioElement.pause();
        }
    }
}

//playback
let selectedAudioFile = undefined;
function selectAudioFile(file) {
    selectedAudioFile = file;
    setPlaying(false);

    if (selectedAudioFile == null) {
        resetPlayback();
    } else {
        updatePlayback({
            title: selectedAudioFile.text,
            canPlay: true,
            playing: false,
            ended: false,
            src: '/static/audio/' + selectedAudioFile.audio_file,
        });
    }
}

//elements
let audioElement = null;

$(document).ready(function () {
    audioElement = document.getElementById('playback');
    ['pause', 'play', 'ended', 'canplay', 'error', 'loadeddata', 'loadedmetadata', 'timeupdate', 'durationchange'].forEach((eventType) =>
        audioElement.addEventListener(eventType, (event) => {
            if (selectedPlayback != null) {
                selectedPlayback.handleAudioElementEvent(event);
            }
        })
    );
});

//playback
let selectedPlayback = undefined;
function selectPlayback(playback, play = true) {
    if (selectedPlayback != null) {
        selectedPlayback.stop();
    }
    selectedPlayback = playback;
    if(play && selectedPlayback != null) {
        selectedPlayback.play();
    }
}

//yes, this could be a class
//no, I can't be bothered
function preparePlayback(rootNode, audioSource, playingChangeCb, stopCb) {
    const playbackElement = rootNode.querySelector('.playback');
    const playElement = rootNode.querySelector('.play-btn');
    const pauseElement = rootNode.querySelector('.pause-btn');
    const restartElement = rootNode.querySelector('.restart-btn');
    const errorElement = rootNode.querySelector('.error-btn');
    const seekLabelElement = rootNode.querySelector('.audio-item__seek label');
    const seekInputElement = rootNode.querySelector('.audio-item__seek input');

    //handlers
    playElement.addEventListener('click', () => playback.play());
    pauseElement.addEventListener('click', () => playback.pause());
    restartElement.addEventListener('click', () => playback.play());
    seekInputElement.addEventListener('change', (e) => {
        if (audioElement != null) {
            audioElement.currentTime = e.target.value;
        }
    });

    const isPlaybackShown = () => isElementDisplayed(playbackElement);

    const enableBtn = (btn) => {
        toggleElementDisplay(playElement, btn === 'play');
        toggleElementDisplay(pauseElement, btn === 'pause');
        toggleElementDisplay(restartElement, btn === 'restart');
        toggleElementDisplay(errorElement, btn === 'error');
    };

    const updateUi = ({ playing, canPlay, error, ended, time, duration, show }) => {
        if (playing !== undefined) {
            enableBtn(playing ? 'pause' : 'play');
            if (playing) {
                //if now playing, enable playback area
                toggleElementDisplay(playbackElement, true);
            }
        }

        if (show !== undefined) {
            toggleElementDisplay(playbackElement, show);
        }

        if (time !== undefined || duration !== undefined) {
            const invalid = time == null || duration == null;
            seekInputElement.min = 0;
            seekInputElement.max = invalid ? 0 : duration;
            seekInputElement.value = invalid ? 0 : time;
            seekLabelElement.innerText = invalid ? '' : secondsToDuration(time) + ' / ' + secondsToDuration(duration);
            toggleElementDisplay(seekInputElement, !invalid);
        }

        if (ended === true) {
            enableBtn('restart');
        }

        if (error === true) {
            enableBtn('error');
        }

        if (canPlay !== undefined) {
            const elements = [playElement, pauseElement, restartElement, errorElement];
            if (canPlay) {
                elements.forEach((el) => el.removeAttribute('disabled'));
            } else {
                elements.forEach((el) => el.setAttribute('disabled', true));
            }
        }
    };

    const resetUi = () => {
        updateUi({ playing: false, canPlay: false, error: false, ended: false, time: null, duration: null, show: false });
    };

    const setPlaying = (playing = true) => {
        if (playing && !isPlaybackShown()) {
            //switching to playing this for the first time
            if (audioElement != null) {
                audioElement.src = audioSource;
            }
            updateUi({ playing, canPlay: true, error: false, ended: false, time: null, duration: null, show: false });
        }
        if (playing) {
            audioElement.play();
        } else {
            audioElement.pause();
        }
    };

    const onPlayingChange = (playing) => {
        updateUi({playing});
        if(playingChangeCb != null) {
            playingChangeCb(playing);
        }
    }

    const playback = {
        root: rootNode,
        play: () => {
            if(!isPlaybackShown()) {
                selectPlayback(playback, false);
            }
            setPlaying(true);
        },
        pause: () => setPlaying(false),
        stop: () => {
            if (audioElement != null) {
                audioElement.pause();
                audioElement.src = undefined;
            }
            resetUi();
            if(stopCb != null) {
                stopCb();
            }
        }, 
        handleAudioElementEvent: (event) => {
            switch (event.type) {
                case 'pause':
                    onPlayingChange(false);
                    break;
                case 'play':
                    onPlayingChange(true);
                    break;
                case 'ended':
                    onPlayingChange(false);
                    break;
                case 'canplay':
                case 'error':
                case 'loadedmetadata':
                case 'loadeddata':
                    updateUi({ canPlay: event.target.readyState >= 2, error: event.target.error != null });
                    break;
                case 'timeupdate':
                case 'durationchange':
                    if (Number.isNaN(event.target.duraton) || Number.isNaN(event.target.currentTime)) {
                        updateUi({ time: null });
                    } else {
                        updateUi({ time: event.target.currentTime, duration: event.target.duration });
                    }
                    break;
            }
        }
    };

    resetUi();

    return playback;
}

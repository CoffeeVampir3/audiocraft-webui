/**
 * {text: string, audio_file: string; timestamp: string; duration?: number; }[]
 */
const audioItems = [];
/**
 * { generated_tokens: number; tokens_to_generate: number; segments_completed: number; id: string; prompt: string; duration?: number; segments: number; }[]
 */
const queueItems = [];
/**
 * To ignore stray socket io events for finished items.
 */
const finishedQueue = [];

function handleQueueProgress(progress) {
    if (progress.id == null) {
        //invalid
        return;
    }
    if (finishedQueue.findIndex((fin) => fin.id === progress.id) !== -1) {
        return; //ignore
    }
    const existingIdx = queueItems.findIndex((item) => item.id === progress.id);
    let segments_completed = 0;
    if (existingIdx !== -1) {
        //existing item, calculate how many segments completed...
        segments_completed = queueItems[existingIdx].segments_completed;
        if (progress.generated_tokens < queueItems[existingIdx].generated_tokens) {
            //looped over!
            segments_completed++;
        }
    }
    //replace or insert at end
    const queueItem = {
        ...(existingIdx !== -1 ? queueItems[existingIdx] : undefined),
        ...progress,
        segments_completed,
    };
    queueItems.splice(existingIdx === -1 ? queueItems.length : existingIdx, existingIdx === -1 ? 0 : 1, queueItem);
    updateQueueItemDom(queueItem);
}

function removeQueueItem(id, { finish = false } = {}) {
    const elementId = 'queue-item-' + id;
    const el = document.getElementById(elementId);
    if (el != null) {
        el.remove();
    }
    const itemIdx = queueItems.findIndex((arrItem) => arrItem.id === id);
    if (finish && itemIdx !== -1) {
        finishedQueue.push(...queueItems.splice(itemIdx, 1));
    }
}

function updateQueueItemDom(queueItem) {
    const elementId = 'queue-item-' + queueItem.id;
    let progress =
        ((queueItem.segments_completed * queueItem.tokens_to_generate + queueItem.generated_tokens) /
            (queueItem.segments * queueItem.tokens_to_generate)) *
        100;
    if (Number.isNaN(progress)) {
        progress = 0;
    }

    if (progress >= 100) {
        removeQueueItem(queueItem.id, { finish: true });
        return;
    }

    const findOrCreate = findOrCreateTemplateInstance('#' + elementId, '.queue-item', ['.queue-item__title', '.queue-item__progress-bar']);
    findOrCreate(({ root, selectedElements: [title, progressBar] }) => {
        root.id = elementId;
        progressBar.style.width = progress + '%';
        title.innerText = queueItem.prompt;
    });
}

function getAudioItemTemplate() {
    return loadTemplate(
        '.audio-item',
        ['.audio-item__title', '.audio-item__timestamp', '.audio-item__duration', '.audio-item__newtag'],
        true
    );
}

function createAudioItemDom(file, { append = true, isNew = false } = {}) {
    const template = getAudioItemTemplate();
    template?.create(
        ({ root, selectedElements: [title, timestamp, duration, newtag] }) => {
            root.id = 'audio-item-' + title;
            $(root).data('file', file);
            toggleElementDisplay(newtag, isNew);

            //bind display values
            title.innerText = file.text;
            let dt = new Date();
            if(file.timestamp) {
                dt = new Date(0);
                dt.setUTCSeconds(file.timestamp);
            }
            timestamp.innerText =
                dt.toLocaleDateString('en-us', { month: 'short', day: 'numeric' }) + ' at ' + dt.toLocaleTimeString('en-US');
            if (file.duration != null) {
                duration.innerText = typeof file.duration === 'number' ? secondsToDuration(file.duration) : file.duration;
            } else {
                toggleElementDisplay(duration, false);
            }

            //create playback
            const playback = preparePlayback(
                root,
                '/static/audio/' + file.audio_file,
                () => {
                    toggleElementDisplay(newtag, false);
                    root.classList.toggle('selected', true);
                },
                () => {
                    root.classList.toggle('selected', false);
                }
            );
            $(root).data('playback', playback);
        },
        { append }
    );
}

function addNewAudioItem(file, { append = false, isNew = false } = {}) {
    audioItems.push(file);
    createAudioItemDom(file, { append, isNew });
}

function rebuildSidebarDom() {
    const audioItemTemplate = getAudioItemTemplate();
    audioItemTemplate.clear();

    audioItems.sort((a, b) => b.timestamp - a.timestamp);
    for (const audioItem of audioItems) {
        createAudioItemDom(audioItem, false);
    }

    for (const queueItem of queueItems) {
        updateQueueItemDom(queueItem);
    }
}

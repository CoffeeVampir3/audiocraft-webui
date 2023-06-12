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
    if(finishedQueue.findIndex(fin => fin.id === progress.id) !== -1) {
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

function updateQueueItemDom(queueItem) {
    const id = 'queue-item-' + queueItem.id;
    const progress =
        ((queueItem.segments_completed * queueItem.tokens_to_generate + queueItem.generated_tokens) /
            (queueItem.segments * queueItem.tokens_to_generate)) *
        100;

    if (progress >= 100) {
        const el = document.getElementById(id);
        if (el != null) {
            el.remove();
        }
        const itemIdx = queueItems.findIndex((arrItem) => arrItem.id === queueItem.id);
        if (itemIdx !== -1) {
            finishedQueue.push(...queueItems.splice(itemIdx, 1));
        }
        return;
    }

    const findOrCreate = findOrCreateTemplateInstance('#' + id, '.queue-item', ['.queue-item__title', '.queue-item__progress-bar']);
    findOrCreate(({ root, selectedElements: [title, progressBar] }) => {
        root.id = id;
        progressBar.style.width = progress + '%';
        title.innerText = queueItem.prompt;
    });
}

function getAudioItemTemplate() {
    return loadTemplate('.audio-item', ['.audio-item__title', '.audio-item__timestamp', '.audio-item__duration'], true);
}

function createAudioItemDom(file, { append = true } = {}) {
    const template = getAudioItemTemplate();
    template?.create(
        ({ root, selectedElements: [title, timestamp, duration] }) => {
            $(root).data('file', file);
            //bind display values
            title.innerText = file.text;
            const dt = new Date(0);
            dt.setUTCSeconds(file.timestamp);
            timestamp.innerText =
                dt.toLocaleDateString('en-us', { month: 'short', day: 'numeric' }) + ' at ' + dt.toLocaleTimeString('en-US');
            if (file.duration != null) {
                duration.innerText = typeof file.duration === 'number' ? secondsToDuration(file.duration) : file.duration;
            } else {
                toggleElementDisplay(duration, false);
            }
            //handlers
            root.addEventListener('click', function (event) {
                event.preventDefault();
                selectAudioFile(file);

                //update selected class for all file items
                document.querySelectorAll('.audio-item:not(.d-none)').forEach((el) => {
                    el.classList.toggle('selected', $(el).data('file')?.audio_file === selectedAudioFile?.audio_file);
                });
            });
        },
        { append }
    );
}

function addNewAudioItem(file, { append = false } = {}) {
    audioItems.push(file);
    createAudioItemDom(file, { append });
}

function rebuildSidebarDom() {
    const audioItemTemplate = getAudioItemTemplate();
    audioItemTemplate.clear();

    audioItems.sort((a, b) => b.timestamp - a.timestamp);
    for (const audioItem of audioItems) {
        createAudioItemDom(audioItem);
    }

    for (const queueItem of queueItems) {
        updateQueueItemDom(queueItem);
    }
}

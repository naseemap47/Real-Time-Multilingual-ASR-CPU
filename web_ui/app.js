// Real-Time Multilingual ASR JavaScript Client Application

document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const statusBadge = document.getElementById('statusBadge');
    const modelSelect = document.getElementById('modelSelect');
    const langSelect = document.getElementById('langSelect');
    const dropzone = document.getElementById('dropzone');
    const audioFileInput = document.getElementById('audioFileInput');
    const fileInfoText = document.getElementById('fileInfoText');
    const btnStart = document.getElementById('btnStart');
    const btnStop = document.getElementById('btnStop');
    const btnReset = document.getElementById('btnReset');
    const transcriptFeed = document.getElementById('transcriptFeed');
    const chunkCountBadge = document.getElementById('chunkCountBadge');

    const valLatency = document.getElementById('valLatency');
    const valRtf = document.getElementById('valRtf');
    const valActiveLegs = document.getElementById('valActiveLegs');
    const valAudioDuration = document.getElementById('valAudioDuration');

    // App State Variables
    let selectedFile = null;
    let selectedAudioBytes = null;
    let ws = null;
    let isStreaming = false;
    let totalChunksSent = 0;
    let streamTimer = null;

    // Dropzone & File Select Logic
    dropzone.addEventListener('click', () => audioFileInput.click());
    
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#6366f1';
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        if (e.dataTransfer.files.length > 0) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    audioFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        if (!file.name.toLowerCase().endsWith('.wav')) {
            alert('Please select a valid WAV audio file.');
            return;
        }
        selectedFile = file;
        fileInfoText.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        btnStart.disabled = false;

        const reader = new FileReader();
        reader.onload = function (evt) {
            selectedAudioBytes = evt.target.result;
        };
        reader.readAsArrayBuffer(file);
    }

    // Controls
    btnStart.addEventListener('click', startStreaming);
    btnStop.addEventListener('click', stopStreaming);
    btnReset.addEventListener('click', resetApp);

    function startStreaming() {
        if (!selectedAudioBytes) {
            alert('Please select a WAV file first.');
            return;
        }

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = window.location.host || 'localhost:8000';
        const wsUrl = `${wsProtocol}//${wsHost}/ws/asr`;

        ws = new WebSocket(wsUrl);
        isStreaming = true;
        totalChunksSent = 0;

        btnStart.disabled = true;
        btnStop.disabled = false;
        modelSelect.disabled = true;
        langSelect.disabled = true;

        statusBadge.textContent = 'STREAMING';
        statusBadge.className = 'badge badge-streaming';
        transcriptFeed.innerHTML = '';

        ws.onopen = () => {
            // Send start configuration frame
            ws.send(JSON.stringify({
                action: 'start',
                session_id: 'web_session_' + Date.now(),
                model: modelSelect.value,
                language: langSelect.value
            }));

            // Begin real-time chunk streaming
            streamAudioChunks();
        };

        ws.onmessage = (evt) => {
            const data = JSON.parse(evt.data);
            handleServerEvent(data);
        };

        ws.onclose = () => {
            if (isStreaming) {
                stopStreaming();
            }
        };

        ws.onerror = (err) => {
            console.error('WebSocket Error:', err);
            stopStreaming();
        };
    }

    function streamAudioChunks() {
        if (!selectedAudioBytes) return;

        // Skip WAV 44-byte header if present
        const pcmPayload = selectedAudioBytes.byteLength > 44 ? selectedAudioBytes.slice(44) : selectedAudioBytes;
        // 200ms chunk @ 16kHz 16-bit mono = 6400 bytes
        const chunkSize = 6400;
        let offset = 0;

        streamTimer = setInterval(() => {
            if (!isStreaming || ws.readyState !== WebSocket.OPEN) {
                clearInterval(streamTimer);
                return;
            }

            if (offset < pcmPayload.byteLength) {
                const chunk = pcmPayload.slice(offset, offset + chunkSize);
                ws.send(chunk);
                offset += chunkSize;
                totalChunksSent++;
                chunkCountBadge.textContent = `${totalChunksSent} chunks`;
                valAudioDuration.textContent = `${(offset / 32000).toFixed(1)}s`;
            } else {
                // Audio payload finished, send stop
                clearInterval(streamTimer);
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ action: 'stop' }));
                }
            }
        }, 200); // 200ms real-time chunk interval pacing
    }

    function handleServerEvent(data) {
        if (data.event === 'transcript') {
            updateTranscriptUI(data);
            if (data.latency_ms) valLatency.textContent = `${data.latency_ms} ms`;
            if (data.rtf) valRtf.textContent = data.rtf;
            if (data.active_legs) valActiveLegs.textContent = data.active_legs;
        } else if (data.event === 'eos') {
            statusBadge.textContent = 'COMPLETED';
            statusBadge.className = 'badge badge-completed';
            stopStreaming();
        }
    }

    function updateTranscriptUI(data) {
        let partialEl = document.getElementById('partialTranscriptLine');
        
        if (data.is_final) {
            if (partialEl) partialEl.remove();
            const finalEl = document.createElement('div');
            finalEl.className = 'transcript-line transcript-final';
            finalEl.textContent = data.text;
            transcriptFeed.appendChild(finalEl);
        } else {
            if (!partialEl) {
                partialEl = document.createElement('div');
                partialEl.id = 'partialTranscriptLine';
                partialEl.className = 'transcript-line transcript-partial';
                transcriptFeed.appendChild(partialEl);
            }
            partialEl.textContent = data.text;
        }
        transcriptFeed.scrollTop = transcriptFeed.scrollHeight;
    }

    function stopStreaming() {
        isStreaming = false;
        if (streamTimer) clearInterval(streamTimer);
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
        btnStart.disabled = false;
        btnStop.disabled = true;
        modelSelect.disabled = false;
        langSelect.disabled = false;
    }

    function resetApp() {
        stopStreaming();
        selectedFile = null;
        selectedAudioBytes = null;
        audioFileInput.value = '';
        fileInfoText.textContent = 'No file selected';
        btnStart.disabled = true;
        btnStop.disabled = true;
        statusBadge.textContent = 'DISCONNECTED';
        statusBadge.className = 'badge badge-disconnected';
        transcriptFeed.innerHTML = '<div class="placeholder-text">Load a WAV file and click "Start Stream" to simulate a real-time call leg transcription...</div>';
        chunkCountBadge.textContent = '0 chunks';
        valLatency.textContent = '--';
        valRtf.textContent = '--';
        valActiveLegs.textContent = '0';
        valAudioDuration.textContent = '0.0s';
    }
});

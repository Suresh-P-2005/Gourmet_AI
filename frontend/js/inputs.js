// Global state variables for inputs
let isDetecting = false;


function initInputMethods() {
    $$('.input-method-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const method = btn.dataset.method;
            switchInputMethod(method);
        });
    });
}

function switchInputMethod(method) {
    currentMethod = method;

    // Update tab buttons
    $$('.input-method-btn').forEach(b => b.classList.remove('active'));
    $(`.input-method-btn[data-method="${method}"]`).classList.add('active');

    // Update panels
    $$('.input-panel').forEach(p => p.classList.remove('active'));
    $(`#panel-${method}`).classList.add('active');

    // Stop camera if switching away
    if (method !== 'camera' && mediaStream) {
        stopCamera();
    }

    // Stop voice if switching away
    if (method !== 'voice' && isRecording) {
        stopVoiceRecording();
    }
}

function initVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        $('#voiceBtn').disabled = true;
        $('#voiceStatus').textContent = 'Voice input not supported in this browser.';
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = $('#ingredientsInput');
        if (input.value.trim()) {
            input.value += ', ' + transcript;
        } else {
            input.value = transcript;
        }
        $('#voiceStatus').textContent = '✅ Ingredients added!';
        showToast('Voice input captured!', 'success');
        setTimeout(() => { $('#voiceStatus').textContent = ''; }, 2500);
    };

    recognition.onerror = (event) => {
        console.error('Speech error:', event.error);
        stopVoiceRecording();
        $('#voiceStatus').textContent = 'Error: ' + event.error;
    };

    recognition.onend = () => {
        stopVoiceRecording();
    };

    $('#voiceBtn').addEventListener('click', toggleVoiceRecording);
}

function toggleVoiceRecording() {
    if (isRecording) {
        stopVoiceRecording();
    } else {
        startVoiceRecording();
    }
}

function startVoiceRecording() {
    if (!recognition) return;
    try {
        recognition.start();
        isRecording = true;
        $('#voiceBtn').classList.add('recording');
        $('#voiceStatus').textContent = '🎧 Listening... speak your ingredients';
    } catch (err) {
        console.error('Voice start error:', err);
    }
}

function stopVoiceRecording() {
    if (recognition && isRecording) {
        try { recognition.stop(); } catch (e) { /* ignore */ }
    }
    isRecording = false;
    $('#voiceBtn').classList.remove('recording');
    if ($('#voiceStatus').textContent.includes('Listening')) {
        $('#voiceStatus').textContent = '';
    }
}

function initCamera() {
    $('#cameraStartBtn').addEventListener('click', startCamera);
    $('#cameraCaptureBtn').addEventListener('click', captureAndDetect);
    $('#cameraStopBtn').addEventListener('click', stopCamera);
}

async function startCamera() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
        });

        const video = $('#cameraVideo');
        video.srcObject = mediaStream;
        video.style.display = 'block';
        await video.play();

        $('#cameraPlaceholder').style.display = 'none';
        $('#cameraStartBtn').style.display = 'none';
        $('#cameraCaptureBtn').style.display = 'inline-flex';
        $('#cameraStopBtn').style.display = 'inline-flex';
    } catch (err) {
        console.error('Camera error:', err);
        showToast('Unable to access camera. Please check permissions.', 'error');
    }
}

function stopCamera() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }

    const video = $('#cameraVideo');
    video.srcObject = null;
    video.style.display = 'none';

    $('#cameraPlaceholder').style.display = 'flex';
    $('#cameraStartBtn').style.display = 'inline-flex';
    $('#cameraCaptureBtn').style.display = 'none';
    $('#cameraStopBtn').style.display = 'none';
}

async function captureAndDetect() {
    if (isDetecting) return;
    
    const video = $('#cameraVideo');
    if (!video.srcObject) {
        showToast('Camera is not active.', 'error');
        return;
    }

    isDetecting = true;
    $('#cameraCaptureBtn').disabled = true;

    // Capture frame to canvas
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.85);

    // Show loading
    showToast('Analyzing image for ingredients...', 'info');

    try {
        let response;
        let data;
        let maxRetries = 3;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            response = await fetch(`${API_BASE}/api/vision/detect`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData }),
            });

            data = await response.json();

            if (response.status === 429 && attempt < maxRetries) {
                const waitTime = Math.pow(2, attempt) * 1000; // 2s, 4s backoff
                showToast(`Quota exceeded. Retrying in ${waitTime / 1000}s...`, 'info', waitTime);
                await new Promise(resolve => setTimeout(resolve, waitTime));
                continue;
            }
            break;
        }

        if (!response.ok) {
            throw new Error(data.detail || 'Detection failed');
        }

        if (data.success && data.detected_ingredients && data.detected_ingredients.length > 0) {
            // Show detected ingredients
            showDetectedIngredients(data.detected_ingredients);

            // Auto-fill the ingredients input
            const input = $('#ingredientsInput');
            const detected = data.detected_ingredients.join(', ');
            input.value = input.value.trim()
                ? input.value + ', ' + detected
                : detected;

            // Switch to type tab to show the filled input
            switchInputMethod('type');

            showToast(`Detected ${data.detected_ingredients.length} ingredients! 📸`, 'success');
        } else {
            showToast('No ingredients detected. Try with a clearer image.', 'error');
        }
    } catch (err) {
        console.error('Detection error:', err);
        showToast(err.message || 'Failed to detect ingredients.', 'error');
    } finally {
        $('#cameraCaptureBtn').disabled = false;
        isDetecting = false;
    }
}

function showDetectedIngredients(ingredients) {
    const box = $('#detectedBox');
    const tagsContainer = box.querySelector('.detected-tags');
    tagsContainer.innerHTML = '';

    ingredients.forEach(ing => {
        const tag = document.createElement('span');
        tag.className = 'detected-tag';
        tag.textContent = ing;
        tagsContainer.appendChild(tag);
    });

    box.classList.add('visible');
}


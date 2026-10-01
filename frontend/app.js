/**
 * Gourmet AI Recipe Generator — Frontend Application
 * 
 * Features:
 * - Recipe generation via Gemini AI
 * - Camera-based ingredient detection
 * - Voice input via Web Speech API
 * - Dark mode with localStorage persistence
 * - Recipe save / history
 * - Toast notifications
 */

// ── API Base URL ──────────────────────────────────────────────────────────────
const API_BASE = '';

// ── DOM Elements ──────────────────────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ── State ─────────────────────────────────────────────────────────────────────
let currentMethod = 'type'; // 'type' | 'voice' | 'camera'
let mediaStream = null;
let isRecording = false;
let recognition = null;

// ══════════════════════════════════════════════════════════════════════════════
//  INITIALIZATION
// ══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initInputMethods();
    initRecipeForm();
    initVoiceInput();
    initCamera();
    loadRecipeHistory();
});

// ══════════════════════════════════════════════════════════════════════════════
//  THEME TOGGLE (Dark / Light Mode)
// ══════════════════════════════════════════════════════════════════════════════

function initThemeToggle() {
    const toggle = $('#themeToggle');
    const saved = localStorage.getItem('theme') || 'light';

    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);

    toggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon(next);
    });
}

function updateThemeIcon(theme) {
    const toggle = $('#themeToggle');
    toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    toggle.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
}

// ══════════════════════════════════════════════════════════════════════════════
//  INPUT METHOD TABS (Type / Voice / Camera)
// ══════════════════════════════════════════════════════════════════════════════

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

// ══════════════════════════════════════════════════════════════════════════════
//  RECIPE FORM — Generate Recipe
// ══════════════════════════════════════════════════════════════════════════════

function initRecipeForm() {
    $('#recipeForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await generateRecipe();
    });
}

async function generateRecipe() {
    const ingredients = $('#ingredientsInput').value.trim();
    const cuisine = $('#cuisineInput').value.trim();
    const dietary = $('#dietaryInput').value.trim();

    if (!ingredients) {
        showToast('Please enter at least one ingredient.', 'error');
        $('#ingredientsInput').focus();
        return;
    }

    // Show loading, hide previous results
    showLoading(true);
    hideRecipeResult();

    try {
        const response = await fetch(`${API_BASE}/api/recipe/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ingredients, cuisine, dietary }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || data.error || 'Failed to generate recipe');
        }

        if (data.success && data.recipe) {
            displayRecipe(data.recipe);
            showToast('Recipe generated successfully! 🎉', 'success');
        } else {
            throw new Error('Unexpected response format');
        }
    } catch (err) {
        console.error('Recipe generation error:', err);
        showToast(err.message || 'Failed to generate recipe. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// ══════════════════════════════════════════════════════════════════════════════
//  DISPLAY RECIPE
// ══════════════════════════════════════════════════════════════════════════════

function displayRecipe(recipe) {
    // Title
    $('#recipeTitle').textContent = recipe.title || 'Untitled Recipe';

    // Meta tags
    const metaContainer = $('#recipeMeta');
    metaContainer.innerHTML = '';
    if (recipe.cuisine) addMetaTag(metaContainer, '🌍', recipe.cuisine);
    if (recipe.dietary) addMetaTag(metaContainer, '🥗', recipe.dietary);
    if (recipe.prep_time) addMetaTag(metaContainer, '⏱️', recipe.prep_time);
    if (recipe.cook_time) addMetaTag(metaContainer, '🔥', recipe.cook_time);
    if (recipe.servings) addMetaTag(metaContainer, '🍽️', recipe.servings);

    // Ingredients
    const ingredientsList = $('#ingredientsList');
    ingredientsList.innerHTML = '';
    (recipe.ingredients || []).forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        ingredientsList.appendChild(li);
    });

    // Instructions
    const instructionsList = $('#instructionsList');
    instructionsList.innerHTML = '';
    (recipe.instructions || []).forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        instructionsList.appendChild(li);
    });

    // Nutrition
    const nutritionSection = $('#nutritionSection');
    if (recipe.nutrition) {
        const grid = $('#nutritionGrid');
        grid.innerHTML = '';
        const fields = [
            { key: 'calories', label: 'Calories', icon: '🔥' },
            { key: 'protein', label: 'Protein', icon: '💪' },
            { key: 'carbs', label: 'Carbs', icon: '🌾' },
            { key: 'fat', label: 'Fat', icon: '🧈' },
            { key: 'fiber', label: 'Fiber', icon: '🥦' },
        ];
        let hasNutrition = false;
        fields.forEach(f => {
            const val = recipe.nutrition[f.key];
            if (val) {
                hasNutrition = true;
                const div = document.createElement('div');
                div.className = 'nutrition-item';
                div.innerHTML = `<span class="nut-value">${val}</span><span class="nut-label">${f.icon} ${f.label}</span>`;
                grid.appendChild(div);
            }
        });
        nutritionSection.style.display = hasNutrition ? 'block' : 'none';
    } else {
        nutritionSection.style.display = 'none';
    }

    // Notes
    const notesSection = $('#notesSection');
    if (recipe.notes) {
        $('#recipeNotes').textContent = recipe.notes;
        notesSection.style.display = 'block';
    } else {
        notesSection.style.display = 'none';
    }

    // Suggestions
    const suggestionsSection = $('#suggestionsSection');
    if (recipe.suggestions) {
        $('#recipeSuggestions').textContent = recipe.suggestions;
        suggestionsSection.style.display = 'block';
    } else {
        suggestionsSection.style.display = 'none';
    }

    // Store current recipe for saving
    window._currentRecipe = recipe;

    // Show result
    showRecipeResult();
}

function addMetaTag(container, icon, text) {
    const span = document.createElement('span');
    span.className = 'meta-tag';
    span.innerHTML = `${icon} ${text}`;
    container.appendChild(span);
}

function showRecipeResult() {
    const el = $('#recipeResult');
    el.classList.add('visible');
    el.style.display = 'block';
    setTimeout(() => {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function hideRecipeResult() {
    const el = $('#recipeResult');
    el.classList.remove('visible');
    el.style.display = 'none';
}

// ══════════════════════════════════════════════════════════════════════════════
//  SAVE & HISTORY
// ══════════════════════════════════════════════════════════════════════════════

async function saveCurrentRecipe() {
    const recipe = window._currentRecipe;
    if (!recipe) {
        showToast('No recipe to save.', 'error');
        return;
    }

    try {
        const payload = {
            title: recipe.title,
            cuisine: recipe.cuisine || '',
            dietary: recipe.dietary || '',
            ingredients: recipe.ingredients || [],
            instructions: recipe.instructions || [],
            notes: recipe.notes || '',
            nutrition: recipe.nutrition || {},
            suggestions: recipe.suggestions || '',
        };

        const response = await fetch(`${API_BASE}/api/recipe/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        if (data.success) {
            showToast('Recipe saved! 📚', 'success');
            loadRecipeHistory();
        } else {
            throw new Error(data.detail || 'Save failed');
        }
    } catch (err) {
        console.error('Save error:', err);
        showToast('Failed to save recipe.', 'error');
    }
}

async function loadRecipeHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/recipe/history?limit=10`);
        const data = await response.json();

        const container = $('#historyList');
        const section = $('#historySection');

        if (!data.success || !data.recipes || data.recipes.length === 0) {
            container.innerHTML = '<div class="history-empty">No saved recipes yet. Generate and save your first recipe!</div>';
            section.style.display = 'block';
            return;
        }

        container.innerHTML = '';
        data.recipes.forEach(recipe => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `
                <div class="history-item-info" onclick="viewSavedRecipe(${recipe.id}, this)">
                    <h4>${escapeHtml(recipe.title)}</h4>
                    <span>${recipe.cuisine || 'Any'} · ${recipe.created_at ? new Date(recipe.created_at).toLocaleDateString() : ''}</span>
                </div>
                <button class="delete-btn" onclick="deleteSavedRecipe(${recipe.id}, event)" title="Delete recipe">🗑️</button>
            `;

            // Store recipe data on element for quick access
            item._recipe = recipe;
            container.appendChild(item);
        });

        section.style.display = 'block';
    } catch (err) {
        console.error('History load error:', err);
    }
}

function viewSavedRecipe(id, element) {
    const item = element.closest('.history-item');
    if (item && item._recipe) {
        displayRecipe(item._recipe);
    }
}

async function deleteSavedRecipe(id, event) {
    event.stopPropagation();
    if (!confirm('Delete this recipe?')) return;

    try {
        const response = await fetch(`${API_BASE}/api/recipe/${id}`, { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
            showToast('Recipe deleted.', 'info');
            loadRecipeHistory();
        }
    } catch (err) {
        showToast('Failed to delete recipe.', 'error');
    }
}

// ══════════════════════════════════════════════════════════════════════════════
//  VOICE INPUT
// ══════════════════════════════════════════════════════════════════════════════

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

// ══════════════════════════════════════════════════════════════════════════════
//  CAMERA INGREDIENT DETECTION
// ══════════════════════════════════════════════════════════════════════════════

let isDetecting = false;

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

// ══════════════════════════════════════════════════════════════════════════════
//  TOAST NOTIFICATIONS
// ══════════════════════════════════════════════════════════════════════════════

function showToast(message, type = 'info', duration = 3500) {
    const container = $('#toastContainer');

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ══════════════════════════════════════════════════════════════════════════════
//  LOADING STATES
// ══════════════════════════════════════════════════════════════════════════════

function showLoading(show) {
    const overlay = $('#loadingOverlay');
    const submitBtn = $('#submitBtn');

    if (show) {
        overlay.classList.add('visible');
        overlay.style.display = 'block';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner" style="width:20px;height:20px;border-width:3px;margin:0;"></span> Generating...';
    } else {
        overlay.classList.remove('visible');
        overlay.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '✨ Generate Recipe';
    }
}

// ══════════════════════════════════════════════════════════════════════════════
//  UTILITIES
// ══════════════════════════════════════════════════════════════════════════════

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

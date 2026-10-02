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

const originalFetch = window.fetch;
window.fetch = function(input, init) {
    if (!init) init = {};
    init.credentials = 'include';
    return originalFetch.call(this, input, init);
};


// ── DOM Elements ──────────────────────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ── State ─────────────────────────────────────────────────────────────────────
let currentMethod = 'type'; // 'type' | 'voice' | 'camera'
let mediaStream = null;
let isRecording = false;
let recognition = null;

let pendingSignupEmail = null;

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initInputMethods();
    initRecipeForm();
    initVoiceInput();
    initCamera();
    checkAuthStatus();
    initGoogleAuth();
});


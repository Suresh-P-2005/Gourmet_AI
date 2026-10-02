/**
 * Global State Manager using Vanilla JS Proxies
 * Enables reactive data binding without a framework like React or Vue.
 */

// Define the initial state
const initialState = {
    user: null,         // User profile { id, username, email, is_admin, avatar }
    recipes: [],        // Community feed
    vault: [],          // User's saved recipes
    isLoading: false,   // Global loading state
    currentRecipe: null // Recipe currently being generated or viewed
};

// Listeners array to trigger DOM updates when state changes
const listeners = [];

// Create the Proxy
window.appState = new Proxy(initialState, {
    set(target, property, value) {
        // Only update and trigger listeners if the value actually changed
        if (target[property] !== value) {
            target[property] = value;
            // Notify all registered listeners
            listeners.forEach(listener => listener(property, value, target));
        }
        return true; // Indicate success
    }
});

/**
 * Register a listener for state changes.
 * @param {Function} callback - Called with (property, newValue, fullState) whenever a property changes.
 */
window.onStateChange = function(callback) {
    listeners.push(callback);
};

// Example DOM Bindings
window.onStateChange((prop, value) => {
    // Global Loading State
    if (prop === 'isLoading') {
        const overlay = document.querySelector('#loadingOverlay'); // Assuming there's a loading overlay or use showLoading
        if (typeof showLoading === 'function') {
            showLoading(value);
        }
    }
    
    // User Profile
    if (prop === 'user') {
        if (value) {
            const avatarFallback = document.querySelector('#navAvatarFallback');
            const avatarImg = document.querySelector('#navAvatarImg');
            
            if (value.avatar && avatarImg) {
                avatarImg.src = value.avatar;
                avatarImg.style.display = 'block';
                if (avatarFallback) avatarFallback.style.display = 'none';
            }
            
            // Admin controls
            if (value.is_admin) {
                if (document.querySelector('#navAdmin')) document.querySelector('#navAdmin').style.display = 'inline-block';
                if (document.querySelector('#mobileNavAdmin')) document.querySelector('#mobileNavAdmin').style.display = 'block';
            }
        }
    }
    
    // Current Recipe
    if (prop === 'currentRecipe' && value) {
        if (typeof displayRecipe === 'function') {
            displayRecipe(value);
        }
    }
});

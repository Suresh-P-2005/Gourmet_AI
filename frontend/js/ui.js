function initThemeToggle() {
    const toggles = document.querySelectorAll('.theme-toggle');
    const saved = localStorage.getItem('theme') || 'light';

    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);

    toggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateThemeIcon(next);
        });
    });
}

function updateThemeIcon(theme) {
    const toggles = document.querySelectorAll('.theme-toggle');
    toggles.forEach(toggle => {
        toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        toggle.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    });
}

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

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function switchView(viewId) {
    const views = ['generateView', 'communityView', 'vaultView', 'adminView', 'accountView'];
    views.forEach(v => {
        const el = $('#' + v);
        if (el) el.style.display = (v === viewId) ? 'block' : 'none';
    });

    // Update active state in nav buttons
    const navButtons = {
        'generateView': ['#navGenerate', '#mobileNavGenerate'],
        'communityView': ['#navCommunity', '#mobileNavCommunity'],
        'vaultView': ['#navVault', '#mobileNavVault'],
        'adminView': ['#navAdmin', '#mobileNavAdmin'],
        'accountView': ['#mobileNavAccount']
    };
    
    // Remove active class from all
    Object.values(navButtons).flat().forEach(selector => {
        const btn = $(selector);
        if (btn) btn.classList.remove('active');
    });

    // Add active class to the selected ones
    if (navButtons[viewId]) {
        navButtons[viewId].forEach(selector => {
            const activeBtn = $(selector);
            if (activeBtn) activeBtn.classList.add('active');
        });
    }
}

function toggleMobileNav() {
    const burger = $('#navBurger');
    const overlay = $('#navOverlay');
    const mobileMenu = $('#navMobile');

    if (!burger || !overlay || !mobileMenu) return;

    burger.classList.toggle('is-open');
    overlay.classList.toggle('is-open');
    mobileMenu.classList.toggle('is-open');
}


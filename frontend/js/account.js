// ── Account Profile Features ────────────────────────────────────────────────

async function loadAccountProfile() {
    try {
        const res = await fetch(`${API_BASE}/api/user/profile`, {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        if (res.ok) {
            // Update Text Details
            $('#profileUsernameDisplay').textContent = escapeHtml(data.user.username);
            $('#profileEmailDisplay').textContent = escapeHtml(data.user.email);
            $('#profileRoleBadge').textContent = data.user.is_admin ? 'Admin' : 'Standard Member';
            
            // Update Stats
            $('#statTotalRecipes').textContent = data.stats.total_generated;
            $('#statSavedRecipes').textContent = data.stats.total_saved;
            
            // Update Avatars (Top Nav and Profile Header)
            if (data.user.avatar) {
                updateAvatarUI(data.user.avatar);
            }
        }
    } catch (err) {
        console.error("Failed to load profile:", err);
    }
}

function updateAvatarUI(avatarDataUrl) {
    // Profile Page Avatar
    $('#profileAvatarLg').src = avatarDataUrl;
    $('#profileAvatarLg').style.display = 'block';
    $('#profileAvatarFallbackLg').style.display = 'none';
    
    // Top Nav Avatar
    $('#navAvatarImg').src = avatarDataUrl;
    $('#navAvatarImg').style.display = 'block';
    $('#navAvatarFallback').style.display = 'none';
}

function handleAvatarUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        showToast('Please upload a valid image file', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = async (e) => {
        const base64Image = e.target.result;
        
        // Optimistically update UI
        updateAvatarUI(base64Image);
        
        try {
            showToast('Saving profile picture...', 'info');
            const res = await fetch(`${API_BASE}/api/user/avatar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify({ avatar_base64: base64Image })
            });
            
            if (res.ok) {
                showToast('Profile picture updated successfully!', 'success');
            } else {
                showToast('Failed to save profile picture', 'error');
            }
        } catch (err) {
            showToast('Error uploading picture', 'error');
        }
    };
    
    // Read the file as base64
    reader.readAsDataURL(file);
}

async function loadAdminUsers() {
    try {
        const res = await fetch(`${API_BASE}/api/admin/users`, {
            headers: getAuthHeaders()
        });
        
        if (!res.ok) {
            showToast("Failed to load admin users. Access denied.", "error");
            switchView('generateView');
            return;
        }
        
        const data = await res.json();
        const tbody = $('#adminUsersTable');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        data.users.forEach(u => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid rgba(255,255,255,0.1)';
            
            const roleBtnText = u.is_admin ? "Demote" : "Make Admin";
            const roleBtnClass = u.is_admin ? "btn-secondary" : "btn-primary";
            
            tr.innerHTML = `
                <td style="padding: 10px;">${u.id}</td>
                <td style="padding: 10px; font-weight: bold;">${escapeHtml(u.username)}</td>
                <td style="padding: 10px;">${escapeHtml(u.email)}</td>
                <td style="padding: 10px;">${u.is_verified ? '✅ Yes' : '⏳ No'}</td>
                <td style="padding: 10px;">${escapeHtml(u.auth_provider)}</td>
                <td style="padding: 10px;">${u.recipe_count}</td>
                <td style="padding: 10px;">
                    <span style="display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; background: ${u.is_admin ? 'rgba(168,85,247,0.3)' : 'rgba(255,255,255,0.1)'}; color: ${u.is_admin ? '#d8b4fe' : 'var(--text)'};">
                        ${u.is_admin ? 'Admin' : 'User'}
                    </span>
                </td>
                <td style="padding: 10px;">
                    <button class="glass-btn btn ${roleBtnClass}" style="padding: 5px 10px; font-size: 0.8em; margin-right: 5px;" onclick="toggleAdminRole(${u.id})">${roleBtnText}</button>
                    <button class="glass-btn btn btn-secondary" style="padding: 5px 10px; font-size: 0.8em; color: #f87171;" onclick="deleteUser(${u.id}, '${escapeHtml(u.username)}')">🗑️</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        showToast("Error loading users", "error");
    }
}

async function toggleAdminRole(userId) {
    if (!confirm("Are you sure you want to change this user's admin privileges?")) return;
    
    try {
        const res = await fetch(`${API_BASE}/api/admin/users/${userId}/toggle-admin`, {
            method: 'PUT',
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast(data.message, "success");
            loadAdminUsers();
        } else {
            showToast(data.detail || "Failed to change role", "error");
        }
    } catch (err) {
        showToast("Error updating role", "error");
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`CRITICAL WARNING: Are you sure you want to permanently delete user "${username}" and ALL their recipes? This cannot be undone.`)) return;
    
    try {
        const res = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        if (res.ok) {
            showToast(data.message, "success");
            loadAdminUsers();
        } else {
            showToast(data.detail || "Failed to delete user", "error");
        }
    } catch (err) {
        showToast("Error deleting user", "error");
    }
}


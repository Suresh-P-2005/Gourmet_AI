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
            cuisine_type: recipe.cuisine_type || 'Other',
            dietary: recipe.dietary || '',
            ingredients: recipe.ingredients || [],
            instructions: recipe.instructions || [],
            notes: recipe.notes || '',
            nutrition: recipe.nutrition || {},
            suggestions: recipe.suggestions || '',
        };

        const response = await fetch(`${API_BASE}/api/recipe/save`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        if (data.success) {
            showToast('Recipe saved! 📚', 'success');
            loadPersonalVault();
            switchView('vaultView');
        } else {
            throw new Error(data.detail || 'Save failed');
        }
    } catch (err) {
        console.error('Save error:', err);
        showToast('Failed to save recipe.', 'error');
    }
}



async function deleteSavedRecipe(id, event) {
    event.stopPropagation();
    if (!confirm('Delete this recipe?')) return;

    try {
        const response = await fetch(`${API_BASE}/api/recipe/${id}`, { 
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        const data = await response.json();
        if (data.success) {
            showToast('Recipe deleted.', 'info');
            loadPersonalVault();
        }
    } catch (err) {
        showToast('Failed to delete recipe.', 'error');
    }
}

let communityCursor = null;
let vaultCursor = null;
let isFetchingCommunity = false;
let isFetchingVault = false;
let scrollObserver = null;

function setupIntersectionObserver(containerId, fetchMoreCallback) {
    if (scrollObserver) scrollObserver.disconnect();
    
    const container = $('#' + containerId);
    if (!container) return;
    
    // Add a sentinel element at the bottom if it doesn't exist
    let sentinel = $('#' + containerId + '-sentinel');
    if (!sentinel) {
        sentinel = document.createElement('div');
        sentinel.id = containerId + '-sentinel';
        sentinel.style.height = '20px';
        sentinel.style.marginTop = '20px';
        container.parentNode.insertBefore(sentinel, container.nextSibling);
    }
    
    scrollObserver = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
            fetchMoreCallback();
        }
    }, { rootMargin: '100px' });
    
    scrollObserver.observe(sentinel);
}

async function loadCommunityFeed(cuisine = 'All', loadMore = false) {
    if (isFetchingCommunity) return;
    isFetchingCommunity = true;
    
    if (!loadMore) {
        communityCursor = null;
        const grid = $('#communityGrid');
        if (grid) grid.innerHTML = '<div class="loading-spinner" style="width: 30px; height: 30px; margin: 20px auto;"></div>';
    }

    const search = $('#searchCommunity')?.value.trim() || '';
    let url = `${API_BASE}/api/recipe/community?limit=20`;
    if (cuisine !== 'All') url += `&cuisine=${encodeURIComponent(cuisine)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (communityCursor) url += `&cursor=${encodeURIComponent(communityCursor)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();
        if (res.ok) {
            renderRecipeCards(data.recipes, 'communityGrid', false, loadMore);
            communityCursor = data.next_cursor;
            
            if (communityCursor) {
                setupIntersectionObserver('communityGrid', () => loadCommunityFeed(cuisine, true));
            } else if (scrollObserver) {
                scrollObserver.disconnect();
            }
        }
    } catch (err) {
        console.error(err);
    } finally {
        isFetchingCommunity = false;
    }
}

async function loadPersonalVault(loadMore = false) {
    if (!window.appState || !window.appState.user) return checkAuthStatus();
    if (isFetchingVault) return;
    isFetchingVault = true;
    
    if (!loadMore) {
        vaultCursor = null;
        const grid = $('#vaultGrid');
        if (grid) grid.innerHTML = '<div class="loading-spinner" style="width: 30px; height: 30px; margin: 20px auto;"></div>';
    }
    
    let url = `${API_BASE}/api/recipe/vault?limit=20`;
    if (vaultCursor) url += `&cursor=${encodeURIComponent(vaultCursor)}`;
    
    try {
        const res = await fetch(url, {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        if (res.ok) {
            renderRecipeCards(data.recipes, 'vaultGrid', true, loadMore);
            vaultCursor = data.next_cursor;
            
            if (vaultCursor) {
                setupIntersectionObserver('vaultGrid', () => loadPersonalVault(true));
            } else if (scrollObserver) {
                scrollObserver.disconnect();
            }
        } else if (res.status === 401) {
            handleLogout();
        }
    } catch (err) {
        console.error(err);
    } finally {
        isFetchingVault = false;
    }
}

function renderRecipeCards(recipes, containerId, isVault, append = false) {
    const container = $('#' + containerId);
    if (!container) return;
    
    if (!append) {
        container.innerHTML = '';
        if (!recipes || recipes.length === 0) {
            container.innerHTML = '<p>No recipes found.</p>';
            return;
        }
    } else if (!recipes || recipes.length === 0) {
        return;
    }

    recipes.forEach(r => {
        const div = document.createElement('div');
        div.className = 'glass-card';
        div.style.padding = '15px';
        div.style.display = 'flex';
        div.style.flexDirection = 'column';
        div.style.gap = '10px';

        let actionHtml = isVault ? 
            `<button class="glass-btn btn btn-secondary" onclick="deleteSavedRecipe(${r.id}, event)">🗑️ Delete</button>
             <button class="glass-btn btn ${r.is_public ? 'btn-primary' : 'btn-secondary'}" onclick="toggleVisibility(${r.id}, ${!r.is_public})">${r.is_public ? '🌍 Public' : '🔒 Private'}</button>` :
            `<button class="glass-btn btn btn-primary" onclick="bookmarkRecipe(${r.id})">💾 Save to Vault</button>`;

        const contentDiv = document.createElement('div');
        contentDiv.style.cssText = "cursor: pointer; flex-grow: 1; display: flex; flex-direction: column; gap: 10px; padding: 5px; border-radius: 8px; transition: background 0.3s ease;";
        contentDiv.onmouseover = () => contentDiv.style.background = "var(--glass-bg)";
        contentDiv.onmouseout = () => contentDiv.style.background = "transparent";
        contentDiv.onclick = () => {
            displayRecipe(r);
            switchView('generateView');
        };
        contentDiv.innerHTML = `
            <h3 style="margin:0">${escapeHtml(r.title)}</h3>
            <span style="font-size: 0.8em; opacity: 0.8;">${escapeHtml(r.cuisine_type || 'Other')}</span>
            <p style="font-size: 0.9em; margin: 0; flex-grow: 1;">${escapeHtml((r.ingredients || []).slice(0, 3).join(', '))}...</p>
        `;

        const actionsDiv = document.createElement('div');
        actionsDiv.style.cssText = "display: flex; gap: 10px; flex-wrap: wrap; margin-top: auto;";
        actionsDiv.innerHTML = actionHtml;

        div.appendChild(contentDiv);
        div.appendChild(actionsDiv);
        container.appendChild(div);
    });
}

async function bookmarkRecipe(id) {
    if (!window.appState || !window.appState.user) {
        showToast("Please login first", "error");
        checkAuthStatus();
        return;
    }
    try {
        const res = await fetch(`${API_BASE}/api/recipe/${id}/save`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        if (res.ok) showToast("Recipe bookmarked to your Vault!", "success");
        else showToast("Failed to bookmark", "error");
    } catch (err) {
        console.error(err);
    }
}

async function toggleVisibility(id, makePublic) {
    try {
        const res = await fetch(`${API_BASE}/api/recipe/${id}/visibility?is_public=${makePublic}`, {
            method: 'PUT',
            headers: getAuthHeaders()
        });
        if (res.ok) {
            showToast(`Recipe is now ${makePublic ? 'public' : 'private'}`, 'success');
            loadPersonalVault();
        }
    } catch (err) {
        console.error(err);
    }
}


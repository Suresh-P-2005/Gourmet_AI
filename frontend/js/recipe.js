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
    window.appState.isLoading = true;
    hideRecipeResult();

    try {
        const response = await fetch(`${API_BASE}/api/recipe/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ingredients, cuisine, dietary }),
        });

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || data.error || 'Failed to generate recipe');
        }

        // Hide loading overlay but keep state loading true to prevent other actions
        $('#loadingOverlay').classList.remove('active');
        $('#streamResult').style.display = 'block';
        $('#streamText').textContent = '';
        
        // Scroll to stream text
        setTimeout(() => {
            $('#streamResult').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let fullJsonText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            fullJsonText += chunk;
            $('#streamText').textContent = fullJsonText;
            
            const pre = $('#streamText');
            pre.scrollTop = pre.scrollHeight;
        }

        $('#streamResult').style.display = 'none';

        try {
            const recipeData = JSON.parse(fullJsonText);
            if (recipeData.error) throw new Error(recipeData.error);
            window.appState.currentRecipe = recipeData;
            showToast('Recipe generated successfully! 🎉', 'success');
            displayRecipe(recipeData);
        } catch (e) {
            if (e.message.includes("Streaming failed")) {
                throw e; // Preserve the backend error message
            }
            throw new Error('Failed to parse final recipe. AI may have returned invalid format.');
        }

    } catch (err) {
        console.error('Recipe generation error:', err);
        showToast(err.message || 'Failed to generate recipe. Please try again.', 'error');
        $('#streamResult').style.display = 'none';
    } finally {
        window.appState.isLoading = false;
    }
}

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
    
    const stream = $('#streamResult');
    if (stream) stream.style.display = 'none';
}


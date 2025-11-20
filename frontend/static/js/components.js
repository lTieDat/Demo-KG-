// UI Components

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');
    
    // Set icon based on type
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toastIcon.textContent = icons[type] || icons.info;
    toastMessage.textContent = message;
    
    // Show toast
    toast.classList.remove('translate-y-full');
    toast.classList.add('translate-y-0');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('translate-y-0');
        toast.classList.add('translate-y-full');
    }, 3000);
}

function showLoading(show = true) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('hidden');
        spinner.classList.add('fade-in');
    } else {
        spinner.classList.add('hidden');
    }
}

function createRecommendationCard(rec) {
    return `
        <div class="recommendation-card bg-white rounded-lg p-6 shadow-md border border-gray-200 hover:border-blue-300">
            <div class="border-b border-gray-200 pb-2 mb-3">
                <h3 class="text-lg font-bold text-blue-600">#${rec.rank} Bài tập ${rec.item_id}</h3>
            </div>
            <p class="font-semibold text-gray-800 mb-2">${rec.title}</p>
            <div class="space-y-1 text-sm text-gray-600">
                <p><span class="font-medium">Chủ đề:</span> ${rec.topic}</p>
                <p><span class="font-medium">Chủ đề phụ:</span> ${rec.sub_topic}</p>
                <p><span class="font-medium">Độ khó:</span> ${rec.difficulty}</p>
                <p class="text-xs text-gray-500 mt-2">Score: ${rec.score.toFixed(4)}</p>
            </div>
        </div>
    `;
}

function renderRecommendations(recommendations) {
    const grid = document.getElementById('recommendationsGrid');
    const section = document.getElementById('recommendationsSection');
    
    if (!recommendations || recommendations.length === 0) {
        section.classList.add('hidden');
        return;
    }
    
    grid.innerHTML = recommendations.map(rec => createRecommendationCard(rec)).join('');
    section.classList.remove('hidden');
    section.classList.add('fade-in');
}

function renderExplanation(explanation) {
    const content = document.getElementById('explanationContent');
    const result = document.getElementById('explanationResult');
    
    // Use marked.js to render markdown
    content.innerHTML = marked.parse(explanation);
    result.classList.remove('hidden');
    result.classList.add('fade-in');
}

function clearExplanation() {
    const result = document.getElementById('explanationResult');
    result.classList.add('hidden');
}

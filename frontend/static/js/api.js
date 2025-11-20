// API Client
const API_BASE = '';  // Same origin

const api = {
    // Models
    async listModels() {
        const response = await fetch(`${API_BASE}/api/models/list`);
        if (!response.ok) throw new Error('Failed to fetch models');
        return response.json();
    },

    async loadModel(modelPath) {
        const response = await fetch(`${API_BASE}/api/models/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_path: modelPath })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to load model');
        }
        return response.json();
    },

    async getCurrentModel() {
        const response = await fetch(`${API_BASE}/api/models/current`);
        if (!response.ok) throw new Error('No model loaded');
        return response.json();
    },

    // Students
    async listStudents(search = '') {
        const url = new URL(`${API_BASE}/api/recommendations/students`, window.location.origin);
        if (search) url.searchParams.append('search', search);
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch students');
        return response.json();
    },

    async getStudent(studentCode) {
        const response = await fetch(`${API_BASE}/api/recommendations/students/${studentCode}`);
        if (!response.ok) throw new Error('Student not found');
        return response.json();
    },

    // Recommendations
    async generateRecommendations(userId, topk = 10) {
        const response = await fetch(`${API_BASE}/api/recommendations/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, topk })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate recommendations');
        }
        return response.json();
    },

    // AI Explainer
    async generateExplanation(studentCode, recommendations, service = 'mistral', modelName = 'mistral-small-latest') {
        const response = await fetch(`${API_BASE}/api/explainer/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_code: studentCode,
                recommendations,
                service,
                model_name: modelName
            })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate explanation');
        }
        return response.json();
    }
};

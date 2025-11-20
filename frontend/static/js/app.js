// Main Application Logic

// State
let currentModel = null;
let currentStudent = null;
let currentRecommendations = null;
let allStudents = [];

// DOM Elements
const modelSelect = document.getElementById('modelSelect');
const loadModelBtn = document.getElementById('loadModelBtn');
const modelInfo = document.getElementById('modelInfo');
const studentSearch = document.getElementById('studentSearch');
const studentSelect = document.getElementById('studentSelect');
const selectedStudentInfo = document.getElementById('selectedStudentInfo');
const topkSelect = document.getElementById('topkSelect');
const generateBtn = document.getElementById('generateBtn');
const explainerSection = document.getElementById('explainerSection');
const explainBtn = document.getElementById('explainBtn');
const clearExplanationBtn = document.getElementById('clearExplanationBtn');
const aiService = document.getElementById('aiService');
const aiModel = document.getElementById('aiModel');

// Initialize
async function init() {
    try {
        // Load available models
        const data = await api.listModels();
        populateModelSelect(data.compatible);
        
        // Set up event listeners
        setupEventListeners();
    } catch (error) {
        showToast('Lỗi khi khởi tạo: ' + error.message, 'error');
    }
}

function populateModelSelect(models) {
    modelSelect.innerHTML = '<option value="">Chọn model...</option>';
    models.forEach(({ filename, info }) => {
        const option = document.createElement('option');
        option.value = filename;
        option.textContent = `${filename} (Epoch: ${info.epoch}, Score: ${info.score})`;
        modelSelect.appendChild(option);
    });
}

function setupEventListeners() {
    // Model loading
    loadModelBtn.addEventListener('click', handleLoadModel);
    
    // Student search
    studentSearch.addEventListener('input', handleStudentSearch);
    studentSelect.addEventListener('change', handleStudentSelect);
    
    // Generate recommendations
    generateBtn.addEventListener('click', handleGenerateRecommendations);
    
    // AI Explainer
    explainBtn.addEventListener('click', handleGenerateExplanation);
    clearExplanationBtn.addEventListener('click', clearExplanation);
    
    // AI Service change
    aiService.addEventListener('change', handleAIServiceChange);
}

async function handleLoadModel() {
    const modelPath = modelSelect.value;
    if (!modelPath) {
        showToast('Vui lòng chọn model', 'warning');
        return;
    }
    
    try {
        loadModelBtn.disabled = true;
        loadModelBtn.textContent = 'Đang load...';
        
        const data = await api.loadModel(modelPath);
        currentModel = data;
        
        // Update UI
        document.getElementById('modelEpoch').textContent = data.model_info.epoch;
        document.getElementById('modelScore').textContent = data.model_info.score;
        document.getElementById('modelUsers').textContent = data.dataset_info.user_num.toLocaleString();
        document.getElementById('modelItems').textContent = data.dataset_info.item_num.toLocaleString();
        modelInfo.classList.remove('hidden');
        
        // Load students
        await loadStudents();
        
        showToast('Model loaded thành công!', 'success');
    } catch (error) {
        showToast('Lỗi: ' + error.message, 'error');
    } finally {
        loadModelBtn.disabled = false;
        loadModelBtn.textContent = 'Load Model';
    }
}

async function loadStudents() {
    try {
        const data = await api.listStudents();
        allStudents = data.students;
        populateStudentSelect(allStudents);
    } catch (error) {
        showToast('Lỗi khi tải danh sách sinh viên: ' + error.message, 'error');
    }
}

function populateStudentSelect(students) {
    studentSelect.innerHTML = '<option value="">Chọn sinh viên...</option>';
    students.forEach(({ student_code, user_id }) => {
        const option = document.createElement('option');
        option.value = user_id;
        option.dataset.code = student_code;
        option.textContent = student_code;
        studentSelect.appendChild(option);
    });
}

function handleStudentSearch(e) {
    const search = e.target.value.trim();
    if (search.length === 0) {
        populateStudentSelect(allStudents);
        return;
    }
    
    const filtered = allStudents.filter(s => 
        s.student_code.toUpperCase().includes(search.toUpperCase())
    );
    populateStudentSelect(filtered);
    
    if (filtered.length > 0) {
        showToast(`Tìm thấy ${filtered.length} sinh viên`, 'success');
    } else {
        showToast('Không tìm thấy sinh viên', 'warning');
    }
}

function handleStudentSelect(e) {
    const userId = parseInt(e.target.value);
    const studentCode = e.target.options[e.target.selectedIndex]?.dataset.code;
    
    if (!userId || !studentCode) {
        selectedStudentInfo.classList.add('hidden');
        currentStudent = null;
        return;
    }
    
    currentStudent = { user_id: userId, student_code: studentCode };
    
    document.getElementById('selectedStudentCode').textContent = studentCode;
    document.getElementById('selectedUserId').textContent = userId;
    selectedStudentInfo.classList.remove('hidden');
}

async function handleGenerateRecommendations() {
    if (!currentStudent) {
        showToast('Vui lòng chọn sinh viên', 'warning');
        return;
    }
    
    try {
        generateBtn.disabled = true;
        showLoading(true);
        
        const topk = parseInt(topkSelect.value);
        const data = await api.generateRecommendations(currentStudent.user_id, topk);
        
        currentRecommendations = data.recommendations;
        renderRecommendations(currentRecommendations);
        
        // Show explainer section
        explainerSection.classList.remove('hidden');
        
        showToast(`Đã tạo ${topk} gợi ý cho ${currentStudent.student_code}`, 'success');
    } catch (error) {
        showToast('Lỗi: ' + error.message, 'error');
    } finally {
        generateBtn.disabled = false;
        showLoading(false);
    }
}

async function handleGenerateExplanation() {
    if (!currentRecommendations || !currentStudent) {
        showToast('Vui lòng tạo gợi ý trước', 'warning');
        return;
    }
    
    try {
        explainBtn.disabled = true;
        explainBtn.textContent = 'Đang tạo...';
        
        const service = aiService.value;
        const model = aiModel.value;
        
        const data = await api.generateExplanation(
            currentStudent.student_code,
            currentRecommendations,
            service,
            model
        );
        
        renderExplanation(data.explanation);
        showToast('Giải thích đã được tạo', 'success');
    } catch (error) {
        showToast('Lỗi: ' + error.message, 'error');
    } finally {
        explainBtn.disabled = false;
        explainBtn.textContent = 'Tạo giải thích';
    }
}

function handleAIServiceChange(e) {
    const service = e.target.value;
    const modelSelect = document.getElementById('aiModel');
    
    if (service === 'mistral') {
        modelSelect.innerHTML = `
            <option value="mistral-small-latest">Mistral Small</option>
            <option value="mistral-medium-latest">Mistral Medium</option>
            <option value="mistral-large-latest">Mistral Large</option>
        `;
    } else {
        modelSelect.innerHTML = `
            <option value="mistral">Mistral</option>
            <option value="llama2">Llama 2</option>
            <option value="phi3:mini">Phi-3 Mini</option>
            <option value="codellama">Code Llama</option>
        `;
    }
}

// Start the app
init();

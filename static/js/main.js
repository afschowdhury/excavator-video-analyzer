// Main JavaScript for Video Analyzer Web App

// State management
let state = {
    analyzerType: 'gemini',
    selectedPrompt: null,
    gpt5Model: 'gpt-4o',
    fps: 3,
    maxFrames: null,
    videoSource: 'url',
    videoUrl: '',
    videoPath: '',
    videoId: null,
    isAnalyzing: false
};

// DOM elements
const analyzerSelect = document.getElementById('analyzer-select');
const analyzerDescription = document.getElementById('analyzer-description');
const gpt5Config = document.getElementById('gpt5-config');
const gpt5ModelSelect = document.getElementById('gpt5-model');
const fpsSelect = document.getElementById('fps-select');
const maxFramesSelect = document.getElementById('max-frames-select');
const promptGroup = document.getElementById('prompt-group');
const promptSelect = document.getElementById('prompt-select');
const promptDescription = document.getElementById('prompt-description');
const videoSourceSelect = document.getElementById('video-source');
const urlGroup = document.getElementById('url-group');
const localGroup = document.getElementById('local-group');
const presetGroup = document.getElementById('preset-group');
const videoUrlInput = document.getElementById('video-url');
const localVideoSelect = document.getElementById('local-video');
const videoEmbed = document.getElementById('video-embed');
const videoPlaceholder = document.getElementById('video-placeholder');
const analyzeBtn = document.getElementById('analyze-btn');
const outputContainer = document.getElementById('output-container');
const presetGrid = document.getElementById('preset-grid');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadPrompts();
    setupEventListeners();
});

// Load available prompts from API
async function loadPrompts(analyzerType = 'gemini') {
    try {
        const response = await fetch(`/api/prompts?analyzer_type=${analyzerType}`);
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to load prompts: ' + data.error);
            return;
        }
        
        // Clear existing options except first
        promptSelect.innerHTML = '<option value="">Select a prompt template...</option>';
        
        // Populate prompt dropdown
        if (data.prompts && data.prompts.length > 0) {
            data.prompts.forEach(prompt => {
                const option = document.createElement('option');
                option.value = prompt.id;
                option.textContent = prompt.name;
                option.dataset.description = prompt.description;
                promptSelect.appendChild(option);
            });
        }
        
    } catch (error) {
        showError('Failed to load prompts: ' + error.message);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Analyzer selection
    analyzerSelect.addEventListener('change', (e) => {
        state.analyzerType = e.target.value;
        updateUIForAnalyzer();
        loadPrompts(state.analyzerType);
        updateAnalyzeButton();
    });

    // GPT-5 model selection
    gpt5ModelSelect.addEventListener('change', (e) => {
        state.gpt5Model = e.target.value;
    });

    // FPS selection
    fpsSelect.addEventListener('change', (e) => {
        state.fps = parseInt(e.target.value);
    });

    // Max frames selection
    maxFramesSelect.addEventListener('change', (e) => {
        const value = e.target.value;
        state.maxFrames = value === '' ? null : parseInt(value);
    });

    // Video source selection
    videoSourceSelect.addEventListener('change', (e) => {
        state.videoSource = e.target.value;
        updateVideoSourceUI();
        updateAnalyzeButton();
    });
    
    // Prompt selection
    promptSelect.addEventListener('change', (e) => {
        const selectedOption = e.target.options[e.target.selectedIndex];
        state.selectedPrompt = e.target.value;
        
        if (state.selectedPrompt) {
            promptDescription.textContent = selectedOption.dataset.description;
        } else {
            promptDescription.textContent = '';
        }
        
        updateAnalyzeButton();
    });
    
    // Video URL input
    videoUrlInput.addEventListener('input', (e) => {
        state.videoUrl = e.target.value.trim();
        const videoId = extractVideoId(state.videoUrl);
        
        if (videoId) {
            state.videoId = videoId;
            updateVideoEmbed(videoId);
            updatePresetSelection(state.videoUrl);
        } else {
            state.videoId = null;
            hideVideoEmbed();
        }
        
        updateAnalyzeButton();
    });

    // Local video selection
    localVideoSelect.addEventListener('change', (e) => {
        state.videoPath = e.target.value;
        updateAnalyzeButton();
    });
    
    // Preset video selection
    const presetItems = document.querySelectorAll('.preset-item');
    presetItems.forEach(item => {
        item.addEventListener('click', () => {
            const url = item.dataset.url;
            const videoId = item.dataset.videoId;
            
            videoUrlInput.value = url;
            state.videoUrl = url;
            state.videoId = videoId;
            state.videoSource = 'url';
            videoSourceSelect.value = 'url';
            
            updateVideoEmbed(videoId);
            updatePresetSelection(url);
            updateVideoSourceUI();
            updateAnalyzeButton();
        });
    });
    
    // Analyze button
    analyzeBtn.addEventListener('click', handleAnalyze);
}

// Update UI based on selected analyzer
function updateUIForAnalyzer() {
    if (state.analyzerType === 'gpt5') {
        gpt5Config.classList.remove('hidden');
        promptGroup.classList.add('hidden');
        // GPT-5 needs local video
        if (state.videoSource === 'url') {
            state.videoSource = 'local';
            videoSourceSelect.value = 'local';
            updateVideoSourceUI();
        }
    } else {
        gpt5Config.classList.add('hidden');
        promptGroup.classList.remove('hidden');
    }
}

// Update video source UI
function updateVideoSourceUI() {
    if (state.videoSource === 'url') {
        urlGroup.classList.remove('hidden');
        localGroup.classList.add('hidden');
        presetGroup.classList.remove('hidden');
    } else {
        urlGroup.classList.add('hidden');
        localGroup.classList.remove('hidden');
        presetGroup.classList.add('hidden');
        hideVideoEmbed();
        // Set default local video
        state.videoPath = localVideoSelect.value;
    }
}

// Extract YouTube video ID from URL
function extractVideoId(url) {
    if (!url) return null;
    
    const patterns = [
        /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)/,
        /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)/,
        /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)/
    ];
    
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) return match[1];
    }
    
    return null;
}

// Update video embed
function updateVideoEmbed(videoId) {
    if (videoId) {
        videoEmbed.src = `https://www.youtube.com/embed/${videoId}`;
        videoEmbed.classList.remove('hidden');
        videoPlaceholder.classList.add('hidden');
    }
}

// Hide video embed
function hideVideoEmbed() {
    videoEmbed.src = '';
    videoEmbed.classList.add('hidden');
    videoPlaceholder.classList.remove('hidden');
}

// Update preset selection visual state
function updatePresetSelection(url) {
    const presetItems = document.querySelectorAll('.preset-item');
    presetItems.forEach(item => {
        if (item.dataset.url === url) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });
}

// Update analyze button state
function updateAnalyzeButton() {
    let isValid = !state.isAnalyzing;
    
    if (state.analyzerType === 'gpt5') {
        // GPT-5 requires local video
        isValid = isValid && state.videoPath;
    } else {
        // Gemini requires prompt and video URL
        isValid = isValid && state.selectedPrompt && state.videoId;
    }
    
    analyzeBtn.disabled = !isValid;
}

// Handle analyze button click
async function handleAnalyze() {
    if (state.isAnalyzing) return;
    
    state.isAnalyzing = true;
    updateAnalyzeButton();
    
    // Update button UI
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    btnText.textContent = 'Analyzing...';
    btnLoader.classList.remove('hidden');
    
    // Show loading state in output
    const loadingMsg = state.analyzerType === 'gpt5' 
        ? 'Analyzing video with GPT-5 multi-agent system... This may take several minutes depending on FPS setting.'
        : 'Analyzing video... This may take a minute.';
    
    outputContainer.innerHTML = `
        <div class="output-placeholder">
            <div class="btn-loader" style="width: 50px; height: 50px; border-width: 4px;"></div>
            <p style="margin-top: 20px;">${loadingMsg}</p>
        </div>
    `;
    
    try {
        // Build request body based on analyzer type
        const requestBody = {
            analyzer_type: state.analyzerType
        };

        if (state.analyzerType === 'gpt5') {
            requestBody.video_path = state.videoPath;
            requestBody.fps = state.fps;
            requestBody.max_frames = state.maxFrames;
            requestBody.gpt5_model = state.gpt5Model;
        } else {
            requestBody.video_url = state.videoUrl;
            requestBody.prompt_type = state.selectedPrompt;
        }

        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else if (data.success) {
            displayReport(data.report, data.metadata);
        }
        
    } catch (error) {
        showError('Failed to analyze video: ' + error.message);
    } finally {
        // Reset button UI
        state.isAnalyzing = false;
        btnText.textContent = 'Analyze Video';
        btnLoader.classList.add('hidden');
        updateAnalyzeButton();
    }
}

// Display report in output panel
function displayReport(report, metadata = null) {
    // Use marked.js to convert markdown to HTML
    const htmlContent = marked.parse(report);
    
    // Add metadata badge if available (for GPT-5)
    let metadataBadge = '';
    if (metadata) {
        metadataBadge = `
            <div class="metadata-badge">
                <strong>Analysis Details:</strong>
                ${metadata.frames_analyzed ? `Frames: ${metadata.frames_analyzed} | ` : ''}
                ${metadata.max_frames ? `Max: ${metadata.max_frames} | ` : ''}
                ${metadata.events_detected ? `Events: ${metadata.events_detected} | ` : ''}
                ${metadata.cycles_found !== undefined ? `Cycles: ${metadata.cycles_found} | ` : ''}
                ${metadata.fps ? `FPS: ${metadata.fps} | ` : ''}
                ${metadata.model ? `Model: ${metadata.model}` : ''}
            </div>
        `;
    }
    
    outputContainer.innerHTML = `
        ${metadataBadge}
        <div class="output-content">
            ${htmlContent}
        </div>
    `;
    
    // Scroll to top of output
    outputContainer.scrollTop = 0;
}

// Show error message
function showError(message) {
    outputContainer.innerHTML = `
        <div class="error-message">
            <strong>Error:</strong> ${message}
        </div>
    `;
}


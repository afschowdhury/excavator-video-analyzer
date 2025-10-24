// Main JavaScript for Video Analyzer Web App

// State management
let state = {
    selectedPrompt: null,
    videoUrl: '',
    videoId: null,
    isAnalyzing: false
};

// DOM elements
const promptSelect = document.getElementById('prompt-select');
const promptDescription = document.getElementById('prompt-description');
const videoUrlInput = document.getElementById('video-url');
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
async function loadPrompts() {
    try {
        const response = await fetch('/api/prompts');
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to load prompts: ' + data.error);
            return;
        }
        
        // Populate prompt dropdown
        data.prompts.forEach(prompt => {
            const option = document.createElement('option');
            option.value = prompt.id;
            option.textContent = prompt.name;
            option.dataset.description = prompt.description;
            promptSelect.appendChild(option);
        });
        
    } catch (error) {
        showError('Failed to load prompts: ' + error.message);
    }
}

// Setup event listeners
function setupEventListeners() {
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
    
    // Preset video selection
    const presetItems = document.querySelectorAll('.preset-item');
    presetItems.forEach(item => {
        item.addEventListener('click', () => {
            const url = item.dataset.url;
            const videoId = item.dataset.videoId;
            
            videoUrlInput.value = url;
            state.videoUrl = url;
            state.videoId = videoId;
            
            updateVideoEmbed(videoId);
            updatePresetSelection(url);
            updateAnalyzeButton();
        });
    });
    
    // Analyze button
    analyzeBtn.addEventListener('click', handleAnalyze);
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
    const isValid = state.selectedPrompt && state.videoId && !state.isAnalyzing;
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
    outputContainer.innerHTML = `
        <div class="output-placeholder">
            <div class="btn-loader" style="width: 50px; height: 50px; border-width: 4px;"></div>
            <p style="margin-top: 20px;">Analyzing video... This may take a minute.</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_url: state.videoUrl,
                prompt_type: state.selectedPrompt
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else if (data.success) {
            displayReport(data.report);
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
function displayReport(report) {
    // Use marked.js to convert markdown to HTML
    const htmlContent = marked.parse(report);
    
    outputContainer.innerHTML = `
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


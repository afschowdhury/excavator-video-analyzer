// Main JavaScript for Video Analyzer Web App

// State management
let state = {
    analyzerType: 'gemini',
    selectedPrompt: null,
    cycleMode: 'simple',
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
const cycleModeGroup = document.getElementById('cycle-mode-group');
const cycleModeSelect = document.getElementById('cycle-mode-select');
const videoSourceSelect = document.getElementById('video-source');
const urlGroup = document.getElementById('url-group');
const localGroup = document.getElementById('local-group');
const presetGroup = document.getElementById('preset-group');
const videoUrlInput = document.getElementById('video-url');
const localVideoSelect = document.getElementById('local-video');
const videoEmbed = document.getElementById('video-embed');
const videoPlaceholder = document.getElementById('video-placeholder');
const analyzeBtn = document.getElementById('analyze-btn');
const generateReportBtn = document.getElementById('generate-report-btn');
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

    // Cycle mode selection
    cycleModeSelect.addEventListener('change', (e) => {
        state.cycleMode = e.target.value;
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
            
            // Show cycle mode dropdown if it's a cycle-time prompt
            if (state.selectedPrompt.toLowerCase().includes('cycle')) {
                cycleModeGroup.classList.remove('hidden');
            } else {
                cycleModeGroup.classList.add('hidden');
            }
        } else {
            promptDescription.textContent = '';
            cycleModeGroup.classList.add('hidden');
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
    
    // Generate HTML Report button
    generateReportBtn.addEventListener('click', handleGenerateReport);
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
    // Generate Report button has same requirements as Analyze
    generateReportBtn.disabled = !isValid;
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
            requestBody.cycle_mode = state.cycleMode;
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
            displayReport(data.report, data.metadata, data.cycle_analysis);
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
function displayReport(report, metadata = null, cycleAnalysis = null) {
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
    
    // Add cycle time analysis section if available
    let cycleAnalysisSection = '';
    if (cycleAnalysis) {
        const stats = cycleAnalysis.statistics;
        const cycleReportHtml = marked.parse(cycleAnalysis.report);
        const modeLabel = cycleAnalysis.mode === 'ai' ? 'AI-Enhanced Mode' : 'Simple Mode';
        const modeBadge = `<span class="mode-badge mode-${cycleAnalysis.mode}">${modeLabel}</span>`;
        
        cycleAnalysisSection = `
            <div class="cycle-analysis-section">
                <div class="cycle-stats-header">
                    <h3>📊 Cycle Time Statistics ${modeBadge}</h3>
                    <div class="cycle-stats-summary">
                        <div class="stat-item">
                            <span class="stat-label">Total Cycles</span>
                            <span class="stat-value">${stats.total_cycles}</span>
                        </div>
                        <div class="stat-item stat-highlight">
                            <span class="stat-label">Approx Avg</span>
                            <span class="stat-sublabel">(with gaps)</span>
                            <span class="stat-value">${stats.approximate_average_duration}s</span>
                        </div>
                        <div class="stat-item stat-highlight">
                            <span class="stat-label">Specific Avg</span>
                            <span class="stat-sublabel">(work only)</span>
                            <span class="stat-value">${stats.specific_average_duration}s</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Idle Time</span>
                            <span class="stat-value">${stats.idle_time_per_cycle}s</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Min</span>
                            <span class="stat-value">${stats.min_duration}s</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Max</span>
                            <span class="stat-value">${stats.max_duration}s</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Std Dev</span>
                            <span class="stat-value">${stats.std_deviation}s</span>
                        </div>
                    </div>
                </div>
                <div class="cycle-analysis-report">
                    ${cycleReportHtml}
                </div>
            </div>
        `;
    }
    
    outputContainer.innerHTML = `
        ${metadataBadge}
        ${cycleAnalysisSection}
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

// Handle Generate HTML Report button click
async function handleGenerateReport() {
    if (state.isAnalyzing) return;
    
    state.isAnalyzing = true;
    updateAnalyzeButton();
    
    // Update button UI
    const btnText = generateReportBtn.querySelector('.btn-text');
    const btnLoader = generateReportBtn.querySelector('.btn-loader');
    const originalText = btnText.textContent;
    btnText.textContent = 'Generating Report...';
    btnLoader.classList.remove('hidden');
    
    // Show loading state in output
    outputContainer.innerHTML = `
        <div class="output-placeholder">
            <div class="btn-loader" style="width: 50px; height: 50px; border-width: 4px;"></div>
            <p style="margin-top: 20px;">Generating comprehensive HTML training report...</p>
            <p style="font-size: 0.9em; color: var(--text-secondary);">This includes AI-powered insights and may take 1-2 minutes.</p>
        </div>
    `;
    
    try {
        // Build request body  - use the same video analysis endpoint with generate_html_report flag
        const requestBody = {
            analyzer_type: state.analyzerType,
            generate_html_report: true,
            joystick_data_path: 'data/joystick_data'
        };

        if (state.analyzerType === 'gpt5') {
            requestBody.video_path = state.videoPath;
            requestBody.fps = state.fps;
            requestBody.max_frames = state.maxFrames;
            requestBody.gpt5_model = state.gpt5Model;
        } else {
            requestBody.video_url = state.videoUrl;
            requestBody.prompt_type = state.selectedPrompt;
            requestBody.cycle_mode = state.cycleMode;
        }

        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        // Check if response is HTML (for download)
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('text/html')) {
            // Download the HTML file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `training_report_${new Date().getTime()}.html`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Show success message
            outputContainer.innerHTML = `
                <div class="output-placeholder" style="color: var(--success-color);">
                    <svg class="placeholder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="color: var(--success-color);">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p><strong>✓ HTML Report Generated Successfully!</strong></p>
                    <p style="font-size: 0.9em;">The report has been downloaded to your computer.</p>
                    <p style="font-size: 0.85em; color: var(--text-secondary); margin-top: 10px;">Open the HTML file in your browser to view the complete training report.</p>
                </div>
            `;
        } else {
            // Parse JSON response
            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
            } else {
                showError('Unexpected response format');
            }
        }
        
    } catch (error) {
        showError('Failed to generate HTML report: ' + error.message);
    } finally {
        // Reset button UI
        state.isAnalyzing = false;
        btnText.textContent = originalText;
        btnLoader.classList.add('hidden');
        updateAnalyzeButton();
    }
}


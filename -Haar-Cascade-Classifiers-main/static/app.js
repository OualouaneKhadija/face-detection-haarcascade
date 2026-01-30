/**
 * Face Detection System - Frontend Application (Simplified)
 */

// State
const state = {
    mode: 'webcam',
    isDetecting: false,
    webcamStream: null,
    websocket: null,
    animationFrame: null,
    settings: {
        scaleFactor: 1.1,
        minNeighbors: 5,
        boxColor: '#22c55e',
        boxThickness: 2
    },
    stats: {
        faceCount: 0,
        fps: 0,
        detectionTime: 0,
        frameCount: 0,
        lastFpsUpdate: Date.now()
    }
};

// DOM Elements
const elements = {
    tabs: document.querySelectorAll('.tab'),
    welcomeState: document.getElementById('welcomeState'),
    videoElement: document.getElementById('videoElement'),
    detectionCanvas: document.getElementById('detectionCanvas'),
    resultImage: document.getElementById('resultImage'),
    loadingState: document.getElementById('loadingState'),
    dropZone: document.getElementById('dropZone'),
    scaleFactor: document.getElementById('scaleFactor'),
    scaleFactorValue: document.getElementById('scaleFactorValue'),
    minNeighbors: document.getElementById('minNeighbors'),
    minNeighborsValue: document.getElementById('minNeighborsValue'),
    faceCount: document.getElementById('faceCount'),
    fps: document.getElementById('fps'),
    detectionTime: document.getElementById('detectionTime'),
    startBtn: document.getElementById('startBtn'),
    actionBtn: document.getElementById('actionBtn'),
    uploadBtn: document.getElementById('uploadBtn'),
    fileInput: document.getElementById('fileInput'),
    colorBtns: document.querySelectorAll('.color-btn'),
    boxThickness: document.getElementById('boxThickness'),
    boxThicknessValue: document.getElementById('boxThicknessValue')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initControls();
    initButtons();
    initDragAndDrop();
    initSettings();
});

// Tab Selection
function initTabs() {
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const mode = tab.dataset.mode;
            setMode(mode);
        });
    });
}

function setMode(mode) {
    state.mode = mode;
    
    elements.tabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.mode === mode);
    });
    
    if (state.isDetecting) {
        stopDetection();
    }
    
    hideAllDisplays();
    elements.welcomeState.style.display = 'block';
    updateActionButton();
    elements.uploadBtn.style.display = mode !== 'webcam' ? 'block' : 'none';
}

function updateActionButton() {
    const btn = elements.actionBtn;
    
    if (state.isDetecting) {
        btn.textContent = 'Stop Detection';
        btn.classList.add('active');
    } else {
        btn.textContent = state.mode === 'webcam' ? 'Start Webcam' : 
                          state.mode === 'image' ? 'Process Image' : 'Process Video';
        btn.classList.remove('active');
    }
}

// Controls
function initControls() {
    elements.scaleFactor.addEventListener('input', (e) => {
        state.settings.scaleFactor = parseFloat(e.target.value);
        elements.scaleFactorValue.textContent = state.settings.scaleFactor.toFixed(2);
    });
    
    elements.minNeighbors.addEventListener('input', (e) => {
        state.settings.minNeighbors = parseInt(e.target.value);
        elements.minNeighborsValue.textContent = state.settings.minNeighbors;
    });
}

// Buttons
function initButtons() {
    elements.startBtn.addEventListener('click', () => {
        setMode('webcam');
        startWebcam();
    });
    
    elements.actionBtn.addEventListener('click', () => {
        if (state.isDetecting) {
            stopDetection();
        } else {
            startDetection();
        }
    });
    
    elements.uploadBtn.addEventListener('click', () => {
        elements.fileInput.accept = state.mode === 'image' ? 'image/*' : 'video/*';
        elements.fileInput.click();
    });
    
    elements.fileInput.addEventListener('change', handleFileSelect);
}

function startDetection() {
    if (state.mode === 'webcam') {
        startWebcam();
    } else {
        elements.fileInput.accept = state.mode === 'image' ? 'image/*' : 'video/*';
        elements.fileInput.click();
    }
}

function stopDetection() {
    state.isDetecting = false;
    
    if (state.webcamStream) {
        state.webcamStream.getTracks().forEach(track => track.stop());
        state.webcamStream = null;
    }
    
    if (state.websocket) {
        state.websocket.close();
        state.websocket = null;
    }
    
    if (state.animationFrame) {
        cancelAnimationFrame(state.animationFrame);
        state.animationFrame = null;
    }
    
    hideAllDisplays();
    elements.welcomeState.style.display = 'block';
    updateStats(0, 0, 0);
    updateActionButton();
}

// Webcam
async function startWebcam() {
    try {
        showLoading();
        
        state.webcamStream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
        });
        
        elements.videoElement.srcObject = state.webcamStream;
        
        await new Promise((resolve, reject) => {
            elements.videoElement.onloadedmetadata = () => {
                elements.videoElement.play().then(resolve).catch(reject);
            };
            elements.videoElement.onerror = reject;
        });
        
        hideLoading();
        hideAllDisplays();
        elements.videoElement.classList.add('active');
        elements.detectionCanvas.classList.add('active');
        
        elements.detectionCanvas.width = elements.videoElement.videoWidth || 640;
        elements.detectionCanvas.height = elements.videoElement.videoHeight || 480;
        
        state.isDetecting = true;
        updateActionButton();
        connectWebSocket();
        
    } catch (error) {
        console.error('Webcam error:', error);
        alert('Could not access webcam: ' + error.message);
        hideLoading();
        stopDetection();
    }
}

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/detect`;
    
    state.websocket = new WebSocket(wsUrl);
    
    state.websocket.onopen = () => detectLoop();
    
    state.websocket.onmessage = (event) => {
        try {
            handleDetectionResult(JSON.parse(event.data));
        } catch (e) {
            console.error('Parse error:', e);
        }
    };
    
    state.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function detectLoop() {
    if (!state.isDetecting) return;
    
    if (!state.websocket || state.websocket.readyState !== WebSocket.OPEN) {
        state.animationFrame = requestAnimationFrame(detectLoop);
        return;
    }
    
    if (elements.videoElement.readyState < 2) {
        state.animationFrame = requestAnimationFrame(detectLoop);
        return;
    }
    
    const width = elements.videoElement.videoWidth || 640;
    const height = elements.videoElement.videoHeight || 480;
    
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = width;
    tempCanvas.height = height;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(elements.videoElement, 0, 0, width, height);
    
    const frameData = tempCanvas.toDataURL('image/jpeg', 0.7);
    
    try {
        state.websocket.send(JSON.stringify({
            frame: frameData,
            scale_factor: state.settings.scaleFactor,
            min_neighbors: state.settings.minNeighbors
        }));
    } catch (e) {
        console.error('Send error:', e);
    }
    
    // FPS counter
    state.stats.frameCount++;
    const now = Date.now();
    if (now - state.stats.lastFpsUpdate >= 1000) {
        state.stats.fps = state.stats.frameCount;
        state.stats.frameCount = 0;
        state.stats.lastFpsUpdate = now;
        elements.fps.textContent = state.stats.fps;
    }
    
    setTimeout(() => {
        state.animationFrame = requestAnimationFrame(detectLoop);
    }, 66);
}

function handleDetectionResult(data) {
    const ctx = elements.detectionCanvas.getContext('2d');
    ctx.clearRect(0, 0, elements.detectionCanvas.width, elements.detectionCanvas.height);
    
    if (data.faces && data.faces.length > 0) {
        ctx.strokeStyle = state.settings.boxColor;
        ctx.lineWidth = state.settings.boxThickness;
        ctx.font = '14px sans-serif';
        ctx.fillStyle = state.settings.boxColor;
        
        data.faces.forEach((face, index) => {
            ctx.strokeRect(face.x, face.y, face.width, face.height);
            
            const label = `Face ${index + 1}`;
            const textWidth = ctx.measureText(label).width;
            ctx.fillStyle = state.settings.boxColor;
            ctx.fillRect(face.x, face.y - 20, textWidth + 10, 18);
            
            ctx.fillStyle = '#fff';
            ctx.fillText(label, face.x + 5, face.y - 6);
            ctx.fillStyle = state.settings.boxColor;
        });
    }
    
    updateStats(data.faces_count || 0, state.stats.fps, data.detection_time_ms || 0);
}

// Image Processing
async function processImage(file) {
    try {
        showLoading();
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('scale_factor', state.settings.scaleFactor);
        formData.append('min_neighbors', state.settings.minNeighbors);
        
        const response = await fetch('/api/detect/image', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideAllDisplays();
            elements.resultImage.src = data.image_data;
            elements.resultImage.classList.add('active');
            updateStats(data.faces_count, 0, data.detection_time_ms);
            state.isDetecting = true;
            updateActionButton();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Image error:', error);
        alert('Error processing image');
    } finally {
        hideLoading();
    }
}

// Video Processing
async function processVideo(file) {
    try {
        showLoading();
        
        const videoUrl = URL.createObjectURL(file);
        elements.videoElement.src = videoUrl;
        
        await new Promise(resolve => {
            elements.videoElement.onloadedmetadata = resolve;
        });
        
        hideAllDisplays();
        elements.videoElement.classList.add('active');
        elements.detectionCanvas.classList.add('active');
        
        elements.detectionCanvas.width = elements.videoElement.videoWidth;
        elements.detectionCanvas.height = elements.videoElement.videoHeight;
        
        elements.videoElement.play();
        
        state.isDetecting = true;
        updateActionButton();
        processVideoFrames();
        
    } catch (error) {
        console.error('Video error:', error);
        alert('Error processing video');
        hideLoading();
    }
}

async function processVideoFrames() {
    if (!state.isDetecting || elements.videoElement.ended || elements.videoElement.paused) {
        if (elements.videoElement.ended) {
            state.isDetecting = false;
            updateActionButton();
        }
        return;
    }
    
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = elements.videoElement.videoWidth;
    tempCanvas.height = elements.videoElement.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(elements.videoElement, 0, 0);
    
    const frameData = tempCanvas.toDataURL('image/jpeg', 0.8);
    
    try {
        const formData = new FormData();
        formData.append('image_data', frameData);
        formData.append('scale_factor', state.settings.scaleFactor);
        formData.append('min_neighbors', state.settings.minNeighbors);
        
        const response = await fetch('/api/detect/base64', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            handleDetectionResult(data);
        }
        
    } catch (error) {
        console.error('Frame error:', error);
    }
    
    state.stats.frameCount++;
    const now = Date.now();
    if (now - state.stats.lastFpsUpdate >= 1000) {
        state.stats.fps = state.stats.frameCount;
        state.stats.frameCount = 0;
        state.stats.lastFpsUpdate = now;
    }
    
    state.animationFrame = requestAnimationFrame(processVideoFrames);
}

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (file.type.startsWith('image/')) {
        processImage(file);
    } else if (file.type.startsWith('video/')) {
        processVideo(file);
    }
    
    e.target.value = '';
}

// Drag and Drop
function initDragAndDrop() {
    const container = document.querySelector('.detection-area');
    
    container.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.dropZone.classList.add('active');
    });
    
    container.addEventListener('dragleave', (e) => {
        e.preventDefault();
        elements.dropZone.classList.remove('active');
    });
    
    container.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.dropZone.classList.remove('active');
        
        const file = e.dataTransfer.files[0];
        if (!file) return;
        
        if (file.type.startsWith('image/')) {
            setMode('image');
            processImage(file);
        } else if (file.type.startsWith('video/')) {
            setMode('video');
            processVideo(file);
        }
    });
}

// Settings
function initSettings() {
    elements.colorBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            elements.colorBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.settings.boxColor = btn.dataset.color;
        });
    });
    
    elements.boxThickness.addEventListener('input', (e) => {
        state.settings.boxThickness = parseInt(e.target.value);
        elements.boxThicknessValue.textContent = state.settings.boxThickness + 'px';
    });
}

// Utilities
function hideAllDisplays() {
    elements.welcomeState.style.display = 'none';
    elements.videoElement.classList.remove('active');
    elements.detectionCanvas.classList.remove('active');
    elements.resultImage.classList.remove('active');
    elements.loadingState.classList.remove('active');
}

function showLoading() {
    elements.loadingState.classList.add('active');
}

function hideLoading() {
    elements.loadingState.classList.remove('active');
}

function updateStats(faces, fps, time) {
    elements.faceCount.textContent = faces;
    elements.fps.textContent = fps;
    elements.detectionTime.textContent = Math.round(time);
}

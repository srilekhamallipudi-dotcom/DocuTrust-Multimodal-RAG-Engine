const BASE_URL = "http://127.0.0.1:8000";

// Global Chart variables to maintain chart re-instantiations safely
let confidenceChartInstance = null;
let chunksChartInstance = null;

// ==========================================
// INTERACTIVE MODULE NAVIGATION SWITCHER LOGIC
// ==========================================
function switchModule(moduleId) {
    // 1. Remove highlight states across side nav items
    document.querySelectorAll('.nav-link').forEach(btn => btn.classList.remove('active'));
    
    // 2. Clear visible blocks active classes
    document.querySelectorAll('.module-tab').forEach(tab => tab.classList.remove('active-module'));
    
    // 3. Setup highlight over targeted menu action element reference
    const activeBtn = document.querySelector(`[onclick="switchModule('${moduleId}')"]`);
    if(activeBtn) activeBtn.classList.add('active');
    
    // 4. Expose the actual targeted script content interface layout container
    const targetModule = document.getElementById(`module-${moduleId}`);
    if(targetModule) targetModule.classList.add('active-module');

    // Automatically trigger fresh chart plotting logic arrays if user switches to Analytics Module
    if (moduleId === 'analytics') {
        initializeAnalyticsCharts();
    }
}

// ==========================================
// DYNAMIC LIVE CHARTJS CONTROLLER CORES
// ==========================================
function initializeAnalyticsCharts() {
    const canvasConfidence = document.getElementById('confidenceChart');
    const canvasChunks = document.getElementById('chunksChart');
    
    if (!canvasConfidence || !canvasChunks) return;

    const ctxConfidence = canvasConfidence.getContext('2d');
    const ctxChunks = canvasChunks.getContext('2d');

    // Destroy existing instanced allocations safely to clear graphic memory overlaps glitches
    if(confidenceChartInstance) confidenceChartInstance.destroy();
    if(chunksChartInstance) chunksChartInstance.destroy();

    // Chart A: Trust Vector Verification Score Logs Tracking Configuration (Bar Layout)
    confidenceChartInstance = new Chart(ctxConfidence, {
        type: 'bar',
        data: {
            labels: ['Query Alpha', 'Query Beta', 'Query Gamma', 'Current Active Session'],
            datasets: [{
                label: 'Confidence Metric Score (%)',
                data: [84, 92, 71, 89], // Mock analytics telemetry logs matrix fields data
                backgroundColor: 'rgba(37, 99, 235, 0.6)',
                borderColor: '#2563eb',
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            scales: { 
                y: { 
                    beginAtZero: true, 
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: { grid: { display: false } }
            },
            plugins: { legend: { labels: { color: '#94a3b8' } } }
        }
    });

    // Chart B: Document Data Extraction Distribution Processing Map (Doughnut Layout)
    chunksChartInstance = new Chart(ctxChunks, {
        type: 'doughnut',
        data: {
            labels: ['Retrieved Valid Chunks', 'Discarded Tokens', 'Cross-Vector Overlaps'],
            datasets: [{
                data: [18, 12, 6],
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                borderWidth: 0
            }]
        },
        options: { 
            responsive: true,
            plugins: { legend: { labels: { color: '#94a3b8' } } }
        }
    });
}

// ====================
// Upload PDF (UNMODIFIED EXTRACTED PIPELINE CORE)
// ====================
async function uploadPDF() {
    const fileInput = document.getElementById("pdfFile");

    if (fileInput.files.length === 0) {
        alert("Please select PDF files.");
        return;
    }

    const formData = new FormData();
    for (const file of fileInput.files) {
        formData.append("files", file);
    }

    try {
        const response = await fetch(`${BASE_URL}/upload/`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        console.log(data);

        if (!response.ok) {
            alert(data.detail);
            return;
        }

        document.getElementById("uploadStatus").innerText = data.message;
        document.getElementById("pages").innerText = data.total_files;
        document.getElementById("totalChunks").innerText = data.total_chunks;
        document.getElementById("status").innerText = data.status;
        document.getElementById("language").innerText = data.language;

    } catch (err) {
        console.error(err);
        alert("Backend server is not running.");
    }
}

// ====================
// Ask Question (UNMODIFIED EXTRACTED PIPELINE CORE)
// ====================
async function askQuestion() {
    const question = document.getElementById("question").value;

    if (!question.trim()) {
        alert("Enter question.");
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();
        console.log(data);

        document.getElementById("answerBox").innerText = data.answer;
        document.getElementById("confidence").innerText = data.confidence;
        document.getElementById("citation").innerText = data.citation;
        document.getElementById("evidence").innerText = data.evidence_found;

        let chunkCount = 0;
        if (data.timeline) {
            for (let item of data.timeline) {
                const match = item.match(/\d+/);
                if (item.includes("Retrieved") && match) {
                    chunkCount = match[0];
                }
            }
        }

        document.getElementById("chunks").innerText = chunkCount;

        let html = "";
        if (data.timeline) {
            for (let item of data.timeline) {
                html += `<p>${item}</p>`;
            }
        }
        document.getElementById("timeline").innerHTML = html;

    } catch (err) {
        console.error(err);
        alert("Cannot connect to backend.");
    }
}
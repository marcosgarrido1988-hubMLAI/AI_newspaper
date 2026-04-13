const API_BASE_URL = window.location.origin;

// DOM Elements
const runPipelineBtn = document.getElementById('runPipelineBtn');
const topicInput = document.getElementById('topicInput');
const resultsSection = document.getElementById('results');
const pipelineMonitor = document.getElementById('pipeline-status');
const consoleText = document.getElementById('consoleText');
const currentTaskName = document.getElementById('currentTaskName');
const articleBody = document.getElementById('articleBody');
const translationContent = document.getElementById('translationContent');
const verificationContent = document.getElementById('verificationContent');
const tweetContent = document.getElementById('tweetContent');
const instaContent = document.getElementById('instaContent');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
const toggleChat = document.getElementById('toggleChat');
const chatPanel = document.getElementById('chatPanel');
const closeChat = document.getElementById('closeChat');

let currentTranslations = {};

// Event Listeners
runPipelineBtn.addEventListener('click', runPipeline);
sendChatBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
toggleChat.addEventListener('click', () => chatPanel.classList.toggle('hidden'));
closeChat.addEventListener('click', () => chatPanel.classList.add('hidden'));

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        showTranslation(e.target.dataset.lang);
    });
});

// Simulated Agent Logs to make the wait engaging
const agentThoughts = {
    'step-research': [
        "Iniciando rastreo de tendencias en la red...",
        "Analizando fuentes de noticias internacionales...",
        "Filtrando ruidos y verificando relevancia del tema...",
        "Compilando ideas clave para el reportaje..."
    ],
    'step-generation': [
        "Buscando contexto histórico en base de datos local...",
        "Estructurando narrativa del reportaje...",
        "Generando borrador inicial con LLM (Groq)...",
        "Refinando estilo periodístico y adaptando tono..."
    ],
    'step-factcheck': [
        "Cruzando datos generados con fuentes externas...",
        "Verificando cronología y nombres propios...",
        "Evaluando posibles sesgos en el contenido...",
        "Auditando integridad de la información..."
    ]
};

async function runPipeline() {
    const topic = topicInput.value.trim();
    if (!topic) return alert('Por favor, introduce un tema para investigar.');

    // UI State Reset
    resultsSection.classList.add('hidden');
    pipelineMonitor.classList.remove('hidden');
    consoleText.innerHTML = "";
    resetSteps();
    
    addLog("> SISTEMA INICIALIZADO. Destino: " + topic);
    currentTaskName.innerText = "DESPERTANDO AGENTES...";

    try {
        // Step 1: Research
        updateStep('step-research', 'active');
        currentTaskName.innerText = "INVESTIGANDO TENDENCIAS...";
        const logInterval = startSimulatedLogs('step-research');
        
        const response = await fetch(`${API_BASE_URL}/run-pipeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });

        clearInterval(logInterval);
        if (!response.ok) throw new Error('Error en el servidor');

        const data = await response.json();
        
        // Finalize visual progress
        updateStep('step-research', 'completed');
        updateStep('step-generation', 'completed');
        updateStep('step-factcheck', 'completed');
        addLog("> PROCESAMIENTO COMPLETADO EXITOSAMENTE.");
        currentTaskName.innerText = "REPORTE LISTO";

        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error(error);
        addLog("!! FATAL_ERROR: Falla en la red neuronal.");
        alert('Ocurrió un error. Si estás en Render, la primera vez puede tardar 20s en "despertar". Prueba de nuevo en unos segundos.');
    }
}

function startSimulatedLogs(stepId) {
    let index = 0;
    return setInterval(() => {
        if (agentThoughts[stepId] && index < agentThoughts[stepId].length) {
            addLog("> " + agentThoughts[stepId][index]);
            index++;
        }
    }, 4000);
}

function addLog(text) {
    const line = document.createElement('div');
    line.innerText = text;
    consoleText.appendChild(line);
    consoleText.scrollTop = consoleText.scrollHeight;
}

function resetSteps() {
    ['step-research', 'step-generation', 'step-factcheck'].forEach(id => {
        document.getElementById(id).className = 'status-item blur-card';
        document.getElementById(id).querySelector('.status-label').innerText = 'Pendiente';
    });
}

function updateStep(id, state) {
    const el = document.getElementById(id);
    el.classList.remove('active', 'completed');
    el.classList.add(state);
    el.querySelector('.status-label').innerText = state === 'active' ? 'Procesando...' : 'Completado';
}

function displayResults(data) {
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    articleBody.innerText = data.article;
    verificationContent.innerText = data.verification;
    tweetContent.innerText = data.social_posts.tweet || 'Social content pending...';
    instaContent.innerText = data.social_posts.instagram || 'Social content pending...';

    currentTranslations = parseTranslations(data.translations);
    document.querySelector('.tab-btn[data-lang="pinyin"]').click();
}

function parseTranslations(text) {
    const langs = { pinyin: '', german: '', dutch: '', portuguese: '', english: '' };
    const lowerText = text.toLowerCase();
    
    const findPart = (keywords) => {
        for (let kw of keywords) {
            let start = lowerText.indexOf(kw.toLowerCase());
            if (start !== -1) {
                let nextKeywords = ["chino", "alemán", "holandés", "portugués", "inglés", "german", "dutch", "portuguese", "english"];
                let end = text.length;
                nextKeywords.forEach(nkw => {
                    let pos = lowerText.indexOf(nkw, start + kw.length);
                    if (pos !== -1 && pos < end) end = pos;
                });
                return text.substring(start, end).replace(/.*[:\n]/m, '').trim();
            }
        }
        return "Traducción no disponible.";
    };

    langs.pinyin = findPart(["chino", "pinyin"]);
    langs.german = findPart(["alemán", "german"]);
    langs.dutch = findPart(["holandés", "dutch"]);
    langs.portuguese = findPart(["portugués", "portuguese"]);
    langs.english = findPart(["inglés", "english"]);
    return langs;
}

function showTranslation(lang) {
    translationContent.innerText = currentTranslations[lang] || "Cargando...";
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    chatInput.value = '';

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();
        appendMessage('bot', data.response);
    } catch (error) {
        appendMessage('bot', 'Error al conectar con la neurona asistente.');
    }
}

function appendMessage(sender, text) {
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    msg.innerText = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Global functions for buttons
window.copyContent = (id) => {
    const content = document.getElementById(id).innerText;
    navigator.clipboard.writeText(content).then(() => {
        alert('Copiado al portapapeles!');
    });
}

window.shareContent = () => {
    if (navigator.share) {
        navigator.share({
            title: 'Neural Newsroom - Reportaje',
            text: articleBody.innerText.substring(0, 100) + "...",
            url: window.location.href
        });
    } else {
        alert('La función de compartir no está disponible en este navegador.');
    }
}

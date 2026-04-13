const API_BASE_URL = window.location.origin;

// DOM Elements
const runPipelineBtn = document.getElementById('runPipelineBtn');
const topicInput = document.getElementById('topicInput');
const resultsSection = document.getElementById('results');
const pipelineStatus = document.getElementById('pipeline-status');
const articleBody = document.getElementById('articleBody');
const translationContent = document.getElementById('translationContent');
const verificationContent = document.getElementById('verificationContent');
const tweetContent = document.getElementById('tweetContent');
const instaContent = document.getElementById('instaContent');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');

let currentTranslations = {};

// Event Listeners
runPipelineBtn.addEventListener('click', runPipeline);
sendChatBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        showTranslation(e.target.dataset.lang);
    });
});

async function runPipeline() {
    const topic = topicInput.value.trim();
    if (!topic) return alert('Por favor, introduce un tema.');

    // Reset UI
    resultsSection.classList.add('hidden');
    pipelineStatus.classList.remove('hidden');
    resetSteps();
    
    try {
        updateStep('step-research', 'active');
        
        const response = await fetch(`${API_BASE_URL}/run-pipeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });

        if (!response.ok) throw new Error('Error en el servidor');

        const data = await response.json();
        
        // Finalize steps visualization
        updateStep('step-research', 'completed');
        updateStep('step-generation', 'completed');
        updateStep('step-factcheck', 'completed');

        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error(error);
        alert('Ocurrió un error al procesar la noticia. Asegúrate de que el backend esté corriendo.');
    } finally {
        pipelineStatus.classList.add('hidden');
    }
}

function resetSteps() {
    ['step-research', 'step-generation', 'step-factcheck'].forEach(id => {
        document.getElementById(id).className = 'status-item blur-card';
    });
}

function updateStep(id, state) {
    const el = document.getElementById(id);
    el.classList.remove('active', 'completed');
    el.classList.add(state);
}

function displayResults(data) {
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    articleBody.innerText = data.article;
    verificationContent.innerText = data.verification;
    tweetContent.innerText = data.social_posts.tweet || 'N/A';
    instaContent.innerText = data.social_posts.instagram || 'N/A';

    // Parse and store translations
    currentTranslations = parseTranslations(data.translations);
    
    // Select first tab by default
    document.querySelector('.tab-btn[data-lang="pinyin"]').click();
}

function parseTranslations(text) {
    const langs = {
        pinyin: '',
        german: '',
        dutch: '',
        portuguese: '',
        english: ''
    };
    
    // Simple parsing logic based on keywords
    const segments = text.split(/1\.|2\.|3\.|4\.|5\.|Chino|Alemán|Holandés|Portugués|Inglés/i);
    // Note: In a real app, the LLM should return JSON or structured markers. 
    // For this demo, we'll try to find the blocks.
    
    const lowerText = text.toLowerCase();
    
    const findPart = (keywords) => {
        for (let kw of keywords) {
            let start = lowerText.indexOf(kw.toLowerCase());
            if (start !== -1) {
                // Find next keyword to end
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
        appendMessage('bot', 'Error al conectar con el asistente.');
    }
}

function appendMessage(sender, text) {
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    msg.innerText = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

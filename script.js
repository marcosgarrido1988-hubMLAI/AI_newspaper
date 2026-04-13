const API_BASE_URL = window.location.origin;

// UI Translations Dictionary
const uiTranslations = {
    spanish: {
        nav_status: "MODO LECTURA ACTIVO",
        hero_title: 'Noticias a la velocidad de la <span class="gradient-text">Luz... bueno casi</span>',
        hero_subtitle: "Introduce un tema en cualquier idioma y deja que nuestra red de agentes redacte, verifique y traduzca para ti.",
        input_placeholder: "Escribe tu tema aquí...",
        btn_generate: "GENERAR",
        loading_text: "SINCRONIZANDO RED DE AGENTES...",
        sidebar_header: "OPCIONES",
        section_translations: "TRADUCCIONES",
        section_verification: "VERIFICACIÓN",
        section_social: "REDES",
        btn_new_search: "NUEVA BÚSQUEDA",
        lang_spanish: "ESPAÑOL",
        lang_german: "ALEMÁN",
        lang_english: "INGLÉS",
        lang_pinyin: "PINYIN",
        lang_dutch: "HOLANDÉS",
        lang_portuguese: "PORTUGUÉS",
        verifying_msg: "Calculando veracidad...",
        chat_header: "Asistente Editorial",
        chat_welcome: "¿Deseas profundizar en algún punto de este reportaje?",
        chat_placeholder: "Escribe aquí...",
        reading_time: "3 min lectura"
    },
    english: {
        nav_status: "READING MODE ACTIVE",
        hero_title: 'News at the speed of <span class="gradient-text">Light... well almost</span>',
        hero_subtitle: "Enter a topic in any language and let our agent network write, verify, and translate for you.",
        input_placeholder: "Write your topic here...",
        btn_generate: "GENERATE",
        loading_text: "SYNCHRONIZING AGENT NETWORK...",
        sidebar_header: "OPTIONS",
        section_translations: "TRANSLATIONS",
        section_verification: "VERIFICATION",
        section_social: "SOCIAL",
        btn_new_search: "NEW SEARCH",
        lang_spanish: "SPANISH",
        lang_german: "GERMAN",
        lang_english: "ENGLISH",
        lang_pinyin: "PINYIN",
        lang_dutch: "DUTCH",
        lang_portuguese: "PORTUGUESE",
        verifying_msg: "Verifying facts...",
        chat_header: "Editorial Assistant",
        chat_welcome: "Do you want to dive deeper into any part of this report?",
        chat_placeholder: "Type here...",
        reading_time: "3 min read"
    },
    german: {
        nav_status: "LESEMODUS AKTIV",
        hero_title: 'Nachrichten in <span class="gradient-text">Lichtgeschwindigkeit... nun ja, fast</span>',
        hero_subtitle: "Geben Sie ein Thema in einer beliebigen Sprache ein und lassen Sie unser Agenten-Netzwerk für Sie schreiben, verifizieren und übersetzen.",
        input_placeholder: "Schreiben Sie Ihr Thema hier...",
        btn_generate: "GENERIEREN",
        loading_text: "AGENTEN-NETZWERK SYNCHRONISIEREN...",
        sidebar_header: "OPTIONEN",
        section_translations: "ÜBERSETZUNGEN",
        section_verification: "VERIFIZIERUNG",
        section_social: "SOCIAL MEDIA",
        btn_new_search: "NEUE SUCHE",
        lang_spanish: "SPANISCH",
        lang_german: "DEUTSCH",
        lang_english: "ENGLISCH",
        lang_pinyin: "PINYIN",
        lang_dutch: "NIEDERLÄNDISCH",
        lang_portuguese: "PORTUGIESISCH",
        verifying_msg: "Fakten werden geprüft...",
        chat_header: "Redaktionsassistent",
        chat_welcome: "Möchten Sie tiefer in einen Teil dieses Berichts eintauchen?",
        chat_placeholder: "Hier tippen...",
        reading_time: "3 Min. Lesezeit"
    },
    pinyin: {
        nav_status: "YUÈDÚ MÓSHÌ JĪHUÓ",
        hero_title: 'Yuèdú sùdù de <span class="gradient-text">Xīnwén... hǎo de jīhū</span>',
        hero_subtitle: "Shūrù rènhé yǔyán de zhùtí, ràng wǒmen de dàilǐ wǎngluò wèi nín xiězuò, yànzhèng hé fānyì.",
        input_placeholder: "Zài zhèlǐ xiě nín de zhùtí...",
        btn_generate: "SHĒNGCHÉNG",
        loading_text: "DÀILǏ WǍNGLUÒ TÓNGBÙ ZHŌNG...",
        sidebar_header: "XUǍNXIÀNG",
        section_translations: "FĀNYÌ",
        section_verification: "YÀNZHÈNG",
        section_social: "SHEJIĀO",
        btn_new_search: "XĪN DE SǑUSUǑ",
        lang_spanish: "XĪBĀNYÁYǓ",
        lang_german: "DÉYǓ",
        lang_english: "YĪNGYǓ",
        lang_pinyin: "PINYIN",
        lang_dutch: "HÉLÁNYǓ",
        lang_portuguese: "PÚTÁOYÁYǓ",
        verifying_msg: "Zhèngzài yànzhèng shìshí...",
        chat_header: "Biānjí Zhùshǒu",
        chat_welcome: "Nín xiǎng gèng shēnrù dì liǎojiě běn bàogào de rènhé bùfèn ma?",
        chat_placeholder: "Zài zhèlǐ shūrù...",
        reading_time: "3 fēnzhōng yuèdú"
    },
    dutch: {
        nav_status: "LEESMODUS ACTIEF",
        hero_title: 'Nieuws met de snelheid van het <span class="gradient-text">Licht... nou ja, bijna</span>',
        hero_subtitle: "Voer een onderwerp in elke taal in en laat ons agent-netwerk voor u schrijven, verifiëren en vertalen.",
        input_placeholder: "Schrijf je onderwerp hier...",
        btn_generate: "GENEREREN",
        loading_text: "AGENT-NETWERK SYNCHRONISEREN...",
        sidebar_header: "OPTIES",
        section_translations: "VERTALINGEN",
        section_verification: "VERIFICATIE",
        section_social: "SOCIAL MEDIA",
        btn_new_search: "NIEUWE ZOEKOPDRACHT",
        lang_spanish: "SPAANS",
        lang_german: "DUITS",
        lang_english: "ENGELS",
        lang_pinyin: "PINYIN",
        lang_dutch: "NEDERLANDS",
        lang_portuguese: "PORTUGEES",
        verifying_msg: "Feiten verifiëren...",
        chat_header: "Redactie-assistent",
        chat_welcome: "Wilt u dieper op een deel van dit verslag ingaan?",
        chat_placeholder: "Typ hier...",
        reading_time: "3 min leestijd"
    },
    portuguese: {
        nav_status: "MODO DE LEITURA ATIVO",
        hero_title: 'Notícias à velocidade da <span class="gradient-text">Luz... bem quase</span>',
        hero_subtitle: "Insira um tema em qualquer idioma e deixe que nossa rede de agentes escreva, verifique e traduza para você.",
        input_placeholder: "Escreva seu tema aqui...",
        btn_generate: "GERAR",
        loading_text: "SINCRONIZANDO REDE DE AGENTES...",
        sidebar_header: "OPÇÕES",
        section_translations: "TRADUÇÕES",
        section_verification: "VERIFICAÇÃO",
        section_social: "REDES SOCIAIS",
        btn_new_search: "NOVA BUSCA",
        lang_spanish: "ESPANHOL",
        lang_german: "ALEMÃO",
        lang_english: "INGLÊS",
        lang_pinyin: "PINYIN",
        lang_dutch: "HOLANDÊS",
        lang_portuguese: "PORTUGUÊS",
        verifying_msg: "Verificando fatos...",
        chat_header: "Assistente Editorial",
        chat_welcome: "Deseja aprofundar em algum ponto deste relatório?",
        chat_placeholder: "Escreva aqui...",
        reading_time: "3 min de leitura"
    }
};

// DOM Elements
const runPipelineBtn = document.getElementById('runPipelineBtn');
const topicInput = document.getElementById('topicInput');
const heroSection = document.getElementById('hero');
const workspace = document.getElementById('workspace');
const loadingState = document.getElementById('loadingState');

const articleTopic = document.getElementById('articleTopic');
const articleBody = document.getElementById('articleBody');
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
let originalArticle = "";
let currentUILang = "spanish";

// Event Listeners
runPipelineBtn.addEventListener('click', runPipeline);
topicInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') runPipeline(); });
sendChatBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
toggleChat.addEventListener('click', () => chatPanel.classList.toggle('hidden'));
closeChat.addEventListener('click', () => chatPanel.classList.add('hidden'));

// Navbar Flag Switcher
document.querySelectorAll('.flag-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const lang = e.currentTarget.dataset.uiLang;
        switchUILanguage(lang);
    });
});

// Vertical Tabs (Article Language)
document.querySelectorAll('.v-tab').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.v-tab').forEach(b => b.classList.remove('active'));
        const target = e.currentTarget;
        target.classList.add('active');
        showTranslation(target.dataset.lang);
    });
});

function switchUILanguage(lang) {
    // Normalización de idiomas comunes y limpieza
    let normalized = lang ? lang.toLowerCase().trim() : 'spanish';
    
    // Mapeo de códigos cortos a nombres largos si es necesario
    const mapping = {
        'es': 'spanish', 'esp': 'spanish', 'castellano': 'spanish',
        'en': 'english', 'eng': 'english',
        'de': 'german', 'ger': 'german', 'deutsch': 'german',
        'nl': 'dutch', 'ned': 'dutch', 'holandés': 'dutch',
        'pt': 'portuguese', 'portugués': 'portuguese',
        'zh': 'pinyin', 'chinese': 'pinyin', 'chino': 'pinyin'
    };

    if (mapping[normalized]) normalized = mapping[normalized];
    
    // Si el idioma no existe en nuestro diccionario, usamos español por defecto
    if (!uiTranslations[normalized]) {
        console.warn(`Idioma no soportado detectado: ${normalized}. Usando español.`);
        normalized = 'spanish';
    }

    currentUILang = normalized;
    
    // Update active flag in nav
    document.querySelectorAll('.flag-btn').forEach(b => b.classList.toggle('active', b.dataset.uiLang === normalized));
    
    // Update all elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (uiTranslations[normalized][key]) {
            el.innerHTML = uiTranslations[normalized][key];
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (uiTranslations[normalized][key]) {
            el.placeholder = uiTranslations[normalized][key];
        }
    });

    // Special case: Reading time
    if (document.getElementById('readingTimeText')) {
        document.getElementById('readingTimeText').innerText = uiTranslations[normalized].reading_time;
    }

    // Sync with Article Translation
    const targetTab = document.querySelector(`.v-tab[data-lang="${normalized}"]`);
    if (targetTab && !workspace.classList.contains('hidden')) {
        // Solo disparamos el click si el workspace está visible
        // Usamos una bandera para evitar bucles infinitos si fuera necesario
        showTranslation(lang);
        // Actualizamos estado visual de la pestaña lateral
        document.querySelectorAll('.v-tab').forEach(b => b.classList.remove('active'));
        targetTab.classList.add('active');
    }
}

async function runPipeline() {
    const topic = topicInput.value.trim();
    if (!topic) return alert('Por favor, ingresa un tema.');

    loadingState.classList.remove('hidden');
    heroSection.style.opacity = "0.3";
    heroSection.style.pointerEvents = "none";

    try {
        const response = await fetch(`${API_BASE_URL}/run-pipeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });

        if (!response.ok) throw new Error('Error en el servidor');

        const data = await response.json();
        
        originalArticle = data.article;
        currentTranslations = parseTranslations(data.translations);
        currentTranslations['spanish'] = originalArticle;

        // Auto-Language Sync
        const detected = data.detected_lang || 'spanish';
        switchUILanguage(detected);

        // Update UI
        articleTopic.innerText = data.topic;
        verificationContent.innerText = data.verification;
        tweetContent.innerText = data.social_posts.tweet || 'N/A';
        instaContent.innerText = data.social_posts.instagram || 'N/A';

        loadingState.classList.add('hidden');
        heroSection.classList.add('hidden');
        workspace.classList.remove('hidden');

        // Select the correct translation tab
        const targetTab = document.querySelector(`.v-tab[data-lang="${detected}"]`);
        if (targetTab) targetTab.click();
        else document.querySelector('.v-tab[data-lang="spanish"]').click();

    } catch (error) {
        console.error("Pipeline Error:", error);
        loadingState.classList.add('hidden');
        heroSection.style.opacity = "1";
        heroSection.style.pointerEvents = "all";
        
        // Error más descriptivo
        const errorMsg = error.message || "Error desconocido";
        alert(`Error al generar la noticia: ${errorMsg}\n\nRevisa el terminal de VS Code para ver el 'traceback' completo.`);
    }
}

function parseTranslations(text) {
    const langs = { pinyin: '', german: '', dutch: '', portuguese: '', english: '' };
    try {
        if (!text || typeof text !== 'string') return langs;
        
        console.log("Analizando respuesta de idiomas...");
        
        let cleanText = text
            .replace(/```json/g, '')
            .replace(/```/g, '')
            .replace(/JSON[:\s]*/i, '')
            .trim();
        
        const start = cleanText.indexOf('{');
        const end = cleanText.lastIndexOf('}') + 1;
        
        if (start !== -1 && end !== 0) {
            const jsonBody = cleanText.substring(start, end);
            const parsed = JSON.parse(jsonBody);
            
            // NORMALIZACIÓN DE CLAVES: Convertimos todo a minúsculas y mapeamos
            const normalizedData = {};
            const keyMapping = {
                'german': 'german', 'alemán': 'german', 'de': 'german',
                'english': 'english', 'inglés': 'english', 'en': 'english',
                'pinyin': 'pinyin', 'chino': 'pinyin', 'zh': 'pinyin',
                'dutch': 'dutch', 'holandés': 'dutch', 'nl': 'dutch',
                'portuguese': 'portuguese', 'portugués': 'portuguese', 'pt': 'portuguese'
            };

            for (let key in parsed) {
                const lowKey = key.toLowerCase();
                const targetKey = keyMapping[lowKey] || lowKey;
                normalizedData[targetKey] = parsed[key];
            }

            if (Object.values(normalizedData).some(v => v && v.length > 10)) {
                console.log("Traducciones normalizadas con éxito.");
                return normalizedData;
            }
        }
        console.warn("La IA no devolvió contenido traducido válido.");
    } catch (e) { 
        console.error("Fallo crítico en el procesador de idiomas:", e); 
    }
    return langs;
}

function showTranslation(lang) {
    // Si es español o el idioma pedido no tiene contenido, mostramos el original
    const translation = currentTranslations[lang];
    const contentToShow = (translation && translation.length > 20) ? translation : originalArticle;

    articleBody.style.opacity = "0";
    setTimeout(() => {
        articleBody.innerText = contentToShow;
        articleBody.style.opacity = "1";
    }, 200);
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
    } catch (error) { appendMessage('bot', 'Error.'); }
}

function appendMessage(sender, text) {
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    msg.innerText = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

window.copyContent = (id) => {
    const content = document.getElementById(id).innerText;
    navigator.clipboard.writeText(content).then(() => alert('¡Copiado!'));
}

window.shareContent = () => {
    if (navigator.share) {
        navigator.share({
            title: 'Neural Newsroom',
            text: articleBody.innerText.substring(0, 150),
            url: window.location.href
        });
    }
}

// Initialize UI strings on load
window.addEventListener('load', () => {
    switchUILanguage('spanish');
});

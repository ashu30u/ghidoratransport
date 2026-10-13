/* ==========================================================================
   GHIDORA AI TRANSPORT CONTROL TOWER - ENTERPRISE LOGIC ENGINE
   ========================================================================== */

// --- DATA STORES & APPLICATION STATE ---
const appState = {
    bookingsToday: 18,
    revenueToday: 48500,
    runningVehicles: 12,
    availableVehicles: 3,
    availableDrivers: 5,
    pendingPaymentTotal: 22000,
    businessHealth: 96,
    isSpeaking: false,
    isMotionActive: false,
    motionInterval: null,
    
    // Active Smart Alerts
    alerts: [
        {
            id: 'alt-1',
            type: 'critical',
            category: 'compliance',
            title: 'Insurance Expiry Alert',
            reg: 'CG04 XX 1234',
            description: 'Vehicle CG04 XX1234 insurance expires in 5 days. Urgent renewal required.',
            actionText: 'Renew Now (₹14,500)',
            actionType: 'RENEW_INSURANCE'
        },
        {
            id: 'alt-2',
            type: 'critical',
            category: 'driver',
            title: 'Driver Fatigue / Safety Violation',
            driver: 'Ramesh Kumar',
            description: 'Driver Ramesh has been driving continuously for 12 hours. Immediate 8-hour rest mandatory.',
            actionText: 'Send Mandatory Rest Notice',
            actionType: 'REST_DRIVER'
        },
        {
            id: 'alt-3',
            type: 'warning',
            category: 'weather',
            title: 'Heavy Rain Route Hazard',
            route: 'Dhamtari → Raipur',
            description: 'Heavy rain expected tomorrow on Dhamtari-Raipur stretch. Possible 40 min delivery delay.',
            actionText: 'Dispatch Today Recommended',
            actionType: 'ADVISE_DISPATCH'
        },
        {
            id: 'alt-4',
            type: 'warning',
            category: 'payment',
            title: 'Pending Customer Overdue Payment',
            customer: 'Amit Sharma',
            description: 'Customer Amit has a remaining pending balance of ₹3,500 for Booking #GH-8092.',
            actionText: 'Send WhatsApp Payment Reminder',
            actionType: 'REMIND_PAYMENT'
        },
        {
            id: 'alt-5',
            type: 'info',
            category: 'compliance',
            title: 'Fitness Certificate Due',
            reg: 'CG04 YY 5678',
            description: 'Vehicle Fitness Certificate expires tomorrow. Schedule RTO inspection.',
            actionText: 'Schedule RTO Slot',
            actionType: 'SCHEDULE_RTO'
        },
        {
            id: 'alt-6',
            type: 'critical',
            category: 'compliance',
            title: 'PUC Compliance Expired',
            reg: 'CG04 EX 9900',
            description: 'PUC Certificate expired today. AI Lock active: Vehicle cannot be assigned until renewed.',
            actionText: 'Upload New PUC Certificate',
            actionType: 'UPLOAD_PUC'
        }
    ],

    // Fleet GPS Telematics
    vehicles: [
        { id: 'v1', reg: 'CG04XX1234', model: 'Mahindra Pickup', cap: '1.2 Ton', status: 'Running', lat: 21.2514, lng: 81.6296, speed: '58 km/h', driver: 'Ramesh Kumar', phone: '+91-9826111111', route: 'Dhamtari → Raipur', earnings: 245000, step: 0 },
        { id: 'v2', reg: 'CG04EX8842', model: 'Tata Ace Super', cap: '850 KG', status: 'Idle', lat: 20.6971, lng: 81.5492, speed: '0 km/h', driver: 'Sunil Verma', phone: '+91-9826222222', route: 'Stationed at Dhamtari Hub', earnings: 195000, step: 0 },
        { id: 'v3', reg: 'CG04YY5678', model: 'Ashok Leyland 16T', cap: '16 Ton', status: 'Stopped', lat: 21.1904, lng: 81.2849, speed: '0 km/h', driver: 'Vikram Singh', phone: '+91-9826333333', route: 'Bypass KM 42 (Unscheduled Halt)', earnings: 375400, step: 0 },
        { id: 'v4', reg: 'CG04ZZ9900', model: 'Eicher Pro 2059', cap: '3.5 Ton', status: 'Running', lat: 21.0971, lng: 81.7492, speed: '62 km/h', driver: 'Anil Yadav', phone: '+91-9826444444', route: 'Raipur → Bilaspur Expressway', earnings: 182000, step: 0 }
    ],

    // Live Dispatch Registry
    dispatches: [
        { id: 'GH-DSP-1048', cargo: 'Furniture (650 KG)', vehicle: 'Mahindra Pickup (CG04XX1234)', driver: 'Ramesh Kumar', route: 'Dhamtari → Raipur', dieselCost: '₹840', status: 'In Transit', time: '10:15 AM' },
        { id: 'GH-DSP-1049', cargo: 'Construction Cement (4.2 Ton)', vehicle: 'Ashok Leyland 16T (CG04YY5678)', driver: 'Vikram Singh', route: 'Raipur → Durg', dieselCost: '₹1,450', status: 'Delayed Halt', time: '11:30 AM' },
        { id: 'GH-DSP-1050', cargo: 'Consumer Electronics (350 KG)', vehicle: 'Tata Ace Super (CG04EX8842)', driver: 'Sunil Verma', route: 'Raipur City Express', dieselCost: '₹420', status: 'Dispatched', time: '01:45 PM' }
    ],

    // Bookings drill-down data (18 bookings for today)
    bookingsList: [
        { id: 'BK-8901', customer: 'Shree Balaji Traders', cargo: 'Industrial Pipes (800 KG)', from: 'Raipur', to: 'Durg', fare: 4500, status: 'In Transit', vehicle: 'CG04XX1234' },
        { id: 'BK-8902', customer: 'Amit Sharma', cargo: 'Household Furniture (650 KG)', from: 'Dhamtari', to: 'Raipur', fare: 3500, status: 'Payment Pending', vehicle: 'CG04EX8842' },
        { id: 'BK-8903', customer: 'Chhattisgarh Agrotech', cargo: 'Paddy Bags (2.5 Ton)', from: 'Kurud', to: 'Raipur Mandi', fare: 7200, status: 'Delivered', vehicle: 'CG04YY5678' },
        { id: 'BK-8904', customer: 'Royale Furnishing', cargo: 'Sofa & Bedding (400 KG)', from: 'Raipur', to: 'Bhilai', fare: 3200, status: 'In Transit', vehicle: 'CG04ZZ9900' },
        { id: 'BK-8905', customer: 'Patanjali Distributor', cargo: 'FMCG Grocery (1.1 Ton)', from: 'Durg', to: 'Rajnandgaon', fare: 5400, status: 'Delivered', vehicle: 'CG04XX1234' },
        { id: 'BK-8906', customer: 'Vinod Hardware', cargo: 'Cement Bags (3 Ton)', from: 'Simga', to: 'Raipur', fare: 6800, status: 'In Transit', vehicle: 'CG04YY5678' },
        { id: 'BK-8907', customer: 'Kalyan Electronics', cargo: 'LED TV & Refrigerators', from: 'Raipur', to: 'Bilaspur', fare: 5800, status: 'In Transit', vehicle: 'CG04ZZ9900' },
        { id: 'BK-8908', customer: 'Mahamaya Steel', cargo: 'TMT Rebars (4 Ton)', from: 'Urla Industrial', to: 'Dhamtari', fare: 8500, status: 'Delivered', vehicle: 'CG04YY5678' },
        { id: 'BK-8909', customer: 'Gupta Medical Store', cargo: 'Medicines & Syrups (200 KG)', from: 'Raipur', to: 'Mahasamund', fare: 2600, status: 'Delivered', vehicle: 'CG04EX8842' },
        { id: 'BK-8910', customer: 'Modern Tiles & Granites', cargo: 'Floor Tiles (1.8 Ton)', from: 'Durg', to: 'Raipur', fare: 4800, status: 'In Transit', vehicle: 'CG04XX1234' }
    ],

    // Debtors data
    debtorsList: [
        { customer: 'Amit Sharma', bookingId: 'GH-8092', amount: 3500, daysOverdue: 6, phone: '+91-9826199999', route: 'Dhamtari → Raipur' },
        { customer: 'Raipur Timber Mart', bookingId: 'GH-7910', amount: 8200, daysOverdue: 14, phone: '+91-9826188888', route: 'Urla → Jagdalpur' },
        { customer: 'Chhattisgarh Cold Storage', bookingId: 'GH-7840', amount: 10300, daysOverdue: 21, phone: '+91-9826177777', route: 'Durg → Bilaspur' }
    ],

    // Driver Roster
    driversList: [
        { name: 'Ramesh Kumar', vehicle: 'CG04XX1234', rating: 4.9, trips: 340, status: 'Driving (Fatigue Alert)', restHours: 2, phone: '+91-9826111111' },
        { name: 'Sunil Verma', vehicle: 'CG04EX8842', rating: 4.8, trips: 285, status: 'Available (Dhamtari)', restHours: 10, phone: '+91-9826222222' },
        { name: 'Vikram Singh', vehicle: 'CG04YY5678', rating: 4.7, trips: 410, status: 'Halted on Route', restHours: 6, phone: '+91-9826333333' },
        { name: 'Anil Yadav', vehicle: 'CG04ZZ9900', rating: 4.9, trips: 198, status: 'Driving (Expressway)', restHours: 5, phone: '+91-9826444444' },
        { name: 'Mahesh Sahu', vehicle: 'Standby / Fleet Reserve', rating: 4.8, trips: 154, status: 'Available (Raipur Hub)', restHours: 12, phone: '+91-9826555555' },
        { name: 'Dinesh Patel', vehicle: 'On Medical Leave', rating: 4.6, trips: 220, status: 'On Leave (Returning Mon)', restHours: 0, phone: '+91-9826666666' },
        { name: 'Kishan Dewangan', vehicle: 'On Planned Leave', rating: 4.9, trips: 310, status: 'On Leave', restHours: 0, phone: '+91-9826777777' }
    ]
};

let mapInstance = null;
let vehicleMarkers = {};
let routePolyline = null;
let revenueChartInstance = null;
let expenseChartInstance = null;

// --- INITIALIZATION ---
function initControlTowerApp() {
    initBackgroundParticles();
    applyTimeBasedGreeting();
    initNavigation();
    renderAlerts();
    renderDispatchTable();
    initLeafletMap();
    initCharts();
    initDispatchEngine();
    initChatManager();
    initGlobalVoiceControls();

    // Time-based executive briefing trigger
    const btnVoiceGreet = document.getElementById('btnVoiceGreet');
    if (btnVoiceGreet && !btnVoiceGreet.dataset.bound) {
        btnVoiceGreet.dataset.bound = 'true';
        btnVoiceGreet.addEventListener('click', toggleMorningBriefing);
    }

    // Check query params or shortcuts
    showToast('Ghidora Enterprise AI 2.0 Control Tower connected. All telematics nodes active.', 'success', 'System Online');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initControlTowerApp);
} else {
    initControlTowerApp();
}

// --- MODERN CYBER TOAST NOTIFICATIONS ---
function showToast(message, type = 'info', title = '') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type}`;

    let iconHtml = '<i class="fa-solid fa-bell"></i>';
    if (type === 'success') iconHtml = '<i class="fa-solid fa-circle-check"></i>';
    if (type === 'warning') iconHtml = '<i class="fa-solid fa-triangle-exclamation"></i>';
    if (type === 'danger') iconHtml = '<i class="fa-solid fa-circle-exclamation"></i>';

    toast.innerHTML = `
        <div class="toast-icon">${iconHtml}</div>
        <div class="toast-body">
            ${title ? `<div class="toast-title">${title}</div>` : ''}
            <div class="toast-desc">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

// --- NAVIGATION SWITCHER ---
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('data-target');
            switchSection(targetId);
        });
    });
}

function switchSection(targetSectionId) {
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));

    const activeLink = document.querySelector(`.nav-link[data-target="${targetSectionId}"]`);
    const activeSection = document.getElementById(targetSectionId);

    if (activeLink) activeLink.classList.add('active');
    if (activeSection) activeSection.classList.add('active');

    // Trigger map resize if switching to GPS view
    if (targetSectionId === 'sec-gps' && mapInstance) {
        setTimeout(() => mapInstance.invalidateSize(), 200);
    }
}

// --- AUTHENTIC INDIAN VOICE AI ENGINE & AUDIO CHIME ---
const voiceConfig = {
    preset: 'priya',        // 'priya' (Female Indian), 'rohan' (Male Indian), 'hindi' (Shuddh Hindi)
    style: 'hinglish',      // 'hinglish', 'hindi', 'indian_english'
    selectedVoiceUri: null, // explicit voice selection if any
    rate: 0.95,
    pitch: 1.05
};

// High-tech futuristic command tower audio chime via Web Audio API
function playChimeSound() {
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        const ctx = new AudioContext();

        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const gain = ctx.createGain();

        osc1.type = 'sine';
        osc2.type = 'sine';

        const now = ctx.currentTime;
        osc1.frequency.setValueAtTime(587.33, now); // D5
        osc1.frequency.setValueAtTime(880.00, now + 0.08); // A5

        osc2.frequency.setValueAtTime(880.00, now);
        osc2.frequency.setValueAtTime(1174.66, now + 0.08); // D6

        gain.gain.setValueAtTime(0.09, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.38);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(ctx.destination);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.38);
        osc2.stop(now + 0.38);
    } catch (e) {
        // AudioContext blocked or not supported
    }
}

function getBestIndianVoice(preset = voiceConfig.preset) {
    if (!('speechSynthesis' in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;

    // Explicit selection by user
    if (voiceConfig.selectedVoiceUri && voiceConfig.selectedVoiceUri !== 'auto') {
        const found = voices.find(v => v.voiceURI === voiceConfig.selectedVoiceUri || v.name === voiceConfig.selectedVoiceUri);
        if (found) return found;
    }

    // Filter Indian Hindi voices (e.g. Swara, Hemant, Kalpana, Heera, Google हिन्दी, hi-IN)
    const hindiVoices = voices.filter(v => 
        (v.lang && (v.lang.toLowerCase().includes('hi-in') || v.lang.toLowerCase().includes('hi_in') || v.lang.toLowerCase().startsWith('hi'))) ||
        (v.name && (v.name.toLowerCase().includes('hindi') || v.name.toLowerCase().includes('swara') || v.name.toLowerCase().includes('hemant') || v.name.toLowerCase().includes('kalpana') || v.name.toLowerCase().includes('heera') || v.name.toLowerCase().includes('madhur')))
    );

    // Filter Indian English voices (e.g. Neerja, Prabhat, Google English (India), en-IN)
    const indianEnglishVoices = voices.filter(v => 
        (v.lang && (v.lang.toLowerCase().includes('en-in') || v.lang.toLowerCase().includes('en_in'))) ||
        (v.name && (v.name.toLowerCase().includes('india') || v.name.toLowerCase().includes('neerja') || v.name.toLowerCase().includes('prabhat') || v.name.toLowerCase().includes('ravi') || v.name.toLowerCase().includes('veena')))
    );

    if (preset === 'hindi' && hindiVoices.length > 0) {
        return hindiVoices[0];
    }

    if (preset === 'rohan') {
        // Look for male Indian voice
        const maleHindi = hindiVoices.find(v => v.name.toLowerCase().includes('hemant') || v.name.toLowerCase().includes('madhur') || v.name.toLowerCase().includes('male'));
        if (maleHindi) return maleHindi;

        const maleIndEng = indianEnglishVoices.find(v => v.name.toLowerCase().includes('prabhat') || v.name.toLowerCase().includes('ravi') || v.name.toLowerCase().includes('male'));
        if (maleIndEng) return maleIndEng;

        if (hindiVoices.length > 0) return hindiVoices[0];
        if (indianEnglishVoices.length > 0) return indianEnglishVoices[0];
    }

    if (preset === 'priya') {
        // Look for female Indian voice
        const femaleIndEng = indianEnglishVoices.find(v => v.name.toLowerCase().includes('neerja') || v.name.toLowerCase().includes('veena') || v.name.toLowerCase().includes('female'));
        if (femaleIndEng) return femaleIndEng;

        const femaleHindi = hindiVoices.find(v => v.name.toLowerCase().includes('swara') || v.name.toLowerCase().includes('heera') || v.name.toLowerCase().includes('kalpana') || v.name.toLowerCase().includes('female'));
        if (femaleHindi) return femaleHindi;

        if (indianEnglishVoices.length > 0) return indianEnglishVoices[0];
        if (hindiVoices.length > 0) return hindiVoices[0];
    }

    // Combined fallback pool
    if (hindiVoices.length > 0) return hindiVoices[0];
    if (indianEnglishVoices.length > 0) return indianEnglishVoices[0];

    // System fallback with clear pronunciation
    const naturalVoice = voices.find(v => v.name.toLowerCase().includes('natural') || v.name.toLowerCase().includes('zira') || v.name.toLowerCase().includes('samantha')) || voices[0];
    return naturalVoice;
}

if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        populateSystemVoicesList();
    };
}

// Speaks natural Indian speech with tone & chime
function speakText(textPayload, onEndCallback = null) {
    if (!('speechSynthesis' in window)) {
        const plainMsg = typeof textPayload === 'string' ? textPayload : (textPayload.hinglish || textPayload.hindi || textPayload.indian_english);
        showToast(plainMsg, 'info', 'AI Speech');
        if (onEndCallback) onEndCallback();
        return;
    }

    window.speechSynthesis.cancel(); // Stop active speech
    playChimeSound(); // Play futuristic chime before speech

    const voice = getBestIndianVoice(voiceConfig.preset);
    const isNativeHindiVoice = voice && voice.lang && (voice.lang.toLowerCase().includes('hi-in') || voice.lang.toLowerCase().includes('hi_in') || voice.lang.toLowerCase().startsWith('hi'));

    let spokenText = "";
    let displayText = "";

    if (typeof textPayload === 'string') {
        spokenText = textPayload;
        displayText = textPayload;
    } else {
        // Multi-language intelligent payload
        if (voiceConfig.style === 'hindi' || isNativeHindiVoice) {
            spokenText = textPayload.hindi || textPayload.hinglish;
            displayText = textPayload.hinglish || textPayload.hindi;
        } else if (voiceConfig.style === 'indian_english') {
            spokenText = textPayload.indian_english || textPayload.hinglish;
            displayText = textPayload.hinglish || textPayload.indian_english;
        } else {
            // Hinglish mode
            if (isNativeHindiVoice && textPayload.hindi) {
                spokenText = textPayload.hindi;
            } else {
                spokenText = textPayload.hinglish || textPayload.indian_english;
            }
            displayText = textPayload.hinglish || textPayload.hindi;
        }
    }

    const utterance = new SpeechSynthesisUtterance(spokenText);

    if (voice) {
        utterance.voice = voice;
        utterance.lang = voice.lang || (isNativeHindiVoice ? 'hi-IN' : 'en-IN');
    } else {
        utterance.lang = 'hi-IN';
    }

    // Persona-specific rate & pitch tuning
    if (voiceConfig.preset === 'priya') {
        utterance.pitch = voiceConfig.pitch || 1.08;
        utterance.rate = voiceConfig.rate || 0.95;
    } else if (voiceConfig.preset === 'rohan') {
        utterance.pitch = voiceConfig.pitch || 0.88;
        utterance.rate = voiceConfig.rate || 0.93;
    } else {
        utterance.pitch = voiceConfig.pitch || 1.0;
        utterance.rate = voiceConfig.rate || 0.92;
    }

    // Show Audio HUD Subtitle Banner
    const hud = document.getElementById('audioHudBanner');
    const hudSub = document.getElementById('audioHudSubtitle');
    if (hud && hudSub) {
        hudSub.innerText = `"${displayText}"`;
        hud.classList.remove('hidden');
    }

    utterance.onend = () => {
        appState.isSpeaking = false;
        setEqualizerState(false);
        if (hud) hud.classList.add('hidden');
        if (onEndCallback) onEndCallback();
    };

    utterance.onerror = () => {
        appState.isSpeaking = false;
        setEqualizerState(false);
        if (hud) hud.classList.add('hidden');
    };

    appState.isSpeaking = true;
    setEqualizerState(true);
    window.speechSynthesis.speak(utterance);
}

function setEqualizerState(isPlaying) {
    const wave = document.getElementById('briefingAudioWave');
    const greetBtn = document.getElementById('btnVoiceGreet');
    const heroCore = document.querySelector('.ai-core-glow');

    if (wave) {
        if (isPlaying) {
            wave.classList.remove('hidden');
            wave.classList.add('playing');
        } else {
            wave.classList.add('hidden');
            wave.classList.remove('playing');
        }
    }
    if (greetBtn) {
        const textSpan = document.getElementById('briefingBtnText');
        if (textSpan) {
            textSpan.innerText = isPlaying ? 'Speaking Briefing...' : getTimeGreeting().btnText;
        }
    }
    if (heroCore) {
        if (isPlaying) {
            heroCore.style.boxShadow = '0 0 35px #00f2fe, 0 0 60px #ff007f';
            heroCore.style.animation = 'pulse-glow 0.8s infinite alternate';
        } else {
            heroCore.style.boxShadow = '';
            heroCore.style.animation = '';
        }
    }
}

function toggleMorningBriefing() {
    if (appState.isSpeaking) {
        window.speechSynthesis.cancel();
        appState.isSpeaking = false;
        setEqualizerState(false);
        const hud = document.getElementById('audioHudBanner');
        if (hud) hud.classList.add('hidden');
        showToast('Voice briefing paused.', 'info', 'Audio Paused');
        return;
    }

    playMorningBriefing();
}

// --- DYNAMIC LOCAL TIME GREETING CALCULATOR ---
function getTimeGreeting() {
    const hour = new Date().getHours();
    if (hour >= 4 && hour < 12) {
        return {
            period: 'morning',
            enSalutation: 'Good Morning Amit Sahu!',
            hiSalutation: 'शुभ प्रभात अमित साहू जी!',
            hinglishSalutation: 'Good Morning Amit Sahu ji!',
            btnText: 'Play Morning Briefing',
            hiContext: 'आज सुबह कुल 18 बुकिंग्स सक्रिय हैं। 12 गाड़ियां रास्ते में हैं और 3 गाड़ियां डिपो में उपलब्ध हैं। 2 ड्राइवर छुट्टी पर हैं।',
            hinglishContext: 'Aaj subah 18 bookings active hain. 12 gaadiyan raste me hain aur 3 gaadiyan available hain. 2 driver leave par hain.',
            enContext: 'Today 18 bookings are active. 12 vehicles on road, 3 available. 2 drivers on leave.'
        };
    } else if (hour >= 12 && hour < 17) {
        return {
            period: 'afternoon',
            enSalutation: 'Good Afternoon Amit Sahu!',
            hiSalutation: 'शुभ दोपहर अमित साहू जी!',
            hinglishSalutation: 'Good Afternoon Amit Sahu ji!',
            btnText: 'Play Afternoon Briefing',
            hiContext: 'आज दोपहर तक 18 बुकिंग्स का परिचालन सुचारु रूप से जारी है। 12 गाड़ियां ऑन-रोड हैं और 3 गाड़ियां तैयार हैं।',
            hinglishContext: 'Aaj dopahar tak 18 bookings me se 12 gaadiyan raste me hain aur 3 gaadiyan available hain.',
            enContext: 'This afternoon 18 bookings are active. 12 vehicles on road, 3 available at hub.'
        };
    } else if (hour >= 17 && hour < 22) {
        return {
            period: 'evening',
            enSalutation: 'Good Evening Amit Sahu!',
            hiSalutation: 'शुभ संध्या अमित साहू जी!',
            hinglishSalutation: 'Good Evening Amit Sahu ji!',
            btnText: 'Play Evening Briefing',
            hiContext: 'आज शाम की स्थिति: 18 बुकिंग्स में से अधिकांश डिलीवरी पूरी हो चुकी हैं। 12 गाड़ियां ऑन-रोड वापसी पर हैं।',
            hinglishContext: 'Aaj shaam 18 bookings me se delivery operations successfully chal rahe hain. 12 gaadiyan on-road hain.',
            enContext: 'Good evening! 18 bookings active today with evening return transits underway.'
        };
    } else {
        return {
            period: 'night',
            enSalutation: 'Late Night Shift • Amit Sahu!',
            hiSalutation: 'शुभ रात्रि अमित साहू जी!',
            hinglishSalutation: 'Good Night Amit Sahu ji!',
            btnText: 'Play Night Shift Briefing',
            hiContext: 'नाईट हाईवे टेलीमैटिक्स और सुरक्षा निगरानी सक्रिय है। 12 गाड़ियां ऑन-रोड हैं और 3 गाड़ियां डिपो में सुरक्षित हैं।',
            hinglishContext: 'Night shift telematics active hai. 12 gaadiyan highway par hain aur 3 gaadiyan depot me park hain.',
            enContext: 'Overnight highway telematics and emergency safety surveillance active.'
        };
    }
}

function applyTimeBasedGreeting() {
    const greeting = getTimeGreeting();

    // Update Hero Banner Quote
    const bannerQuote = document.getElementById('aiGreetingText');
    if (bannerQuote) {
        bannerQuote.innerText = `"${greeting.enSalutation} ${greeting.enContext} Heavy Rain alert on Raipur Route. 2 Insurance renewals due in 5 days."`;
    }

    // Update Header Button Text
    const btnText = document.getElementById('briefingBtnText');
    if (btnText) {
        btnText.innerText = greeting.btnText;
    }
}

function playMorningBriefing() {
    const greeting = getTimeGreeting();

    const briefPayload = {
        hindi: `${greeting.hiSalutation} घिडोरा ट्रांसपोर्ट कंट्रोल टॉवर में आपका स्वागत है। ${greeting.hiContext} रायपुर-धमतरी रूट पर भारी बारिश की चेतावनी है, और 2 गाड़ियों का इंश्योरेंस अगले 5 दिनों में एक्सपायर होने वाला है।`,
        hinglish: `${greeting.hinglishSalutation} ${greeting.hinglishContext} Raipur route par heavy rain ka alert hai, aur 2 gaadiyon ka insurance agle 5 dino me renew karna hai.`,
        indian_english: `${greeting.enSalutation} ${greeting.enContext} Heavy rainfall hazard alert on Raipur corridor, and 2 vehicle insurances due in 5 days.`
    };

    speakText(briefPayload);
    showToast(`Playing ${greeting.btnText} in Indian accent...`, 'info', 'AI Executive Briefing');
}

function stopMorningBriefing() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    appState.isSpeaking = false;
    setEqualizerState(false);
    const hud = document.getElementById('audioHudBanner');
    if (hud) hud.classList.add('hidden');
}

// --- GLOBAL VOICE COMMAND ASSISTANT ---
function initGlobalVoiceControls() {
    const btnMic = document.getElementById('btnMicGlobal');
    if (!btnMic) return;

    btnMic.addEventListener('click', openVoiceCommandModal);
}

function openVoiceCommandModal() {
    openModal('voiceCommandModal');

    const statusEl = document.getElementById('voiceModalStatus');
    const transcriptEl = document.getElementById('voiceModalTranscript');
    const visualEl = document.getElementById('voiceMicVisual');

    if (statusEl) statusEl.innerText = 'Listening for your command...';
    if (transcriptEl) transcriptEl.innerText = 'Speak naturally in Hindi, Hinglish or English...';
    if (visualEl) visualEl.style.animation = 'pulse-glow 1.5s infinite';

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        if (statusEl) statusEl.innerText = 'Speech Recognition not supported in this browser.';
        if (transcriptEl) transcriptEl.innerText = 'Please select any instant command below.';
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN';
    recognition.interimResults = false;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcriptEl) transcriptEl.innerText = `"${transcript}"`;
        if (statusEl) statusEl.innerText = 'Command recognized! Executing...';

        setTimeout(() => {
            closeModal('voiceCommandModal');
            switchSection('sec-ai-chat');
            handleUserQuery(transcript);
        }, 1200);
    };

    recognition.onerror = () => {
        if (statusEl) statusEl.innerText = 'Could not capture audio. Choose an instant command:';
    };

    try {
        recognition.start();
    } catch (e) {
        // Recognition already started or blocked
    }
}

function runVoiceCommandPrompt(actionKey) {
    closeModal('voiceCommandModal');

    switch (actionKey) {
        case 'play_morning_brief':
            playMorningBriefing();
            break;
        case 'check_revenue':
            openKpiModal('revenue');
            speakText("Aaj ka kul revenue ₹48,500 hai. Target ₹50,000 ka 97% achieve ho chuka hai.");
            break;
        case 'free_vehicles':
            switchSection('sec-gps');
            filterFleet('Idle', document.querySelector('.chip-btn:nth-child(3)'));
            speakText("Filhaal 3 vehicles khali hain. Tata Ace Super CG04EX8842 Dhamtari hub par ready condition me khadi hai.");
            break;
        case 'pending_payments':
            openKpiModal('payments');
            speakText("Total pending payment ₹22,000 hai. Customer Amit Sharma par ₹3,500 baaki hain.");
            break;
        case 'weather_advisory':
            switchSection('sec-fuel-weather');
            speakText("Kal Raipur-Dhamtari stretch par 85 mm heavy rainfall warning hai. AI delivery reschedule suggest karta hai.");
            break;
        default:
            switchSection('sec-ai-chat');
            break;
    }
}

// --- RENDER SMART ALERTS ---
function renderAlerts() {
    const miniContainer = document.getElementById('miniAlertsList');
    const fullGrid = document.getElementById('fullAlertsGrid');
    const countBadge = document.getElementById('alertCountBadge');
    const countTabAll = document.getElementById('countTabAll');
    
    if (miniContainer) miniContainer.innerHTML = '';
    if (fullGrid) fullGrid.innerHTML = '';

    if (countBadge) countBadge.innerText = appState.alerts.length;
    if (countTabAll) countTabAll.innerText = appState.alerts.length;

    if (appState.alerts.length === 0) {
        const emptyHtml = `
            <div style="text-align:center; padding: 24px 10px; color: var(--status-green);">
                <i class="fa-solid fa-circle-check" style="font-size: 36px; margin-bottom: 10px;"></i>
                <h4 style="color: #fff; font-size: 15px;">All Clear! Zero Active Alerts</h4>
                <p style="color: var(--text-muted); font-size: 12px;">All vehicles, compliance documents & drivers are 100% compliant.</p>
            </div>
        `;
        if (miniContainer) miniContainer.innerHTML = emptyHtml;
        if (fullGrid) fullGrid.innerHTML = emptyHtml;
        return;
    }

    appState.alerts.forEach((alt, idx) => {
        // Mini card html (for Section 1)
        if (idx < 3 && miniContainer) {
            const miniEl = document.createElement('div');
            miniEl.className = `alert-card-item type-${alt.type}`;
            miniEl.innerHTML = `
                <div class="alert-icon-box">${getAlertIcon(alt.category)}</div>
                <div class="alert-content">
                    <h5>${alt.title}</h5>
                    <p>${alt.description}</p>
                    <button class="alert-action-btn" onclick="triggerAlertAction('${alt.id}')">${alt.actionText}</button>
                </div>
            `;
            miniContainer.appendChild(miniEl);
        }

        // Full grid html (for Section 2)
        if (fullGrid) {
            const fullEl = document.createElement('div');
            fullEl.className = `glass-card alert-card-item type-${alt.type}`;
            fullEl.setAttribute('data-category', alt.category);
            fullEl.id = `fullAlertCard-${alt.id}`;
            fullEl.innerHTML = `
                <div class="alert-icon-box">${getAlertIcon(alt.category)}</div>
                <div class="alert-content">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <h5>${alt.title}</h5>
                        <span class="badge ${alt.type === 'critical' ? 'badge-critical' : alt.type === 'warning' ? 'badge-delayed' : 'badge-active'}">
                            ${alt.category.toUpperCase()}
                        </span>
                    </div>
                    <p style="margin: 6px 0 10px 0;">${alt.description}</p>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="btn-primary" style="padding: 6px 14px; font-size: 11px;" onclick="triggerAlertAction('${alt.id}')">
                            <i class="fa-solid fa-bolt"></i> ${alt.actionText}
                        </button>
                        <button class="btn-secondary" style="padding: 6px 10px; font-size: 11px;" onclick="dismissAlert('${alt.id}')">
                            <i class="fa-solid fa-check"></i> Mark Resolved
                        </button>
                    </div>
                </div>
            `;
            fullGrid.appendChild(fullEl);
        }
    });

    // Attach filter tab clicks
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.onclick = () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const cat = tab.getAttribute('data-filter');

            const allItems = fullGrid.querySelectorAll('.alert-card-item');
            allItems.forEach(item => {
                if (cat === 'all' || item.getAttribute('data-category') === cat) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        };
    });
}

function getAlertIcon(category) {
    switch (category) {
        case 'compliance': return '<i class="fa-solid fa-shield-halved text-rose"></i>';
        case 'driver': return '<i class="fa-solid fa-user-clock text-amber"></i>';
        case 'weather': return '<i class="fa-solid fa-cloud-showers-heavy text-cyan"></i>';
        case 'payment': return '<i class="fa-solid fa-money-bill-wave text-green"></i>';
        default: return '<i class="fa-solid fa-bell text-rose"></i>';
    }
}

// --- SMART ALERT ACTIONS & RESOLUTION WORKFLOWS ---
function triggerAlertAction(alertId) {
    const alertObj = appState.alerts.find(a => a.id === alertId);
    if (!alertObj) return;

    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalFooter = document.getElementById('modalFooter');

    modalTitle.innerHTML = `<i class="fa-solid fa-bolt text-cyan"></i> Resolve Alert: ${alertObj.title}`;

    if (alertObj.actionType === 'RENEW_INSURANCE') {
        modalBody.innerHTML = `
            <div>
                <p><strong>Vehicle:</strong> ${alertObj.reg} (Mahindra Pickup)</p>
                <p><strong>Insurer:</strong> National Insurance Co. Ltd</p>
                <p><strong>Current Expiry:</strong> 18 Sep 2026 (Due in 5 Days)</p>
                <div style="background: rgba(0,242,254,0.06); border: 1px solid var(--border-glass); border-radius: 8px; padding: 14px; margin: 14px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span>Comprehensive Commercial Cover (1 Year):</span>
                        <strong>₹12,288</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span>Goods Transit Liability Rider:</span>
                        <strong>₹1,100</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                        <span>GST (18%):</span>
                        <strong>₹1,112</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 15px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px; color: var(--status-green);">
                        <strong>Total Renewal Premium:</strong>
                        <strong>₹14,500</strong>
                    </div>
                </div>
                <div class="form-group">
                    <label>Select Corporate Payment Mode</label>
                    <select class="form-input" id="insPayMode">
                        <option value="HDFC Bank Corporate NetBanking">HDFC Corporate NetBanking (Ghidora A/C)</option>
                        <option value="ICICI Fastag & Insurance Fleet Wallet">ICICI Fleet Wallet</option>
                        <option value="UPI Auto-Debit">UPI AutoPay (amit.sahu@upi)</option>
                    </select>
                </div>
            </div>
        `;
        modalFooter.innerHTML = `
            <button class="btn-secondary" onclick="closeModal('actionModal')">Cancel</button>
            <button class="btn-primary" onclick="completeInsuranceRenewal('${alertId}')">
                <i class="fa-solid fa-shield-check"></i> Pay ₹14,500 & Renew Policy
            </button>
        `;
    } else if (alertObj.actionType === 'REST_DRIVER') {
        modalBody.innerHTML = `
            <div>
                <p><strong>Driver:</strong> Ramesh Kumar (Ph: +91-9826111111)</p>
                <p><strong>Assigned Vehicle:</strong> CG04 XX 1234 (Mahindra Pickup)</p>
                <p><strong>Telemetry Violation:</strong> 12 Hours continuous driving detected without mandatory 8-hour rest cycle.</p>
                <div style="background: rgba(255,23,68,0.1); border: 1px solid var(--status-rose); border-radius: 8px; padding: 12px; margin: 14px 0;">
                    <i class="fa-solid fa-triangle-exclamation text-rose"></i> <strong>Safety Protocol Mandate:</strong> Motor Vehicles Act requires mandatory 8 hours rest after 10 hours continuous transit to prevent highway accidents.
                </div>
                <div class="form-group">
                    <label>Notice Message to Driver Ramesh</label>
                    <textarea class="form-input" id="restNoticeText" rows="2" style="resize:none;">URGENT REST NOTICE: Driver Ramesh Kumar, pull vehicle CG04XX1234 into nearest designated rest plaza immediately. 8-hour rest lock activated in Ghidora AI app.</textarea>
                </div>
            </div>
        `;
        modalFooter.innerHTML = `
            <button class="btn-secondary" onclick="closeModal('actionModal')">Cancel</button>
            <button class="btn-primary" style="background: linear-gradient(135deg, #ff1744, #ff55b8);" onclick="completeDriverRestNotice('${alertId}')">
                <i class="fa-solid fa-paper-plane"></i> Dispatch Rest Notice & Lock Vehicle
            </button>
        `;
    } else if (alertObj.actionType === 'REMIND_PAYMENT') {
        modalBody.innerHTML = `
            <div>
                <p><strong>Customer:</strong> Amit Sharma (Ph: +91-9826199999)</p>
                <p><strong>Booking Ref:</strong> #GH-8092 (Furniture Transport Dhamtari → Raipur)</p>
                <p><strong>Outstanding Balance:</strong> <strong class="text-rose">₹3,500</strong> (6 Days Overdue)</p>
                <div style="background: rgba(0,230,118,0.08); border: 1px solid var(--status-green); border-radius: 8px; padding: 12px; margin: 14px 0;">
                    <i class="fa-brands fa-whatsapp text-green" style="font-size: 18px;"></i> <strong>WhatsApp Payment Link Template Ready</strong>
                    <div style="font-size: 12px; color: var(--text-muted); margin-top: 6px;">
                        "Namaste Amit ji! Ghidora Transport booking #GH-8092 ka balance ₹3,500 bacha hua hai. Kripya niche diye link par click karke UPI se pay karein: https://pay.ghidoratransport.in/inv/8092. Dhanyawad!"
                    </div>
                </div>
            </div>
        `;
        modalFooter.innerHTML = `
            <button class="btn-secondary" onclick="closeModal('actionModal')">Cancel</button>
            <button class="btn-primary" onclick="completePaymentReminder('${alertId}')">
                <i class="fa-brands fa-whatsapp"></i> Send WhatsApp Reminder
            </button>
        `;
    } else if (alertObj.actionType === 'ADVISE_DISPATCH') {
        modalBody.innerHTML = `
            <div>
                <p><strong>Route Corridor:</strong> Dhamtari → Raipur (NH 30)</p>
                <p><strong>Weather Warning:</strong> 85mm torrential rain starting tomorrow 6:00 AM.</p>
                <p><strong>AI Recommendation:</strong> Advance upcoming tomorrow morning dispatches to Today evening 8:00 PM to bypass highway waterlogging.</p>
                <div style="background: rgba(0,242,254,0.1); border: 1px solid var(--accent-cyan); border-radius: 8px; padding: 12px; margin: 14px 0;">
                    <i class="fa-solid fa-calendar-check text-cyan"></i> <strong>Automated Schedule Shift:</strong> 4 pending morning bookings will be pushed forward to tonight's dispatch queue.
                </div>
            </div>
        `;
        modalFooter.innerHTML = `
            <button class="btn-secondary" onclick="closeModal('actionModal')">Cancel</button>
            <button class="btn-primary" onclick="completeDispatchAdvise('${alertId}')">
                <i class="fa-solid fa-arrows-spin"></i> Apply Schedule Advance & Notify Customers
            </button>
        `;
    } else if (alertObj.actionType === 'SCHEDULE_RTO') {
        modalBody.innerHTML = `
            <div>
                <p><strong>Vehicle:</strong> CG04 YY 5678 (Ashok Leyland 16T Heavy Truck)</p>
                <p><strong>RTO Authority:</strong> RTO Raipur (Near Telibandha)</p>
                <p><strong>Required Inspection:</strong> Annual Fitness & Smoke Opacity Certification</p>
                <div class="form-group" style="margin-top: 14px;">
                    <label>Select Inspection Slot</label>
                    <select class="form-input" id="rtoSlotSelect">
                        <option value="Tomorrow 11:00 AM">Tomorrow 11:00 AM - 01:00 PM (Optimal)</option>
                        <option value="Day After Tomorrow 02:00 PM">Day After Tomorrow 02:00 PM - 04:00 PM</option>
                    </select>
                </div>
            </div>
        `;
        modalFooter.innerHTML = `
            <button class="btn-secondary" onclick="closeModal('actionModal')">Cancel</button>
            <button class="btn-primary" onclick="completeRtoSchedule('${alertId}')">
                <i class="fa-solid fa-calendar-check"></i> Book RTO Inspection Slot
            </button>
        `;
    } else if (alertObj.actionType === 'UPLOAD_PUC') {
        modalBody.innerHTML = `
            <div>
                <p><strong>Vehicle:</strong> CG04 EX 9900</p>
                <p><strong>Current PUC Status:</strong> Expired (Vehicle lock active)</p>
                <div style="border: 2px dashed rgba(255,255,255,0.2); border-radius: 8px; padding: 24px; text-align: center; margin: 14px 0; cursor: pointer;" onclick="document.getElementById('pucFileInput').click()">
                    <i class="fa-solid fa-cloud-arrow-up text-cyan" style="font-size: 32px; margin-bottom: 8px;"></i>
                    <p style="color: #fff; font-size: 13px;">Click to Upload New PUC Certificate (PDF / JPG)</p>
                    <span style="font-size: 11px; color: var(--text-muted);">AI OCR will automatically verify validity date & vehicle number</span>
                    <input type="file" id="pucFileInput" style="display:none;" onchange="handlePucFileSelected(this)">
                </div>
                <div id="pucUploadResult" class="hidden" style="background: rgba(0,230,118,0.1); border: 1px solid var(--status-green); padding: 10px; border-radius: 6px; font-size: 12px; color: var(--status-green);">
                    <i class="fa-solid fa-circle-check"></i> AI OCR Verified: Valid till 14 March 2027 (Emission: Bharat Stage VI Compliant)
                </div>
            </div>
        `;
        modalFooter.innerHTML = `
            <button class="btn-secondary" onclick="closeModal('actionModal')">Cancel</button>
            <button class="btn-primary" id="btnConfirmPuc" onclick="completePucUpload('${alertId}')">
                <i class="fa-solid fa-unlock"></i> Verify & Unlock Vehicle
            </button>
        `;
    } else {
        // Generic custom alert
        modalBody.innerHTML = `
            <div>
                <p><strong>Target:</strong> ${alertObj.reg || alertObj.driver || alertObj.customer || 'Fleet Operation'}</p>
                <p style="margin: 8px 0; color: var(--text-muted);">${alertObj.description}</p>
                <div style="background: rgba(0,230,118,0.1); padding: 12px; border-radius: 8px; border: 1px solid var(--status-green); margin-top: 15px;">
                    <i class="fa-solid fa-check-circle text-green"></i> Action: <strong>${alertObj.actionText}</strong>
                </div>
            </div>
        `;
        modalFooter.innerHTML = `
            <button class="btn-secondary" onclick="closeModal('actionModal')">Cancel</button>
            <button class="btn-primary" onclick="dismissAlert('${alertId}')">
                <i class="fa-solid fa-check"></i> Complete Action & Resolve
            </button>
        `;
    }

    openModal('actionModal');
}

function completeInsuranceRenewal(alertId) {
    closeModal('actionModal');
    dismissAlert(alertId, false);
    showToast('Insurance policy for CG04 XX 1234 successfully renewed for 1 Year (Policy #NIC-2026-99482). Premium ₹14,500 paid via HDFC Corporate.', 'success', 'Policy Renewed');
    speakText("Vehicle CG04 XX 1234 ka insurance successfully renew ho gaya hai.");
}

function completeDriverRestNotice(alertId) {
    closeModal('actionModal');
    dismissAlert(alertId, false);
    showToast('Mandatory 8-hour safety rest order sent to Driver Ramesh Kumar. Vehicle locked for safety.', 'warning', 'Safety Order Sent');
    speakText("Driver Ramesh ko 8 ghante ka mandatory rest notice bhej diya gaya hai.");
}

function completePaymentReminder(alertId) {
    closeModal('actionModal');
    dismissAlert(alertId, false);
    showToast('WhatsApp payment reminder & UPI invoice link sent to Customer Amit Sharma (+91-9826199999).', 'success', 'Reminder Sent');
    speakText("Customer Amit Sharma ko WhatsApp payment reminder bhej diya gaya hai.");
}

function completeDispatchAdvise(alertId) {
    closeModal('actionModal');
    dismissAlert(alertId, false);
    showToast('Route schedule updated: Tomorrow morning dispatches advanced to tonight to bypass heavy rain.', 'success', 'Schedule Advanced');
    speakText("Dhamtari-Raipur schedule advance kar diya gaya hai.");
}

function completeRtoSchedule(alertId) {
    closeModal('actionModal');
    dismissAlert(alertId, false);
    showToast('RTO Inspection booked at Raipur RTO for Tomorrow 11:00 AM (Appt #CG-RTO-4491).', 'success', 'RTO Slot Booked');
    speakText("Vehicle fitness inspection Raipur RTO me book ho gaya hai.");
}

function handlePucFileSelected(input) {
    if (input.files && input.files[0]) {
        const res = document.getElementById('pucUploadResult');
        if (res) {
            res.classList.remove('hidden');
            res.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> AI OCR scanning ${input.files[0].name}...`;
            setTimeout(() => {
                res.innerHTML = `<i class="fa-solid fa-circle-check"></i> AI OCR Verified: ${input.files[0].name} is Valid till 14 Sep 2027. BS-VI compliant.`;
            }, 800);
        }
    }
}

function completePucUpload(alertId) {
    closeModal('actionModal');
    dismissAlert(alertId, false);
    showToast('New PUC certificate verified & linked to vehicle CG04 EX 9900. Vehicle lock released.', 'success', 'Vehicle Unlocked');
    speakText("PUC certificate verify ho gaya hai aur vehicle unlock ho chuki hai.");
}

function dismissAlert(alertId, notify = true) {
    const idx = appState.alerts.findIndex(a => a.id === alertId);
    if (idx !== -1) {
        const removed = appState.alerts.splice(idx, 1)[0];
        renderAlerts();
        if (notify) {
            showToast(`Alert resolved: "${removed.title}"`, 'success', 'Resolved');
        }
    }
}

function resolveAllAlerts() {
    if (appState.alerts.length === 0) {
        showToast('No active alerts to resolve.', 'info', 'All Clear');
        return;
    }
    const count = appState.alerts.length;
    appState.alerts = [];
    renderAlerts();
    showToast(`All ${count} fleet alerts have been reviewed & marked resolved!`, 'success', 'All Resolved');
    speakText(`Sabhi ${count} alerts resolve ho gaye hain. Fleet 100% compliant hai.`);
}

function openCreateAlertModal() {
    openModal('createAlertModal');
}

function submitNewCustomAlert() {
    const category = document.getElementById('newAlertCategory').value;
    const severity = document.getElementById('newAlertSeverity').value;
    const title = document.getElementById('newAlertTitle').value.trim() || 'Manual Operational Alert';
    const target = document.getElementById('newAlertTarget').value.trim() || 'Fleet Item';
    const desc = document.getElementById('newAlertDesc').value.trim() || `Manual alert for ${target}.`;
    const actionText = document.getElementById('newAlertAction').value.trim() || 'Review Now';

    const newAlert = {
        id: 'alt-' + Date.now(),
        type: severity,
        category: category,
        title: title,
        reg: target,
        description: desc,
        actionText: actionText,
        actionType: 'CUSTOM'
    };

    appState.alerts.unshift(newAlert);
    renderAlerts();
    closeModal('createAlertModal');
    showToast(`New ${severity.toUpperCase()} alert added to control tower.`, 'success', 'Alert Created');
    speakText(`Naya alert add kiya gaya: ${title}`);
}

// --- KPI MODAL DRILLDOWN ---
function openKpiModal(kpiType) {
    const modalTitle = document.getElementById('kpiModalTitle');
    const modalBody = document.getElementById('kpiModalBody');
    if (!modalTitle || !modalBody) return;

    if (kpiType === 'bookings') {
        modalTitle.innerHTML = `<i class="fa-solid fa-boxes-stacked text-cyan"></i> Today's Active Bookings (${appState.bookingsList.length} Orders)`;
        let rows = appState.bookingsList.map(b => `
            <tr>
                <td><strong>${b.id}</strong></td>
                <td>${b.customer}</td>
                <td>${b.cargo}</td>
                <td>${b.from} → ${b.to}</td>
                <td class="text-green">₹${b.fare.toLocaleString('en-IN')}</td>
                <td>
                    <span class="status-badge ${b.status === 'Delivered' ? 'badge-active' : b.status === 'In Transit' ? 'badge-active' : 'badge-delayed'}">
                        ${b.status}
                    </span>
                </td>
            </tr>
        `).join('');

        modalBody.innerHTML = `
            <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; color: var(--text-muted);">Real-time shipment tracking for Chhattisgarh logistics network.</span>
                <span class="tag-ai">18 Total Today</span>
            </div>
            <table class="dispatches-table">
                <thead>
                    <tr>
                        <th>Booking ID</th>
                        <th>Customer</th>
                        <th>Cargo</th>
                        <th>Route</th>
                        <th>Fare</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    } else if (kpiType === 'revenue') {
        modalTitle.innerHTML = `<i class="fa-solid fa-sack-dollar text-green"></i> Today's Revenue Breakdown: ₹48,500`;
        modalBody.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 20px;">
                <div style="background: rgba(0,230,118,0.1); border: 1px solid var(--status-green); padding: 14px; border-radius: 8px;">
                    <div style="font-size: 11px; color: var(--text-muted);">Digital / UPI Collections</div>
                    <div style="font-size: 20px; font-weight: 700; color: var(--status-green);">₹32,000</div>
                    <div style="font-size: 11px; color: var(--text-muted);">66% of today's total</div>
                </div>
                <div style="background: rgba(0,242,254,0.1); border: 1px solid var(--accent-cyan); padding: 14px; border-radius: 8px;">
                    <div style="font-size: 11px; color: var(--text-muted);">Cash On Delivery (COD)</div>
                    <div style="font-size: 20px; font-weight: 700; color: var(--accent-cyan);">₹16,500</div>
                    <div style="font-size: 11px; color: var(--text-muted);">Collected by drivers</div>
                </div>
                <div style="background: rgba(255,23,68,0.1); border: 1px solid var(--status-rose); padding: 14px; border-radius: 8px;">
                    <div style="font-size: 11px; color: var(--text-muted);">Diesel Fuel Burn (Est)</div>
                    <div style="font-size: 20px; font-weight: 700; color: var(--status-rose);">-₹7,850</div>
                    <div style="font-size: 11px; color: var(--text-muted);">Today's fleet fuel cost</div>
                </div>
                <div style="background: rgba(121,40,202,0.15); border: 1px solid #7928ca; padding: 14px; border-radius: 8px;">
                    <div style="font-size: 11px; color: var(--text-muted);">Daily Target Progress</div>
                    <div style="font-size: 20px; font-weight: 700; color: #fff;">97.0%</div>
                    <div style="font-size: 11px; color: var(--status-green);">Target: ₹50,000</div>
                </div>
            </div>
            <h4 style="font-size: 13px; color: #fff; margin-bottom: 8px;">Top Performing Corridors Today</h4>
            <table class="dispatches-table">
                <thead>
                    <tr><th>Corridor</th><th>Trips</th><th>Earnings</th><th>Operating Margin</th></tr>
                </thead>
                <tbody>
                    <tr><td>Dhamtari ⇄ Raipur</td><td>8 Trips</td><td class="text-green">₹22,400</td><td>+36%</td></tr>
                    <tr><td>Raipur ⇄ Durg</td><td>6 Trips</td><td class="text-green">₹15,600</td><td>+31%</td></tr>
                    <tr><td>Raipur ⇄ Bilaspur</td><td>4 Trips</td><td class="text-green">₹10,500</td><td>+24%</td></tr>
                </tbody>
            </table>
        `;
    } else if (kpiType === 'drivers') {
        modalTitle.innerHTML = `<i class="fa-solid fa-id-card text-gold"></i> Fleet Driver Roster (${appState.driversList.length} Drivers)`;
        let rows = appState.driversList.map(d => `
            <tr>
                <td><strong>${d.name}</strong></td>
                <td>${d.vehicle}</td>
                <td><i class="fa-solid fa-star text-gold"></i> ${d.rating} (${d.trips} Trips)</td>
                <td>${d.status.includes('Leave') ? `<span class="text-rose">${d.status}</span>` : d.status.includes('Available') ? `<span class="text-green">${d.status}</span>` : `<span class="text-cyan">${d.status}</span>`}</td>
                <td>
                    <button class="btn-secondary" style="padding: 4px 10px; font-size: 11px;" onclick="window.location.href='tel:${d.phone}'; showToast('Dialing ${d.name}...', 'info')">
                        <i class="fa-solid fa-phone"></i> Call
                    </button>
                </td>
            </tr>
        `).join('');

        modalBody.innerHTML = `
            <table class="dispatches-table">
                <thead>
                    <tr>
                        <th>Driver Name</th>
                        <th>Assigned Vehicle</th>
                        <th>Rating & Experience</th>
                        <th>Current Duty Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    } else if (kpiType === 'payments') {
        modalTitle.innerHTML = `<i class="fa-solid fa-clock-rotate-left text-rose"></i> Pending Overdue Payments (₹${appState.pendingPaymentTotal.toLocaleString('en-IN')})`;
        let rows = appState.debtorsList.map(db => `
            <tr>
                <td><strong>${db.customer}</strong></td>
                <td>${db.bookingId}</td>
                <td>${db.route}</td>
                <td class="text-rose" style="font-weight: 700;">₹${db.amount.toLocaleString('en-IN')}</td>
                <td><span class="badge badge-critical">${db.daysOverdue} Days Overdue</span></td>
                <td>
                    <button class="btn-primary" style="padding: 4px 10px; font-size: 11px;" onclick="sendDebtorWhatsApp('${db.customer}', '${db.bookingId}', ${db.amount}, '${db.phone}')">
                        <i class="fa-brands fa-whatsapp"></i> Send Nudge
                    </button>
                </td>
            </tr>
        `).join('');

        modalBody.innerHTML = `
            <table class="dispatches-table">
                <thead>
                    <tr>
                        <th>Debtor Customer</th>
                        <th>Booking Ref</th>
                        <th>Route</th>
                        <th>Amount Due</th>
                        <th>Overdue Status</th>
                        <th>One-Click Nudge</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    }

    openModal('kpiModal');
}

function sendDebtorWhatsApp(customer, bookingId, amount, phone) {
    const text = encodeURIComponent(`Namaste ${customer} ji! Ghidora Transport booking #${bookingId} ka balance ₹${amount} pending hai. Kripya jald se jald clear karein. Payment Link: https://pay.ghidoratransport.in/${bookingId}. Thank you!`);
    window.open(`https://api.whatsapp.com/send?phone=${phone.replace(/[^0-9]/g, '')}&text=${text}`, '_blank');
    showToast(`WhatsApp reminder opened for ${customer} (₹${amount})`, 'success', 'WhatsApp Triggered');
}

// --- DISPATCH RECOMMENDATION ENGINE & LIVE DISPATCH TABLE ---
function initDispatchEngine() {
    const form = document.getElementById('dispatchForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const cargo = document.getElementById('cargoType').value;
            const weight = parseInt(document.getElementById('cargoWeight').value) || 700;
            const pickup = document.getElementById('pickupLoc').value || 'Dhamtari';
            const drop = document.getElementById('dropLoc').value || 'Raipur';

            calculateAIRecommendation(cargo, weight, pickup, drop);
        });
    }

    const btnAssignDispatch = document.getElementById('btnAssignDispatch');
    if (btnAssignDispatch) {
        btnAssignDispatch.addEventListener('click', executeDispatchAssignment);
    }
}

function calculateAIRecommendation(cargo, weight, pickup, drop) {
    const recVehicleName = document.getElementById('recVehicleName');
    const recVehicleReg = document.getElementById('recVehicleReg');
    const recVehicleReasons = document.getElementById('recVehicleReasons');
    const recDriverName = document.getElementById('recDriverName');
    const estFuelCost = document.getElementById('estFuelCost');
    const estDistance = document.getElementById('estDistance');

    if (weight > 2000) {
        // Heavy Truck
        recVehicleName.innerText = "Ashok Leyland 16T Heavy Truck";
        recVehicleReg.innerText = "CG 04 YY 5678";
        estFuelCost.innerText = "₹2,450";
        if (estDistance) estDistance.innerText = "82 KM";
        recVehicleReasons.innerHTML = `
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Heavy Load Capacity:</strong> Rated for ${weight} KG payload (Max 16 Ton)</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Chassis Heavy Reinforced:</strong> Safe for ${cargo}</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Available:</strong> Stationed at ${pickup} Logistics Hub</li>
        `;
        recDriverName.innerText = "Vikram Singh (Heavy Commercial Certified)";
    } else if (weight > 900) {
        // Eicher Truck
        recVehicleName.innerText = "Eicher Pro 2059";
        recVehicleReg.innerText = "CG 04 ZZ 9900";
        estFuelCost.innerText = "₹1,280";
        if (estDistance) estDistance.innerText = "76 KM";
        recVehicleReasons.innerHTML = `
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Mid-Weight Capacity:</strong> Rated for ${weight} KG ${cargo}</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Fast Turnaround:</strong> High highway speed</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Route Clearance:</strong> Cleared for ${pickup} → ${drop}</li>
        `;
        recDriverName.innerText = "Anil Yadav";
    } else {
        // Mahindra Pickup or Tata Ace
        recVehicleName.innerText = "Mahindra Pickup";
        recVehicleReg.innerText = "CG 04 EX 8842";
        estFuelCost.innerText = "₹840";
        if (estDistance) estDistance.innerText = "78 KM";
        recVehicleReasons.innerHTML = `
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Nearest Vehicle:</strong> Located 3.2 KM from ${pickup}</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Capacity:</strong> Perfect fit for ${weight} KG ${cargo} (Max 1.2 Ton)</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Lowest Fuel Cost:</strong> Best km/L efficiency for ${pickup} → ${drop}</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Status:</strong> Idle & Maintenance Cleared</li>
        `;
        recDriverName.innerText = "Ramesh Kumar";
    }

    showToast(`AI calculated optimal match: ${recVehicleName.innerText} + ${recDriverName.innerText}`, 'info', 'AI Recommendation');
    speakText(`AI suggests ${recVehicleName.innerText} and driver ${recDriverName.innerText} for ${cargo}.`);
}

function executeDispatchAssignment() {
    const cargo = document.getElementById('cargoType').value;
    const weight = document.getElementById('cargoWeight').value || '700';
    const pickup = document.getElementById('pickupLoc').value || 'Dhamtari';
    const drop = document.getElementById('dropLoc').value || 'Raipur';
    const vName = document.getElementById('recVehicleName').innerText;
    const vReg = document.getElementById('recVehicleReg').innerText;
    const dName = document.getElementById('recDriverName').innerText;
    const cost = document.getElementById('estFuelCost').innerText;

    const newDispId = 'GH-DSP-' + Math.floor(1000 + Math.random() * 9000);

    appState.dispatches.unshift({
        id: newDispId,
        cargo: `${cargo} (${weight} KG)`,
        vehicle: `${vName} (${vReg})`,
        driver: dName,
        route: `${pickup} → ${drop}`,
        dieselCost: cost,
        status: 'Dispatched',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });

    renderDispatchTable();
    showToast(`Dispatch ${newDispId} officially assigned to ${vName} & Driver ${dName}!`, 'success', 'Dispatch Assigned');
    speakText(`Dispatch assigned successfully to ${vName}. Trip started.`);
}

function renderDispatchTable() {
    const tbody = document.getElementById('dispatchTableBody');
    if (!tbody) return;

    tbody.innerHTML = appState.dispatches.map(d => `
        <tr>
            <td><strong>${d.id}</strong></td>
            <td>${d.cargo}</td>
            <td>${d.vehicle}</td>
            <td>${d.driver}</td>
            <td>${d.route}</td>
            <td class="text-green">${d.dieselCost}</td>
            <td>
                <span class="status-badge ${d.status === 'Dispatched' ? 'badge-active' : d.status === 'In Transit' ? 'badge-active' : 'badge-delayed'}">
                    ${d.status}
                </span>
            </td>
            <td>
                <button class="btn-secondary" style="padding: 3px 8px; font-size: 10px;" onclick="trackDispatchOnMap('${d.id}')">
                    <i class="fa-solid fa-location-crosshairs"></i> Track
                </button>
            </td>
        </tr>
    `).join('');
}

function trackDispatchOnMap(dispId) {
    switchSection('sec-gps');
    showToast(`Centering telematics camera on dispatch ${dispId}`, 'info', 'GPS Tracking');
}

// --- GPS TELEMATICS MAP (LEAFLET.JS) ---
function initLeafletMap() {
    const mapElement = document.getElementById('telematicsMap');
    if (!mapElement) return;

    // Center map around Raipur / Chhattisgarh highway
    mapInstance = L.map('telematicsMap').setView([21.2514, 81.6296], 10);

    // High-contrast clean dark slate telematics tiles without Carto API key watermark
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
        maxZoom: 16
    }).addTo(mapInstance);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
        attribution: '',
        maxZoom: 16
    }).addTo(mapInstance);

    // Draw active route polyline (Dhamtari to Raipur to Bilaspur)
    const routeCoords = [
        [20.6971, 81.5492], // Dhamtari
        [20.9500, 81.6000], // Kurud
        [21.1904, 81.2849], // Durg bypass
        [21.2514, 81.6296], // Raipur Hub
        [21.5000, 81.8000], // Simga
        [22.0797, 82.1409]  // Bilaspur
    ];

    routePolyline = L.polyline(routeCoords, { color: '#00f2fe', weight: 3, dashArray: '6, 6', opacity: 0.8 }).addTo(mapInstance);

    renderFleetListAndMarkers();

    // Simulation buttons
    const btnToggleMotion = document.getElementById('btnToggleMotion');
    if (btnToggleMotion) {
        btnToggleMotion.addEventListener('click', toggleRealtimeGpsMotion);
    }

    const btnSimStop = document.getElementById('btnSimulateStop');
    if (btnSimStop) {
        btnSimStop.addEventListener('click', triggerStopSimulation);
    }

    const btnSimDev = document.getElementById('btnSimulateDeviate');
    if (btnSimDev) {
        btnSimDev.addEventListener('click', triggerDeviateSimulation);
    }
}

function renderFleetListAndMarkers() {
    const fleetListEl = document.getElementById('fleetList');
    if (!fleetListEl || !mapInstance) return;
    fleetListEl.innerHTML = '';

    appState.vehicles.forEach(v => {
        // Custom Marker
        const color = v.status === 'Stopped' ? '#ff1744' : v.status === 'Idle' ? '#ffd700' : '#00e676';
        const markerIcon = L.divIcon({
            className: 'custom-map-pin',
            html: `
                <div style="background:${color}; width:16px; height:16px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 12px ${color}; display: flex; align-items:center; justify-content:center;">
                    <span style="width:4px; height:4px; background:#fff; border-radius:50%;"></span>
                </div>
            `,
            iconSize: [16, 16],
            iconAnchor: [8, 8]
        });

        if (vehicleMarkers[v.id]) {
            mapInstance.removeLayer(vehicleMarkers[v.id]);
        }

        const marker = L.marker([v.lat, v.lng], { icon: markerIcon }).addTo(mapInstance);
        marker.bindPopup(`
            <div style="color:#0f172a; font-family:sans-serif; font-size:12px; line-height:1.5;">
                <strong style="font-size:13px; color:#0284c7;">${v.model} (${v.reg})</strong><br>
                Driver: <strong>${v.driver}</strong> (${v.phone})<br>
                Speed: <strong>${v.speed}</strong> | Status: <strong style="color:${color};">${v.status}</strong><br>
                Route: ${v.route}
            </div>
        `);
        vehicleMarkers[v.id] = marker;

        // Fleet List Entry
        const item = document.createElement('div');
        item.className = 'fleet-item';
        item.setAttribute('data-status', v.status);
        item.innerHTML = `
            <div class="fleet-item-head">
                <span><strong>${v.model}</strong> (${v.reg})</span>
                <span class="${v.status === 'Stopped' ? 'text-rose' : v.status === 'Idle' ? 'text-amber' : 'text-green'}">${v.status}</span>
            </div>
            <div style="color:var(--text-muted); font-size:11px; margin-top:2px;">
                Driver: ${v.driver} • Speed: ${v.speed}
            </div>
            <div style="color:var(--accent-cyan); font-size:10px; margin-top:2px;">
                <i class="fa-solid fa-route"></i> ${v.route}
            </div>
        `;
        item.addEventListener('click', () => {
            mapInstance.flyTo([v.lat, v.lng], 13);
            marker.openPopup();
        });
        fleetListEl.appendChild(item);
    });
}

function filterFleet(statusFilter, btnEl) {
    document.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');

    const items = document.querySelectorAll('.fleet-item');
    items.forEach(item => {
        const itemStatus = item.getAttribute('data-status');
        if (statusFilter === 'all' || itemStatus === statusFilter) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });

    // Also toggle map markers visibility or zoom
    if (statusFilter !== 'all') {
        const matchingVehicle = appState.vehicles.find(v => v.status === statusFilter);
        if (matchingVehicle && mapInstance) {
            mapInstance.panTo([matchingVehicle.lat, matchingVehicle.lng]);
            if (vehicleMarkers[matchingVehicle.id]) {
                vehicleMarkers[matchingVehicle.id].openPopup();
            }
        }
    }
}

function toggleRealtimeGpsMotion() {
    const btn = document.getElementById('btnToggleMotion');
    const textSpan = document.getElementById('motionBtnText');

    if (appState.isMotionActive) {
        clearInterval(appState.motionInterval);
        appState.isMotionActive = false;
        if (textSpan) textSpan.innerText = 'Start Realtime GPS Motion';
        if (btn) btn.classList.remove('pulse-glow');
        showToast('Realtime vehicle simulation paused.', 'info', 'GPS Simulation');
    } else {
        appState.isMotionActive = true;
        if (textSpan) textSpan.innerText = 'Pause GPS Motion';
        if (btn) btn.classList.add('pulse-glow');
        showToast('Realtime live motion simulation started! Vehicles moving on highway.', 'success', 'GPS Active');
        speakText('Realtime vehicle motion simulation shuru ho gayi hai.');

        appState.motionInterval = setInterval(() => {
            // Animate running vehicles slightly along the route
            appState.vehicles.forEach(v => {
                if (v.status === 'Running') {
                    v.lat += (Math.random() - 0.48) * 0.005;
                    v.lng += (Math.random() - 0.48) * 0.005;
                    if (vehicleMarkers[v.id]) {
                        vehicleMarkers[v.id].setLatLng([v.lat, v.lng]);
                    }
                }
            });
        }, 1500);
    }
}

function triggerStopSimulation() {
    showToast('🚨 UNEXPECTED STOP: Vehicle CG04YY5678 stopped for 25 mins at bypass KM 42. Contacting Driver Vikram Singh.', 'danger', 'Stop Alert');
    speakText('Unexpected stop detected! Vehicle CG04YY5678 stopped for 25 minutes.');

    // Add to alerts
    const newAlert = {
        id: 'alt-' + Date.now(),
        type: 'critical',
        category: 'driver',
        title: '25-Min Unscheduled Halt',
        reg: 'CG04YY5678',
        description: 'Vehicle CG04YY5678 stationary for 25 minutes at bypass KM 42. Driver Vikram Singh not answering automated ping.',
        actionText: 'Contact Highway Patrol / Driver',
        actionType: 'REST_DRIVER'
    };
    appState.alerts.unshift(newAlert);
    renderAlerts();
}

function triggerDeviateSimulation() {
    showToast('⚠️ ROUTE DEVIATION: Vehicle CG04ZZ9900 deviated 4.2 KM from approved Raipur-Bilaspur highway route.', 'warning', 'Deviation Alert');
    speakText('Route deviation alert! Vehicle CG04ZZ9900 deviated 4.2 kilometer from approved route.');

    const newAlert = {
        id: 'alt-' + Date.now(),
        type: 'warning',
        category: 'weather',
        title: 'Route Deviation Detected',
        reg: 'CG04ZZ9900',
        description: 'Vehicle CG04ZZ9900 took unauthorized detour 4.2 KM away from NH-130.',
        actionText: 'Re-route Vehicle to Corridor',
        actionType: 'CUSTOM'
    };
    appState.alerts.unshift(newAlert);
    renderAlerts();
}

// --- FUEL & WEATHER DECISION ENGINE ---
function activateAlternateRouteB() {
    const cardB = document.getElementById('cardRouteB');
    const textEl = document.getElementById('btnRouteBText');
    if (cardB && textEl) {
        textEl.innerText = 'Active Route Enforced (Saving ₹350/Trip)';
        showToast('Route B (Bypass Corridor) enforced across all Raipur → Durg dispatches. Estimated diesel saving: ₹350 per trip.', 'success', 'Route B Enforced');
        speakText('Alternate Route B enforce kar diya gaya hai. Har trip par ₹350 diesel ki bachat hogi.');
    }
}

function investigateFuelAnomaly(reg) {
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalFooter = document.getElementById('modalFooter');

    modalTitle.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-rose"></i> Fuel Anomaly Investigation: ${reg}`;
    modalBody.innerHTML = `
        <div>
            <p><strong>Vehicle:</strong> ${reg} (Eicher Pro 2059)</p>
            <p><strong>Driver:</strong> Anil Yadav (Ph: +91-9826444444)</p>
            <p><strong>Timestamp:</strong> Today 11:14 AM - 11:24 AM (Simga Bypass Halt)</p>
            <div style="background: rgba(255,23,68,0.1); border: 1px solid var(--status-rose); border-radius: 8px; padding: 14px; margin: 14px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span>Starting Tank Volume (11:14 AM):</span>
                    <strong>68.0 Litres</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span>Ending Tank Volume (11:24 AM):</span>
                    <strong>56.0 Litres</strong>
                </div>
                <div style="display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px; color: var(--status-rose); font-weight: 700;">
                    <span>Unaccounted Fuel Drop:</span>
                    <span>-12.0 Litres (Estimated Loss: ₹1,134)</span>
                </div>
            </div>
            <p style="font-size: 12px; color: var(--text-muted);">
                AI Telematics Diagnostic: Speed was 0 km/h during drop. Tank cap sensor triggered opening. Probable fuel siphoning event or ultrasonic sensor misalignment.
            </p>
        </div>
    `;
    modalFooter.innerHTML = `
        <button class="btn-secondary" onclick="closeModal('actionModal')">Close</button>
        <button class="btn-primary" style="background: linear-gradient(135deg, #ff1744, #ff55b8);" onclick="lockFuelTankRemote('${reg}')">
            <i class="fa-solid fa-lock"></i> Send Remote IoT Tank Lock
        </button>
    `;
    openModal('actionModal');
}

function lockFuelTankRemote(reg) {
    closeModal('actionModal');
    showToast(`Remote IoT tank lock engaged for vehicle ${reg}. Driver Anil notified.`, 'success', 'IoT Lockdown');
    speakText(`Vehicle ${reg} ka remote tank lock activate kar diya gaya hai.`);
}

function pingDriverFuelAlert(name, phone) {
    showToast(`Automated SMS alert & voice call pinged to driver ${name} (${phone}) regarding fuel anomaly.`, 'info', 'Driver Pinged');
}

function openWeatherBroadcastModal() {
    openModal('weatherBroadcastModal');
}

function sendWeatherBroadcastAction() {
    const hazard = document.getElementById('hazardTypeInput').value;
    closeModal('weatherBroadcastModal');
    showToast(`Weather broadcast successfully dispatched via SMS & Push to 12 on-road drivers in Chhattisgarh corridor!`, 'success', 'Broadcast Sent');
    speakText("Sabhi 12 on-road drivers ko heavy rain warning broadcast bhej diya gaya hai.");
}

// --- BI & PREDICTIVE ANALYTICS TIME RANGE SWITCHER ---
function initCharts() {
    // Chart 1: Revenue Forecast
    const ctxRevenue = document.getElementById('revenueForecastChart');
    if (ctxRevenue) {
        revenueChartInstance = new Chart(ctxRevenue, {
            type: 'line',
            data: {
                labels: ['May', 'Jun', 'Jul', 'Aug (Curr)', 'Sep (Pred)', 'Oct (Pred)'],
                datasets: [
                    {
                        label: 'Actual Revenue (₹)',
                        data: [620000, 710000, 780000, 815400, null, null],
                        borderColor: '#00f2fe',
                        backgroundColor: 'rgba(0, 242, 254, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'AI Forecasted Revenue (₹8,50,000)',
                        data: [null, null, null, 815400, 850000, 910000],
                        borderColor: '#00e676',
                        borderDash: [5, 5],
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    // Chart 2: Monthly Expenses
    const ctxExpense = document.getElementById('expenseChart');
    if (ctxExpense) {
        expenseChartInstance = new Chart(ctxExpense, {
            type: 'doughnut',
            data: {
                labels: ['Diesel Fuel (+10%)', 'Driver Salaries', 'Maintenance & Tyres', 'Insurance & Permits'],
                datasets: [{
                    data: [198000, 120000, 54000, 28000],
                    backgroundColor: ['#ff1744', '#00e5ff', '#7928ca', '#ffd700']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
            }
        });
    }
}

function switchAnalyticsRange(rangeKey, btnEl) {
    document.querySelectorAll('.time-tab').forEach(b => b.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');

    const predLabel = document.getElementById('analyticsPredLabel');
    const predVal = document.getElementById('analyticsPredVal');
    const surgeLabel = document.getElementById('analyticsSurgeLabel');
    const surgeVal = document.getElementById('analyticsSurgeVal');

    if (!revenueChartInstance || !expenseChartInstance) return;

    if (rangeKey === 'today') {
        predLabel.innerText = "Today's Revenue Pace";
        predVal.innerText = "₹48,500";
        surgeLabel.innerText = "Remaining Today Target";
        surgeVal.innerText = "₹1,500 to Reach ₹50k";

        revenueChartInstance.data.labels = ['6 AM', '9 AM', '12 PM', '3 PM', '6 PM', '9 PM (Pred)'];
        revenueChartInstance.data.datasets[0].data = [4200, 12500, 24000, 36000, 48500, null];
        revenueChartInstance.data.datasets[1].data = [null, null, null, null, 48500, 52000];
        revenueChartInstance.update();

        expenseChartInstance.data.datasets[0].data = [7850, 4200, 1800, 950];
        expenseChartInstance.update();

    } else if (rangeKey === 'week') {
        predLabel.innerText = "This Week's Expected Revenue";
        predVal.innerText = "₹3,40,000";
        surgeLabel.innerText = "Surge vs Last Week";
        surgeVal.innerText = "+14.5% Higher";

        revenueChartInstance.data.labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat (Pred)', 'Sun (Pred)'];
        revenueChartInstance.data.datasets[0].data = [44000, 48000, 52000, 46000, 48500, null, null];
        revenueChartInstance.data.datasets[1].data = [null, null, null, null, 48500, 55000, 58000];
        revenueChartInstance.update();

        expenseChartInstance.data.datasets[0].data = [46000, 28000, 12000, 6000];
        expenseChartInstance.update();

    } else if (rangeKey === 'month') {
        predLabel.innerText = "Expected Next Month Revenue";
        predVal.innerText = "₹8,50,000";
        surgeLabel.innerText = "Booking Surge Expected";
        surgeVal.innerText = "+18% Increase";

        revenueChartInstance.data.labels = ['May', 'Jun', 'Jul', 'Aug (Curr)', 'Sep (Pred)', 'Oct (Pred)'];
        revenueChartInstance.data.datasets[0].data = [620000, 710000, 780000, 815400, null, null];
        revenueChartInstance.data.datasets[1].data = [null, null, null, 815400, 850000, 910000];
        revenueChartInstance.update();

        expenseChartInstance.data.datasets[0].data = [198000, 120000, 54000, 28000];
        expenseChartInstance.update();

    } else if (rangeKey === '6m') {
        predLabel.innerText = "H2 Projected Revenue";
        predVal.innerText = "₹52,00,000";
        surgeLabel.innerText = "6-Month Growth Rate";
        surgeVal.innerText = "+26.8% CAGR";

        revenueChartInstance.data.labels = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'];
        revenueChartInstance.data.datasets[0].data = [580000, 600000, 620000, 710000, 780000, 815400];
        revenueChartInstance.data.datasets[1].data = [null, null, null, null, null, null];
        revenueChartInstance.update();

    } else if (rangeKey === 'year') {
        predLabel.innerText = "FY 2026 Projected Revenue";
        predVal.innerText = "₹1.15 Crore";
        surgeLabel.innerText = "Year-over-Year Growth";
        surgeVal.innerText = "+38.4% YoY";

        revenueChartInstance.data.labels = ['Q1 25', 'Q2 25', 'Q3 25', 'Q4 25', 'Q1 26', 'Q2 26 (Pred)'];
        revenueChartInstance.data.datasets[0].data = [1450000, 1680000, 1920000, 2240000, 2650000, null];
        revenueChartInstance.data.datasets[1].data = [null, null, null, null, 2650000, 3100000];
        revenueChartInstance.update();
    }

    showToast(`Analytics view switched to ${rangeKey.toUpperCase()}`, 'info', 'BI Filter');
}

// --- AI MANAGER CHAT BOT ---
function initChatManager() {
    const btnSend = document.getElementById('btnSendChat');
    const input = document.getElementById('chatInputText');
    const btnMic = document.getElementById('btnVoiceInputChat');

    if (btnSend && input) {
        btnSend.addEventListener('click', () => {
            if (input.value.trim()) {
                handleUserQuery(input.value.trim());
                input.value = '';
            }
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                handleUserQuery(input.value.trim());
                input.value = '';
            }
        });
    }

    if (btnMic && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN';

        btnMic.addEventListener('click', () => {
            btnMic.style.color = '#00f2fe';
            btnMic.classList.add('pulse-glow');
            recognition.start();
        });

        recognition.onresult = (e) => {
            btnMic.style.color = '#fff';
            btnMic.classList.remove('pulse-glow');
            const text = e.results[0][0].transcript;
            handleUserQuery(text);
        };

        recognition.onerror = () => {
            btnMic.style.color = '#fff';
            btnMic.classList.remove('pulse-glow');
        };
    }
}

function sendQuickQuery(query) {
    handleUserQuery(query);
}

function handleUserQuery(queryText) {
    const chatContainer = document.getElementById('chatMessages');
    if (!chatContainer) return;

    // Add user bubble
    const userDiv = document.createElement('div');
    userDiv.className = 'msg msg-user';
    userDiv.innerHTML = `
        <div class="msg-avatar"><i class="fa-solid fa-user"></i></div>
        <div class="msg-bubble">${queryText}</div>
    `;
    chatContainer.appendChild(userDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // AI Response Logic (Multilingual Indian Voice & Diction)
    let responseObj = {
        hindi: "मुझे इसका रिकॉर्ड सत्यापित करने दीजिए।",
        hinglish: "Mujhe iska record verify karne dijiye.",
        indian_english: "Let me verify this record in the fleet telemetry."
    };

    const q = queryText.toLowerCase();
    if (q.includes('booking') || q.includes('बुकिंग')) {
        responseObj = {
            hindi: "आज कुल 18 बुकिंग्स हुई हैं। जिसमें से 12 गाड़ियां रास्ते में हैं और कुल ₹48,500 का राजस्व प्राप्त हुआ है।",
            hinglish: "Aaj total 18 bookings hui hain. Jisme se 12 active transit me hain aur ₹48,500 ka revenue earn hua hai.",
            indian_english: "A total of 18 bookings have been registered today, generating ₹48,500 in revenue with 12 active transits."
        };
    } else if (q.includes('गाड़ी') || q.includes('vehicle') || q.includes('खाली') || q.includes('free') || q.includes('available')) {
        responseObj = {
            hindi: "फिलहाल 3 गाड़ियां डिपो में उपलब्ध हैं। सबसे नज़दीक टाटा ऐस सुपर (CG04EX8842) धमतरी हब पर तुरंत लोड के लिए तैयार खड़ी है।",
            hinglish: "Filhaal 3 vehicles available hain. Sabse paas Tata Ace Super (CG04EX8842) Dhamtari hub par ready condition me khadi hai.",
            indian_english: "Currently 3 vehicles are available. Tata Ace Super (CG04EX8842) is standing ready at Dhamtari hub."
        };
    } else if (q.includes('कमाई') || q.includes('earning') || q.includes('revenue') || q.includes('profit')) {
        responseObj = {
            hindi: "इस महीने सबसे ज्यादा कमाई महिंद्रा पिकअप (CG04XX1234) ने की है — कुल ₹2,45,000!",
            hinglish: "Sabse zyada kamai Mahindra Pickup (CG04XX1234) ne ki hai — Total ₹2,45,000 is mahine!",
            indian_english: "The highest earning vehicle this month is Mahindra Pickup (CG04XX1234), generating ₹2,45,000."
        };
    } else if (q.includes('payment') || q.includes('pending') || q.includes('बाकी') || q.includes('debt')) {
        responseObj = {
            hindi: "कुल पेंडिंग पेमेंट ₹22,000 है। ग्राहक अमित शर्मा पर ₹3,500 और रायपुर टिंबर मार्ट पर ₹8,200 बकाया हैं।",
            hinglish: "Total Pending Payment ₹22,000 hai. Customer Amit Sharma par ₹3,500 aur Raipur Timber par ₹8,200 baaki hain.",
            indian_english: "Total outstanding payment is ₹22,000, including ₹3,500 from customer Amit Sharma."
        };
    } else if (q.includes('weather') || q.includes('barish') || q.includes('बारिश') || q.includes('rain')) {
        responseObj = {
            hindi: "कल धमतरी-रायपुर मार्ग पर 85 मिलीमीटर भारी बारिश की चेतावनी है। मौसम को देखते हुए आज शाम ही माल रवाना करने की सलाह है।",
            hinglish: "Kal Dhamtari-Raipur belt par 85 mm heavy rainfall alert hai. Early dispatch recommend kiya gaya hai.",
            indian_english: "Heavy rain warning with 85mm rainfall is active on Dhamtari-Raipur belt for tomorrow. Early dispatch recommended."
        };
    } else if (q.includes('raipur') || q.includes('route') || q.includes('रूट')) {
        responseObj = {
            hindi: "धमतरी-रायपुर कॉरिडोर हमारी कंपनी का सबसे अधिक लाभ देने वाला रूट है, जिसमें 34.2% ऑपरेटिंग मार्जिन है।",
            hinglish: "Dhamtari-Raipur corridor humara sabse profitable route hai (+34.2% operating margin).",
            indian_english: "Dhamtari to Raipur corridor is our most profitable route with a 34.2% operating profit margin."
        };
    } else if (q.includes('diesel') || q.includes('fuel') || q.includes('तेल')) {
        responseObj = {
            hindi: "आज छत्तीसगढ़ में डीजल का भाव ₹94.50 प्रति लीटर है। पूरे फ्लीट का औसत माइलेज 12.4 किलोमीटर प्रति लीटर है।",
            hinglish: "Aaj Chhattisgarh me diesel rate ₹94.50 per litre hai. Fleet mileage average 12.4 km/L chal raha hai.",
            indian_english: "Today's diesel rate in Chhattisgarh is ₹94.50 per litre, with a fleet mileage average of 12.4 km/L."
        };
    } else {
        responseObj = {
            hindi: `आपके प्रश्न '${queryText}' की रिपोर्ट: कंट्रोल टॉवर 96% स्वास्थ्य क्षमता पर चल रहा है। 12 गाड़ियां सुरक्षित परिचालन में हैं।`,
            hinglish: `Aapke sawal '${queryText}' ka summary: Company telematics 96% health par chal rahi hai. 12 gaadiyan on-road hain, koi breakdown nahi hai.`,
            indian_english: `Telemetry summary for '${queryText}': Fleet is operating normally at 96% health rating with 12 vehicles on road.`
        };
    }

    setTimeout(() => {
        const displayText = voiceConfig.style === 'hindi' ? responseObj.hindi : (voiceConfig.style === 'indian_english' ? responseObj.indian_english : responseObj.hinglish);

        const botDiv = document.createElement('div');
        botDiv.className = 'msg msg-bot';
        botDiv.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-bubble">${displayText}</div>
        `;
        chatContainer.appendChild(botDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        speakText(responseObj);
    }, 450);
}

// --- AUTOMATED REPORTS GENERATOR ---
function generateReportPreview() {
    const freq = document.getElementById('reportFreq').value;
    const subTitle = document.getElementById('reportHeaderSubtitle');
    const periodText = document.getElementById('reportPeriodText');
    const timeText = document.getElementById('reportGeneratedTime');
    const body = document.getElementById('reportSheetBody');

    if (timeText) timeText.innerText = new Date().toLocaleString();

    if (freq === 'Daily') {
        if (subTitle) subTitle.innerText = "Daily Operations & Dispatch Summary";
        if (periodText) periodText.innerText = "Today (" + new Date().toLocaleDateString() + ")";
        if (body) {
            body.innerHTML = `
                <h4>1. Operations & Financial Performance (Daily)</h4>
                <table class="report-table">
                    <thead><tr><th>Metric</th><th>Target</th><th>Actual Achieved</th><th>Variance</th></tr></thead>
                    <tbody>
                        <tr><td>Bookings Dispatched</td><td>20 Bookings</td><td><strong>18 Bookings</strong></td><td><span class="text-amber">90% Target</span></td></tr>
                        <tr><td>Gross Daily Revenue</td><td>₹50,000</td><td><strong>₹48,500</strong></td><td><span class="text-green">97% Target</span></td></tr>
                        <tr><td>Estimated Fuel Expense</td><td>₹7,500</td><td><strong>₹7,850</strong></td><td><span class="text-rose">+₹350 Detour</span></td></tr>
                        <tr><td>Net Daily Profit</td><td>₹42,500</td><td><strong>₹40,650</strong></td><td><span class="text-green">Profitable</span></td></tr>
                    </tbody>
                </table>
                <h4>2. Active Vehicles On Road Today</h4>
                <table class="report-table">
                    <thead><tr><th>Reg Number</th><th>Model</th><th>Route</th><th>Trips Today</th></tr></thead>
                    <tbody>
                        <tr><td>CG04XX1234</td><td>Mahindra Pickup</td><td>Dhamtari → Raipur</td><td>3 Trips (₹9,800)</td></tr>
                        <tr><td>CG04YY5678</td><td>Ashok Leyland 16T</td><td>Raipur → Durg</td><td>2 Trips (₹14,500)</td></tr>
                        <tr><td>CG04ZZ9900</td><td>Eicher Pro 2059</td><td>Raipur → Bilaspur</td><td>2 Trips (₹11,600)</td></tr>
                    </tbody>
                </table>
            `;
        }
    } else if (freq === 'Weekly') {
        if (subTitle) subTitle.innerText = "Weekly Logistics & Revenue Performance";
        if (periodText) periodText.innerText = "Current Week";
        if (body) {
            body.innerHTML = `
                <h4>1. Operations & Financial Performance (Weekly)</h4>
                <table class="report-table">
                    <thead><tr><th>Metric</th><th>Target</th><th>Actual Achieved</th><th>Variance</th></tr></thead>
                    <tbody>
                        <tr><td>Weekly Bookings</td><td>110 Bookings</td><td><strong>124 Bookings</strong></td><td><span class="text-green">+12.7%</span></td></tr>
                        <tr><td>Weekly Gross Revenue</td><td>₹3,00,000</td><td><strong>₹3,42,000</strong></td><td><span class="text-green">+14% Growth</span></td></tr>
                        <tr><td>Weekly Diesel Spend</td><td>₹45,000</td><td><strong>₹49,200</strong></td><td><span class="text-rose">+9.3%</span></td></tr>
                        <tr><td>Net Operating Margin</td><td>28%</td><td><strong>31.2%</strong></td><td><span class="text-green">High Margin</span></td></tr>
                    </tbody>
                </table>
            `;
        }
    } else if (freq === 'Monthly') {
        if (subTitle) subTitle.innerText = "AI Automated Executive Report";
        if (periodText) periodText.innerText = "August 2026";
        if (body) {
            body.innerHTML = `
                <h4>1. Operations & Financial Performance (Monthly)</h4>
                <table class="report-table">
                    <thead><tr><th>Metric</th><th>Target</th><th>Actual Achieved</th><th>Variance / AI Remark</th></tr></thead>
                    <tbody>
                        <tr><td>Total Completed Bookings</td><td>450 Bookings</td><td><strong>492 Bookings</strong></td><td><span class="text-green">+9.3% Higher Demand</span></td></tr>
                        <tr><td>Gross Operational Revenue</td><td>₹7,50,000</td><td><strong>₹8,15,400</strong></td><td><span class="text-green">Target Exceeded</span></td></tr>
                        <tr><td>Total Diesel Fuel Expense</td><td>₹1,80,000</td><td><strong>₹1,98,000</strong></td><td><span class="text-rose">+10% Route detour increase</span></td></tr>
                        <tr><td>Net Operational Profit</td><td>₹5,70,000</td><td><strong>₹6,17,400</strong></td><td><span class="text-green">+8.3% Profit Margin</span></td></tr>
                    </tbody>
                </table>
                <h4>2. Top Vehicle Performance</h4>
                <table class="report-table">
                    <thead><tr><th>Vehicle Number</th><th>Category</th><th>Total Trips</th><th>Total Revenue Earned</th></tr></thead>
                    <tbody>
                        <tr><td>CG04XX1234</td><td>Mahindra Pickup</td><td>84 Trips</td><td><strong>₹2,45,000</strong> (Highest Earned)</td></tr>
                        <tr><td>CG04EX8842</td><td>Tata Ace Super</td><td>72 Trips</td><td><strong>₹1,95,000</strong></td></tr>
                        <tr><td>CG04YY5678</td><td>Ashok Leyland 16T</td><td>38 Trips</td><td><strong>₹3,75,400</strong></td></tr>
                    </tbody>
                </table>
            `;
        }
    } else if (freq === 'Yearly') {
        if (subTitle) subTitle.innerText = "Annual Enterprise Logistics Report";
        if (periodText) periodText.innerText = "Financial Year 2025 - 2026";
        if (body) {
            body.innerHTML = `
                <h4>1. Annual Financial Performance (FY 25-26)</h4>
                <table class="report-table">
                    <thead><tr><th>Metric</th><th>Target</th><th>Actual Achieved</th><th>YoY Growth</th></tr></thead>
                    <tbody>
                        <tr><td>Total Trips Completed</td><td>4,800 Trips</td><td><strong>5,420 Trips</strong></td><td><span class="text-green">+24.5% YoY</span></td></tr>
                        <tr><td>Annual Gross Turnover</td><td>₹85,00,000</td><td><strong>₹98,40,000</strong></td><td><span class="text-green">+28.2% YoY</span></td></tr>
                        <tr><td>Fleet Operating Costs</td><td>₹26,00,000</td><td><strong>₹28,10,000</strong></td><td><span class="text-amber">Controlled</span></td></tr>
                        <tr><td>Net Enterprise Profit</td><td>₹59,00,000</td><td><strong>₹70,30,000</strong></td><td><span class="text-green">+32.6% YoY</span></td></tr>
                    </tbody>
                </table>
            `;
        }
    }

    showToast(`Generated ${freq} Executive Report preview.`, 'success', 'Report Generated');
}

function downloadReport(format) {
    const freq = document.getElementById('reportFreq').value;
    if (format === 'CSV') {
        const rows = [
            ["Metric", "Target", "Achieved", "Variance"],
            ["Total Bookings", "450 Bookings", "492 Bookings", "+9.3% Demand"],
            ["Gross Revenue", "₹7,50,000", "₹8,15,400", "+8.7% Target Exceeded"],
            ["Diesel Fuel Expense", "₹1,80,000", "₹1,98,000", "+10% Detour Increase"],
            ["Net Operational Profit", "₹5,70,000", "₹6,17,400", "+8.3% Margin"],
            ["", "", "", ""],
            ["Top Vehicle", "Category", "Trips", "Revenue"],
            ["CG04XX1234", "Mahindra Pickup", "84 Trips", "₹2,45,000"],
            ["CG04EX8842", "Tata Ace Super", "72 Trips", "₹1,95,000"],
            ["CG04YY5678", "Ashok Leyland 16T", "38 Trips", "₹3,75,400"]
        ];

        let csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.join(",")).join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `Ghidora_${freq}_Report_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast(`CSV report downloaded successfully!`, 'success', 'CSV Exported');
    } else {
        showToast('Opening clean print layout for PDF generation...', 'info', 'Exporting PDF');
        window.print();
    }
}

// --- GENERIC MODAL CONTROLS ---
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function closeModal(modalId) {
    if (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('hidden');
    } else {
        document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.add('hidden'));
    }
}

// Close on backdrop click or ESC key
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop')) {
        e.target.classList.add('hidden');
    }
});

window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.add('hidden'));
    }
});

// --- VOICE & INDIAN ACCENT CUSTOMIZATION HANDLERS ---
function openVoiceSettingsModal() {
    populateSystemVoicesList();
    openModal('voiceSettingsModal');
}

function populateSystemVoicesList() {
    const sel = document.getElementById('voiceSystemSelector');
    if (!sel || !('speechSynthesis' in window)) return;

    const voices = window.speechSynthesis.getVoices();
    sel.innerHTML = '<option value="auto">Auto Detect Best Indian Voice (Recommended)</option>';

    voices.forEach((v, idx) => {
        const isIndian = (v.lang && (v.lang.toLowerCase().includes('in') || v.lang.toLowerCase().includes('hi'))) ||
                         (v.name && (v.name.toLowerCase().includes('india') || v.name.toLowerCase().includes('hindi') || v.name.toLowerCase().includes('heera') || v.name.toLowerCase().includes('neerja') || v.name.toLowerCase().includes('prabhat') || v.name.toLowerCase().includes('swara')));
        const opt = document.createElement('option');
        opt.value = v.voiceURI || v.name;
        opt.text = `${isIndian ? '🇮🇳 ' : ''}${v.name} (${v.lang})`;
        if (voiceConfig.selectedVoiceUri === (v.voiceURI || v.name)) {
            opt.selected = true;
        }
        sel.appendChild(opt);
    });
}

function selectVoicePreset(preset) {
    voiceConfig.preset = preset;
    document.querySelectorAll('.voice-preset-card').forEach(c => c.classList.remove('active'));

    const badgeLabel = document.getElementById('voiceBadgeLabel');
    const rateSlider = document.getElementById('voiceRateSlider');
    const pitchSlider = document.getElementById('voicePitchSlider');
    const sampleText = document.getElementById('voiceTestSampleText');

    if (preset === 'priya') {
        const c = document.getElementById('presetPriya');
        if (c) c.classList.add('active');
        voiceConfig.pitch = 1.08;
        voiceConfig.rate = 0.95;
        if (badgeLabel) badgeLabel.innerText = "Voice: Priya (Indian Female)";
        if (sampleText) sampleText.innerText = '"नमस्ते अमित जी! मैं प्रिया हूँ। आपकी ट्रांसपोर्ट कंपनी का कार्य सुचारु रूप से चल रहा है।"';
    } else if (preset === 'rohan') {
        const c = document.getElementById('presetRohan');
        if (c) c.classList.add('active');
        voiceConfig.pitch = 0.88;
        voiceConfig.rate = 0.93;
        if (badgeLabel) badgeLabel.innerText = "Voice: Rohan (Indian Male)";
        if (sampleText) sampleText.innerText = '"नमस्ते अमित साहू जी! मैं रोहन हूँ, घिडोरा कंट्रोल टॉवर से लाइव रिपोर्टिंग।"';
    } else if (preset === 'hindi') {
        const c = document.getElementById('presetHindi');
        if (c) c.classList.add('active');
        voiceConfig.pitch = 1.0;
        voiceConfig.rate = 0.92;
        if (badgeLabel) badgeLabel.innerText = "Voice: Swara (Shuddh Hindi)";
        if (sampleText) sampleText.innerText = '"नमस्ते अमित जी! आज 18 बुकिंग्स और 12 गाड़ियां सड़क पर परिचालन में हैं।"';
    }

    if (rateSlider) {
        rateSlider.value = voiceConfig.rate;
        document.getElementById('voiceRateVal').innerText = voiceConfig.rate + 'x';
    }
    if (pitchSlider) {
        pitchSlider.value = voiceConfig.pitch;
        document.getElementById('voicePitchVal').innerText = voiceConfig.pitch + 'x';
    }
}

function updateVoiceLanguageStyle(style) {
    voiceConfig.style = style;
    const sampleText = document.getElementById('voiceTestSampleText');
    if (style === 'hindi') {
        if (sampleText) sampleText.innerText = '"नमस्ते अमित साहू जी! आज कुल 18 बुकिंग्स सक्रिय हैं और कंपनी 96% हेल्थ पर चल रही है।"';
    } else if (style === 'indian_english') {
        if (sampleText) sampleText.innerText = '"Good day Amit Sahu sir! Ghidora AI Control Tower telemetry is operating at 96% health."';
    } else {
        if (sampleText) sampleText.innerText = '"Namaste Amit ji! Main Ghidora AI Assistant hoon, Indian voice me live updates de rahi hoon."';
    }
}

function onManualVoiceSelect(val) {
    voiceConfig.selectedVoiceUri = val;
}

function testActiveVoiceSound() {
    const rateEl = document.getElementById('voiceRateSlider');
    const pitchEl = document.getElementById('voicePitchSlider');
    if (rateEl) voiceConfig.rate = parseFloat(rateEl.value);
    if (pitchEl) voiceConfig.pitch = parseFloat(pitchEl.value);

    const testPayload = {
        hindi: "नमस्ते अमित साहू जी! मैं आपकी घिडोरा एआई ट्रांसपोर्ट असिस्टेंट हूँ। मैं भारतीय आवाज़ और सही उच्चारण में बात कर सकती हूँ।",
        hinglish: "Namaste Amit ji! Main Ghidora AI Voice Assistant hoon, aur main Indian accent me report karti hoon.",
        indian_english: "Hello Amit Sahu sir! This is Ghidora AI Transport Control Tower, speaking in natural Indian accent."
    };

    speakText(testPayload);
    showToast('Testing selected Indian voice tone...', 'info', 'Testing Voice');
}

function saveVoiceSettings() {
    const rateEl = document.getElementById('voiceRateSlider');
    const pitchEl = document.getElementById('voicePitchSlider');
    const styleEl = document.getElementById('voiceLanguageStyle');
    if (rateEl) voiceConfig.rate = parseFloat(rateEl.value);
    if (pitchEl) voiceConfig.pitch = parseFloat(pitchEl.value);
    if (styleEl) voiceConfig.style = styleEl.value;

    closeModal('voiceSettingsModal');
    showToast('Indian Voice configuration saved & applied across all control tower announcements!', 'success', 'Voice Updated');
    speakText({
        hindi: "भारतीय आवाज़ की सेटिंग्स सफलतापूर्वक सेव हो गई हैं।",
        hinglish: "Indian voice settings successfully save ho gayi hain.",
        indian_english: "Indian voice settings have been successfully applied."
    });
}

// --- DRIVER SOBRIETY BIOMETRIC SCANNER ---
function triggerBiometricVerificationAll() {
    playChimeSound();
    showToast('Pushing biometric sobriety test & breathalyzer sync to all 4 on-road drivers...', 'info', 'Biometric Sync');

    setTimeout(() => {
        showToast('All 4 Drivers Cleared: Ramesh Kumar (0.00% BAC), Sunil Verma (0.00% BAC), Vikram Singh (0.00% BAC), Anil Yadav (0.00% BAC). Zero alcohol detected.', 'success', 'Sobriety 100% Clear');
        speakText({
            hindi: "सभी ड्राइवरों का बायोमेट्रिक और ब्रीथलाइज़र टेस्ट पास हो गया है। कोई नशा या अनहोनी नहीं पाई गई।",
            hinglish: "Sabhi drivers ka sobriety breathalyzer test clear hai. 0.00% alcohol detected.",
            indian_english: "All 4 drivers have passed the biometric sobriety test with 0.00% BAC."
        });
    }, 1200);
}

// --- FASTAG FLEET WALLET TOP-UP ---
function openFastagTopupModal() {
    openModal('fastagTopupModal');
}

function completeFastagRecharge() {
    const amt = parseInt(document.getElementById('fastagRechargeAmt').value) || 5000;
    closeModal('fastagTopupModal');

    const balDisplay = document.getElementById('fastagBalanceDisplay');
    const newBal = 14250 + amt;
    if (balDisplay) balDisplay.innerText = `₹${newBal.toLocaleString('en-IN')}`;

    playChimeSound();
    showToast(`Fastag Fleet Wallet recharged with ₹${amt.toLocaleString('en-IN')} via UPI AutoPay! New balance: ₹${newBal.toLocaleString('en-IN')}`, 'success', 'Fastag Recharged');
    speakText({
        hindi: `फ़ास्टैग वॉलेट में ₹${amt} का तुरंत रिचार्ज हो गया है। नया बैलेंस ₹${newBal} है।`,
        hinglish: `Fastag wallet me ₹${amt} ka instant recharge successful ho gaya hai.`,
        indian_english: `Fleet Fastag wallet recharged with rupees ${amt}. New balance is ${newBal}.`
    });
}

// --- HIGHWAY FLEET SOS RESCUE PROTOCOL ---
function openSosModal() {
    openModal('sosModal');
}

function dispatchSosRescueNow() {
    const veh = document.getElementById('sosVehicleSelect').value;
    const type = document.getElementById('sosTypeSelect').value;
    closeModal('sosModal');

    playChimeSound();
    showToast(`🚨 HIGHWAY SOS ACTIVE: Heavy Towing Crane & Highway Patrol dispatched to ${veh} at Bypass KM 42! GPS pinpoint transmitted.`, 'danger', 'SOS Dispatched');
    speakText({
        hindi: `आपातकालीन सूचना: गाड़ी ${veh} के लिए हाईवे क्रेन और पेट्रोलिंग टीम रवाना कर दी गई है।`,
        hinglish: `Emergency alert! Vehicle ${veh} ke liye highway crane aur patrol van dispatch kar di gayi hai.`,
        indian_english: `Emergency protocol active. Highway rescue crane dispatched to vehicle ${veh}.`
    });

    // Add critical SOS alert to active alert list
    const sosAlert = {
        id: 'alt-' + Date.now(),
        type: 'critical',
        category: 'driver',
        title: `🚨 HIGHWAY SOS: ${veh} Rescue Active`,
        reg: veh,
        description: `Highway Rescue Crane dispatched from Durg Hub to Bypass KM 42. ETA: 18 Minutes. Driver alerted.`,
        actionText: 'Track Rescue Crane',
        actionType: 'CUSTOM'
    };
    appState.alerts.unshift(sosAlert);
    renderAlerts();
}

// --- 🌌 3D ANIMATED BACKGROUND PARTICLE ENGINE (from Image 3 / Quote Form) ---
function initBackgroundParticles() {
    const canvas = document.getElementById('controlTowerBgCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const count = 50;

    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.7,
            vy: (Math.random() - 0.5) * 0.7,
            radius: Math.random() * 2 + 1.2,
            color: i % 2 === 0 ? 'rgba(0, 242, 254, ' : 'rgba(255, 0, 127, '
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < count; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color + '0.75)';
            ctx.shadowBlur = 10;
            ctx.shadowColor = p.color + '1)';
            ctx.fill();

            for (let j = i + 1; j < count; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.hypot(dx, dy);

                if (dist < 135) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(0, 242, 254, ${0.16 * (1 - dist / 135)})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(animate);
    }

    animate();
}

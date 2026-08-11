/* ==========================================================================
   GHIDORA AI TRANSPORT CONTROL TOWER - MAIN APPLICATION LOGIC
   ========================================================================== */

// --- DATA STORES & STATE ---
const appState = {
    bookingsToday: 18,
    revenueToday: 48500,
    runningVehicles: 12,
    availableVehicles: 3,
    availableDrivers: 5,
    pendingPaymentTotal: 22000,
    businessHealth: 96,
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
    vehicles: [
        { id: 'v1', reg: 'CG04XX1234', model: 'Mahindra Pickup', cap: '1.2 Ton', status: 'Running', lat: 21.2514, lng: 81.6296, driver: 'Ramesh K', earnings: 245000 },
        { id: 'v2', reg: 'CG04EX8842', model: 'Tata Ace Super', cap: '850 KG', status: 'Idle', lat: 20.6971, lng: 81.5492, driver: 'Sunil Verma', earnings: 195000 },
        { id: 'v3', reg: 'CG04YY5678', model: 'Ashok Leyland 16T', cap: '16 Ton', status: 'Stopped', lat: 21.1904, lng: 81.2849, driver: 'Vikram Singh', earnings: 375400 },
        { id: 'v4', reg: 'CG04ZZ9900', model: 'Eicher Pro 2059', cap: '3.5 Ton', status: 'Running', lat: 21.0971, lng: 81.7492, driver: 'Anil Yadav', earnings: 182000 }
    ]
};

let mapInstance = null;
let vehicleMarkers = {};

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    renderAlerts();
    initLeafletMap();
    initCharts();
    initDispatchEngine();
    initChatManager();
    initGlobalVoiceControls();

    // Auto-play morning brief synthesis button
    document.getElementById('btnVoiceGreet').addEventListener('click', playMorningBriefing);
});

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

// --- VOICE SYNTHESIS (NATURAL INDIAN HINDI VOICE) ---
let cachedHindiVoice = null;

function loadHindiVoice() {
    if (!('speechSynthesis' in window)) return;
    const voices = window.speechSynthesis.getVoices();
    cachedHindiVoice = voices.find(v => 
        (v.lang && (v.lang.includes('hi') || v.lang.includes('hi-IN') || v.lang.includes('hi_IN'))) ||
        (v.name && (v.name.includes('Hindi') || v.name.includes('Swara') || v.name.includes('Hemant') || v.name.includes('Kalpana') || v.name.includes('Google हिन्दी')))
    ) || voices.find(v => v.lang && v.lang.includes('IN')) || voices[0];
}

if ('speechSynthesis' in window) {
    loadHindiVoice();
    window.speechSynthesis.onvoiceschanged = loadHindiVoice;
}

function speakText(text) {
    if (!('speechSynthesis' in window)) {
        alert('Voice synthesis not supported in this browser.');
        return;
    }

    window.speechSynthesis.cancel(); // Stop active speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'hi-IN';
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    if (!cachedHindiVoice) loadHindiVoice();
    if (cachedHindiVoice) utterance.voice = cachedHindiVoice;

    window.speechSynthesis.speak(utterance);
}

function playMorningBriefing() {
    const briefText = "गुड मॉर्निंग अमित साहू जी! आज आपकी कंपनी में कुल 18 बुकिंग्स एक्टिव हैं। 12 गाड़ियां रास्ते में हैं और 3 गाड़ियां खाली खड़ी हैं। 2 ड्राइवर छुट्टी पर हैं। रायपुर रूट पर भारी बारिश की चेतावनी है, और 2 गाड़ियों का इंश्योरेंस अगले 5 दिनों में एक्सपायर होने वाला है।";
    speakText(briefText);
}

// --- GLOBAL VOICE COMMAND RECOGNITION ---
function initGlobalVoiceControls() {
    const btnMic = document.getElementById('btnMicGlobal');
    
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        btnMic.title = "Speech Recognition not supported";
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN'; // Hindi / Hinglish recognition
    recognition.interimResults = false;

    btnMic.addEventListener('click', () => {
        speakText("Aapka command sun raha hoon...");
        btnMic.classList.add('pulse-glow');
        btnMic.querySelector('span').innerText = 'Listening...';
        recognition.start();
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        btnMic.classList.remove('pulse-glow');
        btnMic.querySelector('span').innerText = 'Voice Command';

        // Process question in AI Manager Bot
        switchSection('sec-ai-chat');
        handleUserQuery(transcript);
    };

    recognition.onerror = () => {
        btnMic.classList.remove('pulse-glow');
        btnMic.querySelector('span').innerText = 'Voice Command';
    };
}

// --- RENDER SMART ALERTS ---
function renderAlerts() {
    const miniContainer = document.getElementById('miniAlertsList');
    const fullGrid = document.getElementById('fullAlertsGrid');
    
    miniContainer.innerHTML = '';
    fullGrid.innerHTML = '';

    appState.alerts.forEach((alt, idx) => {
        // Mini card html
        if (idx < 3) {
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

        // Full grid html
        const fullEl = document.createElement('div');
        fullEl.className = `glass-card alert-card-item type-${alt.type}`;
        fullEl.setAttribute('data-category', alt.category);
        fullEl.innerHTML = `
            <div class="alert-icon-box">${getAlertIcon(alt.category)}</div>
            <div class="alert-content">
                <h5>${alt.title}</h5>
                <p>${alt.description}</p>
                <div style="margin-top: 10px;">
                    <button class="btn-primary" style="padding: 6px 12px; font-size: 11px;" onclick="triggerAlertAction('${alt.id}')">
                        <i class="fa-solid fa-bolt"></i> ${alt.actionText}
                    </button>
                </div>
            </div>
        `;
        fullGrid.appendChild(fullEl);
    });

    document.getElementById('alertCountBadge').innerText = appState.alerts.length;

    // Filter tab handler
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
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
        });
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

function triggerAlertAction(alertId) {
    const alertObj = appState.alerts.find(a => a.id === alertId);
    if (!alertObj) return;

    const modal = document.getElementById('actionModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.innerText = `Action Resolution: ${alertObj.title}`;
    
    let content = `
        <div style="padding: 10px 0;">
            <p><strong>Item Target:</strong> ${alertObj.reg || alertObj.driver || alertObj.customer || alertObj.route}</p>
            <p style="margin: 8px 0; color: var(--text-muted);">${alertObj.description}</p>
            <div style="background: rgba(0,230,118,0.1); padding: 12px; border-radius: 8px; border: 1px solid var(--status-green); margin-top: 15px;">
                <i class="fa-solid fa-check-circle text-green"></i> <strong>AI Action Processing:</strong> Executing automated workflow for <em>${alertObj.actionText}</em>.
            </div>
        </div>
    `;
    modalBody.innerHTML = content;
    modal.classList.remove('hidden');

    speakText(`Executing action for ${alertObj.title}`);
}

function closeModal() {
    document.getElementById('actionModal').classList.add('hidden');
}

// --- DISPATCH ENGINE (CARGO & RECOMMENDATION) ---
function initDispatchEngine() {
    const form = document.getElementById('dispatchForm');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const cargo = document.getElementById('cargoType').value;
        const weight = parseInt(document.getElementById('cargoWeight').value) || 700;
        const pickup = document.getElementById('pickupLoc').value;
        const drop = document.getElementById('dropLoc').value;

        calculateAIRecommendation(cargo, weight, pickup, drop);
    });

    document.getElementById('btnAssignDispatch').addEventListener('click', () => {
        alert('✅ Dispatch Confirmed! Mahindra Pickup & Driver Ramesh Kumar assigned to Booking.');
        speakText('Booking assigned successfully to Mahindra Pickup and Driver Ramesh.');
    });
}

function calculateAIRecommendation(cargo, weight, pickup, drop) {
    const recVehicleName = document.getElementById('recVehicleName');
    const recVehicleReg = document.getElementById('recVehicleReg');
    const recVehicleReasons = document.getElementById('recVehicleReasons');
    const recDriverName = document.getElementById('recDriverName');
    const estFuelCost = document.getElementById('estFuelCost');

    if (weight > 1500) {
        // High weight cargo recommendation
        recVehicleName.innerText = "Ashok Leyland 16T Heavy Truck";
        recVehicleReg.innerText = "CG 04 YY 5678";
        estFuelCost.innerText = "₹2,450";
        recVehicleReasons.innerHTML = `
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Heavy Load Capacity:</strong> Rated for ${weight} KG payload (Max 16 Ton)</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Chassis Heavy Reinforced:</strong> Safe for construction material</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Available:</strong> Stationed at ${pickup} Logistics Hub</li>
        `;
        recDriverName.innerText = "Vikram Singh (Heavy Commercial Certified)";
    } else {
        // Light / Medium cargo recommendation (e.g. 700 KG Furniture)
        recVehicleName.innerText = "Mahindra Pickup";
        recVehicleReg.innerText = "CG 04 EX 8842";
        estFuelCost.innerText = "₹840";
        recVehicleReasons.innerHTML = `
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Nearest Vehicle:</strong> Located 3.2 KM from ${pickup}</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Capacity:</strong> Perfect fit for ${weight} KG ${cargo} (Max 1.2 Ton)</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Lowest Fuel Cost:</strong> Best km/L efficiency for ${pickup} → ${drop}</li>
            <li><i class="fa-solid fa-circle-check text-green"></i> <strong>Status:</strong> Idle & Maintenance Cleared</li>
        `;
        recDriverName.innerText = "Ramesh Kumar";
    }

    speakText(`AI recommends ${recVehicleName.innerText} and driver ${recDriverName.innerText} for ${weight} KG ${cargo}.`);
}

// --- GPS TELEMATICS MAP (LEAFLET.JS) ---
function initLeafletMap() {
    const mapElement = document.getElementById('telematicsMap');
    if (!mapElement) return;

    // Center map around Raipur / Chhattisgarh region
    mapInstance = L.map('telematicsMap').setView([21.2514, 81.6296], 10);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 18
    }).addTo(mapInstance);

    // Draw active route polyline (Dhamtari to Raipur)
    const routeCoords = [
        [20.6971, 81.5492], // Dhamtari
        [20.9500, 81.6000], 
        [21.1904, 81.2849], // Durg
        [21.2514, 81.6296]  // Raipur
    ];

    L.polyline(routeCoords, { color: '#00f2fe', weight: 4, dashArray: '8, 8' }).addTo(mapInstance);

    // Add Vehicle Markers
    renderFleetListAndMarkers();

    // Attach simulation buttons
    document.getElementById('btnSimulateStop').addEventListener('click', triggerStopSimulation);
    document.getElementById('btnSimulateDeviate').addEventListener('click', triggerDeviateSimulation);
}

function renderFleetListAndMarkers() {
    const fleetListEl = document.getElementById('fleetList');
    fleetListEl.innerHTML = '';

    appState.vehicles.forEach(v => {
        // Map Marker
        const markerIcon = L.divIcon({
            className: 'custom-map-pin',
            html: `<div style="background:${v.status === 'Stopped' ? '#ff1744' : '#00e676'}; width:14px; height:14px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 10px ${v.status === 'Stopped' ? '#ff1744' : '#00e676'};"></div>`,
            iconSize: [14, 14]
        });

        const marker = L.marker([v.lat, v.lng], { icon: markerIcon }).addTo(mapInstance);
        marker.bindPopup(`
            <div style="color:#000; font-family:sans-serif;">
                <strong>${v.model} (${v.reg})</strong><br>
                Driver: ${v.driver}<br>
                Status: <strong>${v.status}</strong>
            </div>
        `);
        vehicleMarkers[v.id] = marker;

        // Fleet List Entry
        const item = document.createElement('div');
        item.className = 'fleet-item';
        item.innerHTML = `
            <div class="fleet-item-head">
                <span>${v.model} (${v.reg})</span>
                <span class="${v.status === 'Stopped' ? 'text-rose' : 'text-green'}">${v.status}</span>
            </div>
            <div style="color:var(--text-muted); font-size:11px;">
                Driver: ${v.driver} | Capacity: ${v.cap}
            </div>
        `;
        item.addEventListener('click', () => {
            mapInstance.flyTo([v.lat, v.lng], 13);
            marker.openPopup();
        });
        fleetListEl.appendChild(item);
    });
}

function triggerStopSimulation() {
    alert('🚨 UNEXPECTED STOP DETECTED!\nVehicle CG04YY5678 stopped for 25 Minutes at unexpected location (Bypass KM 42). AI recommends contacting Driver Vikram Singh.');
    speakText('Unexpected stop detected! Vehicle CG04YY5678 stopped for 25 minutes.');
}

function triggerDeviateSimulation() {
    alert('⚠️ ROUTE DEVIATION DETECTED!\nVehicle CG04ZZ9900 deviated 4.2 KM from assigned route Raipur-Bilaspur highway.');
    speakText('Route deviation alert! Vehicle CG04ZZ9900 deviated from assigned route.');
}

// --- BI ANALYTICS CHARTS (CHART.JS) ---
function initCharts() {
    // Chart 1: Revenue Forecast
    const ctxRevenue = document.getElementById('revenueForecastChart');
    if (ctxRevenue) {
        new Chart(ctxRevenue, {
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
        new Chart(ctxExpense, {
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
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
            }
        });
    }
}

// --- AI MANAGER CHAT BOT ---
function initChatManager() {
    const btnSend = document.getElementById('btnSendChat');
    const input = document.getElementById('chatInputText');
    const btnMic = document.getElementById('btnVoiceInputChat');

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

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN';

        btnMic.addEventListener('click', () => {
            btnMic.style.color = '#00f2fe';
            recognition.start();
        });

        recognition.onresult = (e) => {
            btnMic.style.color = '#ff55b8';
            const text = e.results[0][0].transcript;
            handleUserQuery(text);
        };
    }
}

function sendQuickQuery(query) {
    handleUserQuery(query);
}

function handleUserQuery(queryText) {
    const chatContainer = document.getElementById('chatMessages');

    // Add user bubble
    const userDiv = document.createElement('div');
    userDiv.className = 'msg msg-user';
    userDiv.innerHTML = `
        <div class="msg-avatar"><i class="fa-solid fa-user"></i></div>
        <div class="msg-bubble">${queryText}</div>
    `;
    chatContainer.appendChild(userDiv);

    // AI Response Logic
    let responseText = "Mujhe abhi iska exact data check karna padega.";

    const q = queryText.toLowerCase();
    if (q.includes('booking') || q.includes('बुकिंग')) {
        responseText = "Aaj total 18 bookings hui hain. Jisme se 12 active transit me hain aur ₹48,500 ka revenue earn hua hai.";
    } else if (q.includes('गाड़ी') || q.includes('vehicle') || q.includes('खाली')) {
        responseText = "Filhaal 3 vehicles available hain. Tata Ace Super (CG04EX8842) Dhamtari hub par ready condition me hai.";
    } else if (q.includes('कमाई') || q.includes('earning') || q.includes('revenue')) {
        responseText = "Sabse zyada kamai Mahindra Pickup (CG04XX1234) ne ki hai — Total ₹2,45,000 is mahine.";
    } else if (q.includes('payment') || q.includes('pending') || q.includes('बाकी')) {
        responseText = "Total Pending Payment ₹22,000 hai. Customer Amit Sharma par ₹3,500 baaki hain.";
    } else {
        responseText = `Aapke request '${queryText}' ka snapshot: Company health 96% par operational hai. 12 vehicles active duty par hain.`;
    }

    setTimeout(() => {
        const botDiv = document.createElement('div');
        botDiv.className = 'msg msg-bot';
        botDiv.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-bubble">${responseText}</div>
        `;
        chatContainer.appendChild(botDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        speakText(responseText);
    }, 400);
}

// --- REPORT GENERATOR ---
function generateReportPreview() {
    const freq = document.getElementById('reportFreq').value;
    alert(`📄 Generated ${freq} Executive Report preview.`);
}

function downloadReport(format) {
    if (format === 'CSV') {
        const csvContent = "data:text/csv;charset=utf-8,Metric,Target,Achieved\nTotal Bookings,450,492\nRevenue,750000,815400\nFuel Cost,180000,198000\nNet Profit,570000,617400";
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `Ghidora_Transport_Report_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        window.print();
    }
}

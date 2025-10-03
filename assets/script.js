// START script.js

// ========================================================
// --- QWebChannel Integration Block ---
// ========================================================
let pythonBackend = null; // To store the QObject proxy
let isWebChannelReady = false;

function initializeWebChannel() {
    console.log("Attempting to initialize QWebChannel...");
    if (typeof qt !== 'undefined' && typeof qt.webChannelTransport !== 'undefined') {
        try {
            new QWebChannel(qt.webChannelTransport, function (channel) {
                if (channel.objects.backend) {
                    pythonBackend = channel.objects.backend;
                    isWebChannelReady = true;
                    console.log("QWebChannel connection established. Python backend object acquired.");
                    setTimeout(() => {
                         if (pythonBackend && typeof pythonBackend.js_ready === 'function') {
                            try { pythonBackend.js_ready(); console.log("Called pythonBackend.js_ready()"); }
                            catch (e) { console.error("Error calling pythonBackend.js_ready():", e); }
                        } else { console.error("Python backend object found, but js_ready function is missing or not callable."); }
                    }, 50);
                } else { console.error("QWebChannel connected, but 'backend' object not found in channel.objects."); }
            });
        } catch (e) { console.error("Error creating QWebChannel:", e); setTimeout(initializeWebChannel, 1500); }
    } else { console.warn("qt.webChannelTransport not defined yet. Retrying setup..."); setTimeout(initializeWebChannel, 300); }
}

function callPythonBackend(methodName, ...args) {
    const isSoundRequest = methodName === 'jsRequestSound';
    if (isWebChannelReady && pythonBackend && typeof pythonBackend[methodName] === 'function') {
        try {
            if (methodName === 'jsRequestSound') {
                if (args.length === 1 && typeof args[0] === 'string') {
                    pythonBackend.jsRequestSound(args[0]);
                } else if (args.length === 1 && typeof args[0] === 'object' && args[0].hasOwnProperty('stop')) {
                     pythonBackend.jsRequestSound(`stop:${args[0].stop}`);
                } else if (args.length > 1 && typeof args[0] === 'string' && typeof args[1] === 'number') {
                    pythonBackend.jsRequestSound(`play:${args[0]}:${args[1]}`);
                } else {
                    console.warn(`Cannot call pythonBackend.jsRequestSound with arguments:`, args);
                }
            } else {
                pythonBackend[methodName](...args);
            }
        }
        catch (e) { console.error(`Error calling pythonBackend.${methodName}():`, e); }
    } else {
        if (!isSoundRequest) {
             if (!pythonBackend || (isSoundRequest && typeof pythonBackend[methodName] !== 'function')) {
                // console.warn(`Cannot call pythonBackend.${methodName}(), backend not ready or method missing.`);
             }
        }
    }
}
// ========================================================
// --- End QWebChannel Integration Block ---
// ========================================================


// ========================================================
// --- Animation Options Block ---
// ========================================================
const OPTIONS = {
    BOX_COUNT: 25, DEFAULT_REVEAL_INTERVAL_MS: 300, CYCLE_INTERVAL_MS: 80, BOX_PULSE_DURATION_MS: 800, BOXES_APPEAR_DELAY_MS: 100, REVEAL_START_DELAY_MS: 600, CHARS: "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    TRIGLAVIAN_GLYPHS: "ABCČDEFGHILMNOPRSŠTUVZŽƕƆƗƖƜƞƚƶENTYΛƆЯƧИ",

    LIST_NUM_LIGHTS: 20,
    LIST_RAF_FAST_SPEED: 50,
    LIST_DECELERATION_DURATION_MS: 5000,
    LIST_FAST_SCROLL_DURATION_MS_FAST: 6000,
    LIST_FAST_SCROLL_DURATION_MS_NORMAL: 10000,
    LIST_FAST_SCROLL_DURATION_MS_SLOW: 20000,
    LIST_APPEAR_DELAY_MS: 100,
    LIST_SCROLL_START_DELAY_MS: 100,
    LIST_MIN_REPEATS_FEW_ENTRANTS: 25,
    LIST_MIN_REPEATS_MANY_ENTRANTS: 15,
    LIST_MANY_ENTRANTS_THRESHOLD: 50,
    LIST_RANDOM_FINAL_OFFSET_PX: 2,
    LIST_WINNER_DISPLAY_DELAY_MS: 300,
    COUNTDOWN_START_DELAY_AFTER_LIST_MS: 800,
    LIST_TEXT_UPDATE_INTERVAL_MS: 60,
    LIST_TARGET_SNAP_THRESHOLD_PX: 0.5,
    LIST_TICK_SOUND_KEY: "wheel_tick",
    LIST_HARD_CAP_DURATION_MS: 35000,

    TRIG_BOX_COUNT: 5, TRIG_APPEAR_DELAY_MS: 100, TRIG_BOXES_APPEAR_DELAY_MS: 100, TRIG_CYCLE_INTERVAL_MS: 90, TRIG_REVEAL_START_DELAY_MS: 500, TRIG_REVEAL_INTERVAL_MS_FAST: 200, TRIG_REVEAL_INTERVAL_MS_NORMAL: 350, TRIG_REVEAL_INTERVAL_MS_SLOW: 600, TRIG_SCAN_PING_DURATION_MS: 250, TRIG_SCAN_PING_DELAY_BEFORE_REVEAL_MS: 100, TRIG_PULSE_DURATION_MS: 600, TRIG_TEMP_REVEAL_CLEAR_DELAY_MS: 150, TRIG_WINNER_DISPLAY_DELAY_MS: 300, TRIG_PLACEHOLDER_CHAR: ' ', COUNTDOWN_START_DELAY_AFTER_TRIG_MS: 500,

    NODE_PATH_APPEAR_DELAY_MS: 100, NODE_PATH_GRID_APPEAR_DELAY_MS: 150, NODE_PATH_REVEAL_START_DELAY_MS: 400,
    NODE_PATH_MIN_PATH_LENGTH: 7, NODE_PATH_MAX_PATH_ATTEMPTS: 5, NODE_PATH_WINNER_REVEAL_DELAY_MS: 250, COUNTDOWN_START_DELAY_AFTER_NODE_PATH_MS: 500,
    NODE_PATH_MIDPOINT_PAUSE_MS: 2000,
    NODE_PATH_VOWEL_REVEAL_SOUND: "verified",
    NODE_PATH_PLACEHOLDER_CHAR: '_',

    TRIG_CONDUIT_NODE_COUNT: 7,
    TRIG_CONDUIT_APPEAR_DELAY_MS: 100,
    TRIG_CONDUIT_NODE_APPEAR_STAGGER_MS: 80,
    TRIG_CONDUIT_PULSE_ANIM_DURATION_MS: 1600,
    TRIG_CONDUIT_REVEAL_BASE_INTERVAL_MS_SLOW: 1200,
    TRIG_CONDUIT_REVEAL_BASE_INTERVAL_MS_NORMAL: 800,
    TRIG_CONDUIT_REVEAL_BASE_INTERVAL_MS_FAST: 450,
    TRIG_CONDUIT_WINNER_DISPLAY_DELAY_MS: 600,
    TRIG_CONDUIT_COUNTDOWN_DELAY_MS: 900,
    TRIG_CONDUIT_PLACEHOLDER_CHAR: '■',
    TRIG_CONDUIT_SCRAMBLE_DURATION_MS: 600,
    TRIG_CONDUIT_SCRAMBLE_CYCLES_PER_CHAR: 8,

    TRIG_CODE_DEFAULT_CHAR_SET: "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCČDEFGHILMNOPRSŠTUVZŽƕƆƗƖƜƞƚƶENTYΛƆЯƧИ",
    TRIG_CODE_DEFAULT_LENGTH: 8,
    TRIG_CODE_MIN_MUTATIONS: 1,
    TRIG_CODE_MAX_MUTATIONS: 3,
    TRIG_CODE_DEFAULT_FINALIST_COUNT: 10,
    TRIG_CODE_FINAL_TWO_PAUSE_MS: 3000,
    TRIG_CODE_REVEAL_INTERVAL_MS_FAST: 300,
    TRIG_CODE_REVEAL_INTERVAL_MS_NORMAL: 500,
    TRIG_CODE_REVEAL_INTERVAL_MS_SLOW: 900,
    TRIG_CODE_PLACEHOLDER_CHAR: '·',
    TRIG_CODE_APPEAR_DELAY_MS: 100,
    TRIG_CODE_LIST_APPEAR_DELAY_MS: 250,
    TRIG_CODE_WINNER_CODE_REVEAL_START_DELAY_MS: 500,
    TRIG_CODE_ELIMINATION_DELAY_MS: 250,
    TRIG_CODE_ELIMINATION_ANIM_DURATION_MS: 400,
    TRIG_CODE_WINNER_NAME_DISPLAY_DELAY_MS: 300,
    COUNTDOWN_START_DELAY_AFTER_TRIG_CODE_MS: 600,

    SLIDE_UP_DELAY_MS: 100, COLOR_SHIFT_START_DELAY_MS: 2000, SOUND_NOTIFICATION_KEY: "notification",
    SOUND_CONDUIT_STABLE_KEY: "conduit_stable",
};

const NODE_PATH_SPEED_DURATIONS = { "Normal": 120, "Slow": 280, "Very Slow": 500 };
// ========================================================
// --- End Animation Options Block ---
// ========================================================

// --- DOM Elements ---
let bodyElement; let backgroundCanvas;
let animationContent; 
let boxRevealMode; let listRevealMode; let triglavianRevealMode; let nodePathRevealMode;
let trigConduitRevealMode; let trigCodeRevealMode;
let prizeRevealContainer, prizeRevealDisplay, prizeRevealName, prizeRevealDonator;
let boxesRow;
let listScrollContainer; let listPointer; let entrantList; let listWinnerDisplay; let listWinnerNameSpan;
let listLightsIndicator;
let triglavianBoxesRow; let triglavianWinnerDisplay; let triglavianWinnerNameSpan; /* ESI: */ let triglavianWinnerPortraitImg, triglavianWinnerCorpSpan, triglavianWinnerAllianceSpan;
let nodePathGridContainer; let nodePathSvgOverlay = null; let nodePathWinnerDisplay; let nodePathWinnerNameSpan; /* ESI: */ let nodePathWinnerPortraitImg, nodePathWinnerCorpSpan, nodePathWinnerAllianceSpan;
let trigConduitNodesContainer; let trigConduitWinnerDisplay; let trigConduitWinnerNameSpan; /* ESI: */ let trigConduitWinnerPortraitImg, trigConduitWinnerCorpSpan, trigConduitWinnerAllianceSpan;
let trigCodeParticipantsContainer; let trigCodeWinnerCodeDisplay; let trigCodeWinnerNameDisplay; let trigCodeWinnerNameSpan; /* ESI: */ let trigCodeWinnerPortraitImg, trigCodeWinnerCorpSpan, trigCodeWinnerAllianceSpan;


let countdownContainer; let countdownProgress; let countdownText;

// --- State Variables ---
let boxes = []; let cyclingIntervalId = null; let revealTimeoutId = null; let revealedIndices = new Set(); let currentRevealInterval = OPTIONS.DEFAULT_REVEAL_INTERVAL_MS;
let isListScrolling = false;
let winnerLiElement = null;
let listAnimationFrameId = null;
let listScrollState = {
    currentTranslateY: 0, startTime: 0, lastTextUpdateTime: 0, targetTranslateY: 0, decelerationStartTime: 0,
    initialPosAtDeceleration: 0, currentPhase: 'fast-scroll',
    singleBlockHeight: 0,
    currentFastScrollDurationMs: OPTIONS.LIST_FAST_SCROLL_DURATION_MS_NORMAL,
    currentFastSpeed: OPTIONS.LIST_RAF_FAST_SPEED,
    listLights: [], numLightsCurrentlyOn: OPTIONS.LIST_NUM_LIGHTS, lightsTurnedOffThisCycle: false,
    cachedWinnerLiOffsetTop: 0,
    cachedWinnerLiHeight: 0,
    initialLightsOnAtDecel: 0,
    lastTickedItemGlobalIndex: -1,
    totalItemHeightWithMargin: 0,
    animationStartTime: 0,
};

let triglavianBoxes = []; let triglavianCyclingIntervalId = null; let triglavianRevealTimeoutId = null; let trigRevealSequence = []; let trigRevealedLetters = []; let trigTempRevealTimeouts = {};
let nodeGrid = []; let nodePathLines = {}; let currentPath = []; let nodePathRevealTimeoutId = null; let nodePathActiveNodeTimeoutId = null; let nodePathGenerationAttempts = 0;
let nodePathWinnerDisplayState = [];
let trigConduitNodes = [];
let trigConduitNamePlaceholders = [];
let trigConduitNodeCenters = [];
let trigConduitIntervalId = null;
let currentTrigConduitStepDuration = OPTIONS.TRIG_CONDUIT_REVEAL_BASE_INTERVAL_MS_NORMAL;
let trigConduitScrambleIntervals = {};
let trigConduitCore = null;

let trigCodeParticipantsData = [];
let trigCodeWinnerCode = "";
let trigCodeRevealedChars = [];
let trigCodeCurrentRevealIndex = 0;
let trigCodeRevealIntervalId = null;
let currentTrigCodeRevealStepDuration = OPTIONS.TRIG_CODE_REVEAL_INTERVAL_MS_NORMAL;
let currentTrigCodeCharSet = OPTIONS.TRIG_CODE_DEFAULT_CHAR_SET;
let currentTrigCodeFinalistCount = OPTIONS.TRIG_CODE_DEFAULT_FINALIST_COUNT;

let progressRingCircumference = 0; let animationSequenceTimeoutIds = [];
let isCountdownActive = false; let countdownStartTime = 0;
let currentWinnerNameForCallback = "Unknown";
let currentCountdownDurationS = 30;
let _cachedParticipantList = []; let isBackgroundListsReady = false;
let currentNodePathStepDuration = NODE_PATH_SPEED_DURATIONS["Normal"];

let canPlayTickSound = true;
const tickSoundDebounceDelay = 120;


// --- Helper Functions ---

// Universal animation state reset
function resetAllAnimationStates() {
    resetListState();
    resetTriglavianState();
    resetNodePathState();
    resetTrigConduitState();
    resetTrigCodeRevealState();
    // Remove animation classes from all .box and winner containers
    document.querySelectorAll('.box, .triglavian-box, .trig-conduit-node').forEach(el => {
        el.classList.remove('box-pulse', 'revealed', 'showing-reveal', 'active', 'letter-placeholder', 'letter-revealed');
        el.textContent = '';
    });
    document.querySelectorAll('.winner-target-slot, .visible, .slide-up, .standalone').forEach(el => {
        el.classList.remove('winner-target-slot', 'visible', 'slide-up', 'standalone');
    });
    // Hide or clear winner name/portrait containers
    [
        'hacking-winner-name', 'list-winner-name', 'triglavian-winner-name',
        'node-path-winner-name', 'trig-conduit-winner-name', 'trig-code-winner-name'
    ].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = '';
    });
}
function clearAnimationSequenceTimeouts() { animationSequenceTimeoutIds.forEach(id => { clearTimeout(id); clearInterval(id); }); animationSequenceTimeoutIds = []; }
function shuffleArray(array) { for (let i = array.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [array[i], array[j]] = [array[j], array[i]]; } return array; }
function getRandomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function getRandomFloat(min, max) { return Math.random() * (max - min) + min; }
function getCssVariableValue(variableName) { try { return getComputedStyle(document.documentElement).getPropertyValue(variableName).trim(); } catch (e) { console.error(`Error getting CSS variable ${variableName}:`, e); return null; } }
function parsePixels(cssValue) { if (!cssValue) return 0; const match = cssValue.match(/(\d+(\.\d+)?)px/); return match ? parseFloat(match[1]) : 0; }
function parseVmin(cssValue) { if (!cssValue) return 0; const match = cssValue.match(/(\d+(\.\d+)?)vmin/); if (!match) return 0; const val = parseFloat(match[1]); const vmin = Math.min(window.innerWidth, window.innerHeight) / 100; return val * vmin; }
function getRandomChar() { return OPTIONS.CHARS[Math.floor(Math.random() * OPTIONS.CHARS.length)]; }
function getRandomTrigGlyph() { return OPTIONS.TRIGLAVIAN_GLYPHS[Math.floor(Math.random() * OPTIONS.TRIGLAVIAN_GLYPHS.length)]; }
function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
function easeOutQuint(t) { return 1 - Math.pow(1 - t, 5); }


// --- Initialization ---
function initializeDisplay() {
    resetAllAnimationStates();
    bodyElement = document.body; backgroundCanvas = document.getElementById('background-canvas');
    animationContent = document.getElementById('animation-content'); 
    boxRevealMode = document.getElementById('box-reveal-mode'); listRevealMode = document.getElementById('list-reveal-mode');
    triglavianRevealMode = document.getElementById('triglavian-reveal-mode');
    nodePathRevealMode = document.getElementById('node-path-reveal-mode');
    trigConduitRevealMode = document.getElementById('trig-conduit-reveal-mode');
    trigCodeRevealMode = document.getElementById('trig-code-reveal-mode');
    prizeRevealContainer = document.getElementById('prize-reveal-container'); 
    prizeRevealDisplay = document.getElementById('prize-reveal-display'); 
    prizeRevealName = document.getElementById('prize-reveal-name');
    prizeRevealDonator = document.getElementById('prize-reveal-donator');
    boxesRow = document.getElementById('boxes-row');
    listScrollContainer = document.getElementById('list-scroll-container'); listPointer = document.querySelector('#list-reveal-mode .list-pointer');
    entrantList = document.getElementById('entrant-list'); listWinnerDisplay = document.getElementById('list-winner-display'); listWinnerNameSpan = document.getElementById('list-winner-name');
    listLightsIndicator = document.getElementById('list-lights-indicator');
    
    triglavianBoxesRow = document.getElementById('triglavian-boxes-row');
    triglavianWinnerDisplay = document.getElementById('triglavian-winner-display');
    triglavianWinnerNameSpan = document.getElementById('triglavian-winner-name');
    triglavianWinnerPortraitImg = document.getElementById('triglavian-winner-portrait'); // ESI
    triglavianWinnerCorpSpan = document.getElementById('triglavian-winner-corp');     // ESI
    triglavianWinnerAllianceSpan = document.getElementById('triglavian-winner-alliance'); // ESI

    nodePathGridContainer = document.getElementById('node-path-grid-container'); nodePathSvgOverlay = null;
    nodePathWinnerDisplay = document.getElementById('node-path-winner-display');
    nodePathWinnerNameSpan = document.getElementById('node-path-winner-name');
    nodePathWinnerPortraitImg = document.getElementById('node-path-winner-portrait'); // ESI
    nodePathWinnerCorpSpan = document.getElementById('node-path-winner-corp');     // ESI
    nodePathWinnerAllianceSpan = document.getElementById('node-path-winner-alliance'); // ESI

    trigConduitNodesContainer = document.getElementById('trig-conduit-nodes-container');
    trigConduitWinnerDisplay = document.getElementById('trig-conduit-winner-display');
    trigConduitWinnerNameSpan = document.getElementById('trig-conduit-winner-name');
    trigConduitWinnerPortraitImg = document.getElementById('trig-conduit-winner-portrait'); // ESI
    trigConduitWinnerCorpSpan = document.getElementById('trig-conduit-winner-corp');     // ESI
    trigConduitWinnerAllianceSpan = document.getElementById('trig-conduit-winner-alliance'); // ESI
    
    trigCodeParticipantsContainer = document.getElementById('trig-code-participants-container');
    trigCodeWinnerCodeDisplay = document.getElementById('trig-code-winner-code-display');
    trigCodeWinnerNameDisplay = document.getElementById('trig-code-winner-name-display');
    trigCodeWinnerNameSpan = document.getElementById('trig-code-winner-name');
    trigCodeWinnerPortraitImg = document.getElementById('trig-code-winner-portrait'); // ESI
    trigCodeWinnerCorpSpan = document.getElementById('trig-code-winner-corp');     // ESI
    trigCodeWinnerAllianceSpan = document.getElementById('trig-code-winner-alliance'); // ESI


    countdownContainer = document.getElementById('countdown-container'); countdownProgress = document.getElementById('countdown-progress'); countdownText = document.getElementById('countdown-text');

    if (!bodyElement || !animationContent || !boxRevealMode || !listRevealMode || !triglavianRevealMode || !nodePathRevealMode || !trigConduitRevealMode || !trigCodeRevealMode || !countdownContainer || !backgroundCanvas || !countdownProgress || !countdownText || !listLightsIndicator || !prizeRevealContainer || !prizeRevealDisplay || !prizeRevealName || !prizeRevealDonator) {
        console.error("Initialization Error: Core elements missing!"); if(bodyElement) bodyElement.innerHTML = "<h1 style='color:red; font-family: sans-serif;'>Init Error: Missing Core Elements!</h1>"; return false;
    }
    stopAnimationSequence();
    bodyElement.classList.remove('show-boxes', 'show-list', 'show-triglavian', 'show-node-path', 'show-trig-conduit', 'show-trig-code');
    [boxRevealMode, listRevealMode, triglavianRevealMode, nodePathRevealMode, trigConduitRevealMode, trigCodeRevealMode].forEach(mode => {
        if(mode) { mode.style.display = 'none'; mode.classList.remove('visible', 'slide-up'); }
    });
    if(prizeRevealContainer) { prizeRevealContainer.style.display = 'none'; prizeRevealContainer.classList.remove('visible'); }
    if(animationContent) { animationContent.style.display = 'flex'; }
    if(boxesRow) boxesRow.classList.remove('visible');
    if(listWinnerDisplay) listWinnerDisplay.classList.remove('visible');
    if(listLightsIndicator) listLightsIndicator.innerHTML = '';
    
    // Reset ESI display elements too
    [triglavianWinnerDisplay, nodePathWinnerDisplay, trigConduitWinnerDisplay, trigCodeWinnerNameDisplay].forEach(el => { if(el) el.classList.remove('visible', 'standalone'); });
    [triglavianWinnerPortraitImg, nodePathWinnerPortraitImg, trigConduitWinnerPortraitImg, trigCodeWinnerPortraitImg, document.getElementById('list-winner-portrait')].forEach(el => { if(el) { el.src="#"; el.style.display='none';} }); // Added list-winner-portrait
    [triglavianWinnerCorpSpan, triglavianWinnerAllianceSpan, nodePathWinnerCorpSpan, nodePathWinnerAllianceSpan, trigConduitWinnerCorpSpan, trigConduitWinnerAllianceSpan, trigCodeWinnerCorpSpan, trigCodeWinnerAllianceSpan, document.getElementById('list-winner-corp'), document.getElementById('list-winner-alliance')].forEach(el => { if(el) el.textContent=''; }); // Added list ESI spans


    if(triglavianBoxesRow) triglavianBoxesRow.classList.remove('visible');
    if(nodePathGridContainer) nodePathGridContainer.classList.remove('visible');
    if(trigConduitNodesContainer) trigConduitNodesContainer.classList.remove('visible');
    if(trigCodeParticipantsContainer) { trigCodeParticipantsContainer.innerHTML = ''; trigCodeParticipantsContainer.classList.remove('visible');}
    if(trigCodeWinnerCodeDisplay) { trigCodeWinnerCodeDisplay.innerHTML = ''; trigCodeWinnerCodeDisplay.classList.remove('visible');}


    countdownContainer.classList.remove('visible');
    resetListState(); resetTriglavianState(); resetNodePathState(); resetTrigConduitState(); resetTrigCodeRevealState();
    revealedIndices.clear(); boxes.forEach(box => { if (box) { box.classList.remove('box-pulse', 'revealed'); box.textContent = ''; } });
    winnerLiElement = null;
    console.log("🔧 initializeDisplay: Creating boxes and Triglavian boxes...");
    createBoxes(); createTriglavianBoxes();
    console.log("🔧 initializeDisplay: After creation - boxes.length:", boxes.length, "triglavianBoxes.length:", triglavianBoxes.length);
    initializeBackgroundNetwork();
    if (countdownProgress && progressRingCircumference === 0) { const radiusEl = countdownProgress.r?.baseVal; if (radiusEl) { const radius = radiusEl.value; progressRingCircumference = 2 * Math.PI * radius; } else { console.error("Could not get countdown radius."); progressRingCircumference = 283; } countdownProgress.style.strokeDasharray = `${progressRingCircumference} ${progressRingCircumference}`; }
    return true;
}

// --- Background Network Functions ---
function initializeBackgroundNetwork() { if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.init === 'function') { if (!window.networkAnimationRunning) { NetworkAnimation.init(updateCountdown); window.networkAnimationRunning = true; setTimeout(() => { if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.forceResizeCheck === 'function') { NetworkAnimation.forceResizeCheck(); } }, 150); } } else { console.error("NetworkAnimation module not found or init function missing!"); } }
function stopBackgroundNetworkAnimation() { if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.stop === 'function') { NetworkAnimation.stop(); window.networkAnimationRunning = false; } }

// --- Function Called by Python ---
function updateParticipantsJS(participantArray) { console.log("JS: updateParticipantsJS function ENTRY. Received type:", typeof participantArray, "Value:", participantArray ? participantArray.slice(0,5) : 'null/undefined'); try { _cachedParticipantList = Array.isArray(participantArray) ? participantArray : []; console.log("JS: _cachedParticipantList updated. Count:", _cachedParticipantList.length); if (isBackgroundListsReady && typeof BackgroundLists !== 'undefined' && typeof BackgroundLists.update === 'function') { console.log("JS: Calling BackgroundLists.update..."); BackgroundLists.update(_cachedParticipantList); console.log("JS: BackgroundLists.update call finished."); } else if (!isBackgroundListsReady) { console.warn("BackgroundLists module not ready yet, skipping update."); } else { console.warn("BackgroundLists module ready but update function not found!"); } } catch (e) { console.error("JS Error within updateParticipantsJS:", e); } }
window.updateParticipantsJS = updateParticipantsJS;

// --- Hacking (Box) Creation / Cycling / Reveal ---
function createBoxes() { if (!boxesRow) { console.error("Boxes row missing!"); return; } if (boxes.length !== OPTIONS.BOX_COUNT) { boxesRow.innerHTML = ''; boxes = []; for (let i = 0; i < OPTIONS.BOX_COUNT; i++) { const box = document.createElement('div'); box.classList.add('box'); box.id = `box-${i}`; boxesRow.appendChild(box); boxes.push(box); } } }
function cycleChars() { if (!bodyElement.classList.contains('show-boxes')) { if (cyclingIntervalId) { clearInterval(cyclingIntervalId); cyclingIntervalId = null; } return; } if (boxes.length !== OPTIONS.BOX_COUNT) return; boxes.forEach((box, index) => { if (box && !revealedIndices.has(index)) { box.textContent = getRandomChar(); box.classList.remove('revealed'); } }); }
function pulseBox(boxElement) { if (boxElement) { boxElement.classList.add('box-pulse'); setTimeout(() => { if (boxElement) boxElement.classList.remove('box-pulse'); }, OPTIONS.BOX_PULSE_DURATION_MS); } }
function revealLetter(box, letter, index) { if (!box) return; box.textContent = letter; box.classList.add('revealed'); pulseBox(box); revealedIndices.add(index); if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.notifyBoxReveal === 'function') { NetworkAnimation.notifyBoxReveal(index, box); } callPythonBackend('jsRequestSound', OPTIONS.SOUND_NOTIFICATION_KEY); }
function checkRevealCompletion(remainingIndices) { if (remainingIndices.length === 0) { if (cyclingIntervalId) { clearInterval(cyclingIntervalId); cyclingIntervalId = null; } if (revealTimeoutId) clearTimeout(revealTimeoutId); revealTimeoutId = null; const revealMode = document.querySelector('.reveal-mode.visible'); if (revealMode) revealMode.classList.add('slide-up'); const countdownStartTimeoutId = setTimeout(() => { startCountdownPhase(); }, OPTIONS.SLIDE_UP_DELAY_MS); animationSequenceTimeoutIds.push(countdownStartTimeoutId); console.log(`JS checkRevealCompletion: Sending original name back: '${currentWinnerNameForCallback}'`); callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback); return true; } return false; }
function revealRandomLetter(winnerNameToReveal, leftPadding, unrevealedTargetIndices) { if (checkRevealCompletion(unrevealedTargetIndices)) return; const randomIndexInUnrevealed = Math.floor(Math.random() * unrevealedTargetIndices.length); const boxIndexToReveal = unrevealedTargetIndices[randomIndexInUnrevealed]; const letterIndexInName = boxIndexToReveal - leftPadding; const letter = winnerNameToReveal[letterIndexInName]?.toUpperCase() || '?'; const box = boxes[boxIndexToReveal]; if (!box) { console.error(`Target box ${boxIndexToReveal} not found! Skipping.`); unrevealedTargetIndices.splice(randomIndexInUnrevealed, 1); revealRandomLetter(winnerNameToReveal, leftPadding, unrevealedTargetIndices); } else { revealLetter(box, letter, boxIndexToReveal); unrevealedTargetIndices.splice(randomIndexInUnrevealed, 1); if (unrevealedTargetIndices.length > 0) { if (revealTimeoutId) clearTimeout(revealTimeoutId); revealTimeoutId = setTimeout(() => { revealRandomLetter(winnerNameToReveal, leftPadding, unrevealedTargetIndices); }, currentRevealInterval); animationSequenceTimeoutIds.push(revealTimeoutId); } else { checkRevealCompletion(unrevealedTargetIndices); } } }
function showBoxes() { if (boxesRow) { boxesRow.classList.add('visible'); } else { console.error("Boxes row not found!"); } }

// --- Vertical List Logic (Hybrid Approach) ---
// ... (buildList, scrollListWithRAF, createListLights, updateAllLightsVisualState, resetListState remain the same) ...
function createListLights(indicatorElement = listLightsIndicator, stateObject = listScrollState, numLights = OPTIONS.LIST_NUM_LIGHTS) {
    if (!indicatorElement) return;
    indicatorElement.innerHTML = '';
    stateObject.listLights = [];
    stateObject.numLightsCurrentlyOn = numLights;

    for (let i = 0; i < numLights; i++) {
        const light = document.createElement('div');
        light.classList.add('list-light');
        indicatorElement.appendChild(light);
        stateObject.listLights.push(light);
    }
    updateAllLightsVisualState(stateObject);
}

function updateAllLightsVisualState(stateObject = listScrollState) {
    if (!stateObject.listLights || stateObject.listLights.length === 0) return;
    const totalLights = stateObject.listLights.length;
    const lightsToDisplayOn = stateObject.numLightsCurrentlyOn;
    const lightsOffEachSide = Math.floor((totalLights - lightsToDisplayOn) / 2);
    stateObject.listLights.forEach((light, index) => {
        let shouldBeOn = (lightsToDisplayOn === 0) ? false :
                         (totalLights % 2 === 1 && lightsToDisplayOn === 1) ? (index === Math.floor(totalLights / 2)) :
                         (index >= lightsOffEachSide && index < totalLights - lightsOffEachSide);
        const isOn = light.classList.contains('on');
        if (shouldBeOn && !isOn) light.classList.remove('off', 'dim'), light.classList.add('on');
        else if (!shouldBeOn && isOn) {
            light.classList.remove('on'), light.classList.add('dim');
            setTimeout(() => { light.classList.remove('dim'), light.classList.add('off'); }, 150);
        } else if (!shouldBeOn && !light.classList.contains('dim')) light.classList.add('off');
    });
}

function resetListState() {
    console.log("Resetting List State (Hybrid)");
    if (listAnimationFrameId) { cancelAnimationFrame(listAnimationFrameId); listAnimationFrameId = null; }
    if (entrantList) {
        entrantList.innerHTML = '';
        entrantList.style.transform = 'translateY(0px)';
        entrantList.style.transition = 'none';
    }
    if (listWinnerDisplay) listWinnerDisplay.classList.remove('visible');
    if (listWinnerNameSpan) listWinnerNameSpan.textContent = '';
    if (listLightsIndicator) listLightsIndicator.innerHTML = '';

    winnerLiElement = null;
    isListScrolling = false;
    listScrollState = {
        currentTranslateY: 0, startTime: 0, lastTextUpdateTime: 0, targetTranslateY: 0, decelerationStartTime: 0,
        initialPosAtDeceleration: 0, currentPhase: 'fast-scroll',
        singleBlockHeight: 0,
        currentFastScrollDurationMs: OPTIONS.LIST_FAST_SCROLL_DURATION_MS_NORMAL,
        currentFastSpeed: OPTIONS.LIST_RAF_FAST_SPEED,
        listLights: [], numLightsCurrentlyOn: OPTIONS.LIST_NUM_LIGHTS, lightsTurnedOffThisCycle: false,
        cachedWinnerLiOffsetTop: 0, cachedWinnerLiHeight: 0, initialLightsOnAtDecel: 0,
        lastTickedItemGlobalIndex: -1,
        totalItemHeightWithMargin: 0,
        animationStartTime: 0,
    };
    canPlayTickSound = true;
}

function buildList(winnerName, allParticipants) {
    console.log(`Building list for: ${winnerName} (Hybrid approach)`);
    if (!entrantList || !listScrollContainer) { console.error("List elements missing for buildList"); return false; }

    const participantsToUse = (allParticipants && allParticipants.length > 0) ? [...allParticipants] : [..._cachedParticipantList];
    if (!participantsToUse || participantsToUse.length === 0) {
        console.warn("buildList: No participants available.");
        entrantList.innerHTML = '<li>--- NO ENTRANTS ---</li>';
        listScrollState.totalItemHeightWithMargin = 0;
        winnerLiElement = null;
        return false;
    }

    let localShuffledParticipants = shuffleArray([...participantsToUse]);
    let winnerIndexInShuffled = localShuffledParticipants.indexOf(winnerName);

    if (winnerIndexInShuffled === -1) {
        console.warn(`Winner "${winnerName}" not in provided list. Adding to local copy for build.`);
        localShuffledParticipants.push(winnerName);
        localShuffledParticipants = shuffleArray(localShuffledParticipants);
        winnerIndexInShuffled = localShuffledParticipants.indexOf(winnerName);
        if (winnerIndexInShuffled === -1) {
            console.error("CRITICAL: Winner still not found after adding and reshuffling.");
            return false;
        }
    }

    entrantList.innerHTML = '';
    winnerLiElement = null;

    const listItemHeightValue = getCssVariableValue('--list-item-height');
    const listItemMarginValue = getCssVariableValue('--list-item-margin');
    const itemHeight = parsePixels(listItemHeightValue) || 40;
    const itemMargin = parsePixels(listItemMarginValue) || 4;
    listScrollState.totalItemHeightWithMargin = itemHeight + itemMargin;

    const containerHeight = listScrollContainer.offsetHeight;
    if (containerHeight <= 0 || listScrollState.totalItemHeightWithMargin <= itemMargin) {
        console.error("List container/item height invalid.");
        return false;
    }

    const numUniqueParticipants = localShuffledParticipants.length;
    listScrollState.singleBlockHeight = numUniqueParticipants * listScrollState.totalItemHeightWithMargin;

    const itemsPerViewport = Math.ceil(containerHeight / listScrollState.totalItemHeightWithMargin);
    const targetPhysicalItemCount = Math.max(itemsPerViewport * 5, numUniqueParticipants * 3, 60);
    let numRepeats = 1;
    if (numUniqueParticipants > 0) {
        numRepeats = Math.ceil(targetPhysicalItemCount / numUniqueParticipants);
    } else {
        numRepeats = OPTIONS.LIST_MIN_REPEATS_FEW_ENTRANTS;
    }
     numRepeats = Math.max(numRepeats, (numUniqueParticipants > OPTIONS.LIST_MANY_ENTRANTS_THRESHOLD)
                            ? OPTIONS.LIST_MIN_REPEATS_MANY_ENTRANTS
                            : OPTIONS.LIST_MIN_REPEATS_FEW_ENTRANTS);


    console.log(`List Build (Hybrid): Unique=${numUniqueParticipants}, Repeats=${numRepeats}, ItemH=${listScrollState.totalItemHeightWithMargin}, TargetPhysicalItems=${targetPhysicalItemCount}`);

    const fragment = document.createDocumentFragment();
    const targetWinnerRepeat = Math.floor(numRepeats / 2);

    for (let repeat = 0; repeat < numRepeats; repeat++) {
        localShuffledParticipants.forEach((name, indexInShuffled) => {
            const li = document.createElement('li');
            li.textContent = localShuffledParticipants[indexInShuffled] || "ErrorName"; // Ensure text content
            if (indexInShuffled === winnerIndexInShuffled && repeat === targetWinnerRepeat) {
                li.classList.add('winner-target-slot');
                winnerLiElement = li;
            }
            fragment.appendChild(li);
        });
    }
    entrantList.appendChild(fragment);

    if (!winnerLiElement) {
        console.error(`CRITICAL: winnerLiElement not assigned in buildList for "${winnerName}".`);
        return false;
    }

    listScrollState.cachedWinnerLiOffsetTop = winnerLiElement.offsetTop;
    listScrollState.cachedWinnerLiHeight = winnerLiElement.offsetHeight;

    const pointerCenterY = containerHeight / 2;
    const winnerLiCenterY = listScrollState.cachedWinnerLiOffsetTop + (listScrollState.cachedWinnerLiHeight / 2);
    listScrollState.targetTranslateY = pointerCenterY - winnerLiCenterY;
    listScrollState.targetTranslateY += (Math.random() * OPTIONS.LIST_RANDOM_FINAL_OFFSET_PX * 2 - OPTIONS.LIST_RANDOM_FINAL_OFFSET_PX);

    entrantList.style.transform = 'translateY(0px)';
    void entrantList.offsetWidth;
    console.log(`List built. Target DOM element for winner: ${winnerLiElement.textContent}. Target Y: ${listScrollState.targetTranslateY.toFixed(2)}`);
    return true;
}


function scrollListWithRAF(winnerName) {
    if (!entrantList || !listScrollContainer || !listLightsIndicator) {
        console.error("scrollListWithRAF: Core list or lights elements missing.");
        callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback); return;
    }
    if (!winnerLiElement) {
        console.error("scrollListWithRAF: winnerLiElement is null. Cannot start scroll.");
        if (listWinnerNameSpan) listWinnerNameSpan.textContent = winnerName;
        if (listWinnerDisplay) listWinnerDisplay.classList.add('visible');
        callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback); return;
    }

    createListLights(listLightsIndicator, listScrollState, OPTIONS.LIST_NUM_LIGHTS);

    requestAnimationFrame(() => {
        isListScrolling = true;
        entrantList.style.transition = 'none';

        listScrollState.animationStartTime = performance.now();
        listScrollState.startTime = listScrollState.animationStartTime;
        listScrollState.lastTextUpdateTime = listScrollState.startTime;
        listScrollState.currentPhase = 'fast-scroll';
        listScrollState.decelerationStartTime = 0;
        listScrollState.currentTranslateY = 0;
        listScrollState.lightsTurnedOffThisCycle = false;
        listScrollState.lastTickedItemGlobalIndex = -1;
        canPlayTickSound = true;

        const allPhysicalLIs = Array.from(entrantList.children);
        const numPhysicalLIs = allPhysicalLIs.length;
        const containerHeight = listScrollContainer.offsetHeight;
        const pointerCenterY = containerHeight / 2;
        const itemFullHeight = listScrollState.totalItemHeightWithMargin;
        const numUniqueNames = _cachedParticipantList.length;

        const itemsPerViewportApprox = Math.ceil(containerHeight / itemFullHeight);

        function forceFinishAnimation() {
            console.log("List Animation: Forcing finish (Hybrid).");
            isListScrolling = false;
            if (listAnimationFrameId) { cancelAnimationFrame(listAnimationFrameId); listAnimationFrameId = null; }

            listScrollState.numLightsCurrentlyOn = 0;
            updateAllLightsVisualState(listScrollState);

            entrantList.style.transform = `translateY(${listScrollState.targetTranslateY}px)`;
            listScrollState.currentTranslateY = listScrollState.targetTranslateY;

            const textUpdateBufferFinal = Math.max(5, itemsPerViewportApprox);
            const finalScrollTop = -listScrollState.targetTranslateY;
            const firstFinalVisiblePhysicalIndex = Math.max(0, Math.floor(finalScrollTop / itemFullHeight) - textUpdateBufferFinal);
            const lastFinalVisiblePhysicalIndex = Math.min(numPhysicalLIs - 1, firstFinalVisiblePhysicalIndex + itemsPerViewportApprox + 2 * textUpdateBufferFinal);

            const winnerLiDomIndex = allPhysicalLIs.indexOf(winnerLiElement);
            const winnerCachedIdx = numUniqueNames > 0 ? _cachedParticipantList.indexOf(winnerName) : -1;

            allPhysicalLIs.forEach((li, index) => {
                li.classList.remove('active');
                if (li === winnerLiElement) {
                    li.textContent = winnerName;
                    li.classList.add('active');
                } else if (index >= firstFinalVisiblePhysicalIndex && index <= lastFinalVisiblePhysicalIndex) {
                    if (numUniqueNames > 0 && winnerCachedIdx !== -1 && winnerLiDomIndex !== -1) {
                        const offsetFromWinner = index - winnerLiDomIndex;
                        let nameToShowIdx = (winnerCachedIdx + offsetFromWinner) % numUniqueNames;
                        if (nameToShowIdx < 0) nameToShowIdx += numUniqueNames;
                        li.textContent = _cachedParticipantList[nameToShowIdx] || "---";
                    } else if (numUniqueNames > 0) {
                         li.textContent = _cachedParticipantList[Math.abs(index) % numUniqueNames] || "---";
                    } else {
                         li.textContent = getRandomChar() + getRandomChar();
                    }
                }
            });

            if (listWinnerNameSpan) listWinnerNameSpan.textContent = winnerName;
            if (listWinnerDisplay) listWinnerDisplay.classList.add('visible');
            const revealMode = document.querySelector('.reveal-mode.visible');
            if (revealMode) revealMode.classList.add('slide-up');
            callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback);
            const cdt = setTimeout(() => startCountdownPhase(), OPTIONS.COUNTDOWN_START_DELAY_AFTER_LIST_MS);
            animationSequenceTimeoutIds.push(cdt);
        }

        function step(timestamp) {
            if (!isListScrolling) return;
            const totalElapsedTime = timestamp - listScrollState.animationStartTime;
            if (totalElapsedTime >= OPTIONS.LIST_HARD_CAP_DURATION_MS) { forceFinishAnimation(); return; }

            let newTranslateY = listScrollState.currentTranslateY;
            const timeInCurrentPhase = timestamp - listScrollState.startTime;

            if (listScrollState.currentPhase === 'fast-scroll') {
                newTranslateY -= listScrollState.currentFastSpeed;
                if (timeInCurrentPhase >= listScrollState.currentFastScrollDurationMs || (OPTIONS.LIST_HARD_CAP_DURATION_MS - totalElapsedTime) <= OPTIONS.LIST_DECELERATION_DURATION_MS + 500) {
                    listScrollState.currentPhase = 'decelerating';
                    listScrollState.decelerationStartTime = timestamp;
                    listScrollState.initialPosAtDeceleration = newTranslateY;
                    listScrollState.initialLightsOnAtDecel = listScrollState.numLightsCurrentlyOn;
                } else {
                    const fastScrollProgress = timeInCurrentPhase / listScrollState.currentFastScrollDurationMs;
                    const lightsThatShouldBeOn = Math.max(0, Math.round(OPTIONS.LIST_NUM_LIGHTS * (1-fastScrollProgress)));
                    if(lightsThatShouldBeOn < listScrollState.numLightsCurrentlyOn) {
                        listScrollState.numLightsCurrentlyOn = lightsThatShouldBeOn;
                        updateAllLightsVisualState(listScrollState);
                    }
                }
            } else if (listScrollState.currentPhase === 'decelerating') {
                const elapsedDecelTime = timestamp - listScrollState.decelerationStartTime;
                const effectiveDecelDuration = Math.min(OPTIONS.LIST_DECELERATION_DURATION_MS, (OPTIONS.LIST_HARD_CAP_DURATION_MS - (listScrollState.decelerationStartTime - listScrollState.animationStartTime) - 500));
                let decelProgress = Math.min(1, elapsedDecelTime / Math.max(1, effectiveDecelDuration));
                newTranslateY = listScrollState.initialPosAtDeceleration + (listScrollState.targetTranslateY - listScrollState.initialPosAtDeceleration) * easeOutQuint(decelProgress);

                if (listScrollState.initialLightsOnAtDecel > 0) {
                    const lightsOn = Math.round(listScrollState.initialLightsOnAtDecel * (1 - decelProgress));
                     if(lightsOn < listScrollState.numLightsCurrentlyOn){
                         listScrollState.numLightsCurrentlyOn = Math.max(0, lightsOn);
                         updateAllLightsVisualState(listScrollState);
                     }
                }
                if (elapsedDecelTime >= effectiveDecelDuration || Math.abs(newTranslateY - listScrollState.targetTranslateY) < OPTIONS.LIST_TARGET_SNAP_THRESHOLD_PX) {
                    forceFinishAnimation(); return;
                }
            }

            entrantList.style.transform = `translateY(${newTranslateY}px)`;
            listScrollState.currentTranslateY = newTranslateY;

            if (timestamp - listScrollState.lastTextUpdateTime > OPTIONS.LIST_TEXT_UPDATE_INTERVAL_MS) {
                const scrollTop = -newTranslateY;
                const viewportTopEdge = scrollTop;
                const viewportBottomEdge = scrollTop + containerHeight;

                const updateWindowMargin = containerHeight * 1.5;
                const updateWindowTop = viewportTopEdge - updateWindowMargin;
                const updateWindowBottom = viewportBottomEdge + updateWindowMargin;

                const winnerLiDomIndex = allPhysicalLIs.indexOf(winnerLiElement);
                const winnerCachedIdx = numUniqueNames > 0 ? _cachedParticipantList.indexOf(winnerName) : -1;

                allPhysicalLIs.forEach((li, physicalIndex) => {
                    const itemTop = physicalIndex * itemFullHeight;
                    const itemBottom = itemTop + itemFullHeight;

                    if (li === winnerLiElement && listScrollState.currentPhase === 'decelerating') {
                        li.textContent = winnerName;
                    } else if (itemBottom >= updateWindowTop && itemTop <= updateWindowBottom) {
                        if (numUniqueNames > 0) {
                            if (listScrollState.currentPhase === 'decelerating' && winnerCachedIdx !== -1 && winnerLiDomIndex !== -1) {
                                const offsetFromWinner = physicalIndex - winnerLiDomIndex;
                                let nameToShowIdx = (winnerCachedIdx + offsetFromWinner) % numUniqueNames;
                                if (nameToShowIdx < 0) nameToShowIdx += numUniqueNames;
                                li.textContent = _cachedParticipantList[nameToShowIdx] || "---";
                            } else {
                                li.textContent = _cachedParticipantList[Math.floor(Math.random() * numUniqueNames)] || "---";
                            }
                        } else {
                            li.textContent = getRandomChar() + getRandomChar() + "X";
                        }
                    } else {
                        if (!li.textContent || li.textContent.length < 2) {
                            if (numUniqueNames > 0) {
                                li.textContent = _cachedParticipantList[physicalIndex % numUniqueNames] || "Name";
                            } else {
                                li.textContent = getRandomChar();
                            }
                        }
                    }
                });
                listScrollState.lastTextUpdateTime = timestamp;
            }

            const currentItemPhysicalIndex = Math.floor(((-newTranslateY + pointerCenterY - itemFullHeight/2) / itemFullHeight));
            if (currentItemPhysicalIndex !== listScrollState.lastTickedItemGlobalIndex && canPlayTickSound) {
                if (OPTIONS.LIST_TICK_SOUND_KEY) { callPythonBackend('jsRequestSound', OPTIONS.LIST_TICK_SOUND_KEY); canPlayTickSound = false; setTimeout(() => { canPlayTickSound = true; }, tickSoundDebounceDelay); }
                listScrollState.lastTickedItemGlobalIndex = currentItemPhysicalIndex;
            }

            listAnimationFrameId = requestAnimationFrame(step);
        }
        listAnimationFrameId = requestAnimationFrame(step);
        animationSequenceTimeoutIds.push(listAnimationFrameId);
    });
}

// --- Triglavian Translation Logic ---
// ... (resetTriglavianState, createTriglavianBoxes, cycleTriglavianChars, pulseTriglavianBox, startTriglavianReveal, checkRevealCompletionTriglavian, showTriglavianBoxes remain same) ...
function resetTriglavianState() { console.log("Resetting Triglavian State"); if (triglavianCyclingIntervalId) clearInterval(triglavianCyclingIntervalId); triglavianCyclingIntervalId = null; if (triglavianRevealTimeoutId) clearTimeout(triglavianRevealTimeoutId); triglavianRevealTimeoutId = null; Object.values(trigTempRevealTimeouts).forEach(clearTimeout); trigTempRevealTimeouts = {}; triglavianBoxes.forEach(box => { if (box) { box.classList.remove('box-pulse', 'showing-reveal'); box.textContent = ''; } }); if(triglavianWinnerNameSpan) triglavianWinnerNameSpan.innerHTML = ''; if(triglavianWinnerDisplay) triglavianWinnerDisplay.classList.remove('visible', 'standalone'); if(triglavianBoxesRow) triglavianBoxesRow.classList.remove('visible'); trigRevealSequence = []; trigRevealedLetters = []; }
function createTriglavianBoxes() { 
    console.log("🔧 createTriglavianBoxes() called");
    if (!triglavianBoxesRow) { 
        console.error("🚨 createTriglavianBoxes: triglavianBoxesRow is null/undefined!"); 
        return; 
    }
    console.log(`🔧 createTriglavianBoxes: Current triglavianBoxes.length: ${triglavianBoxes.length}, expected: ${OPTIONS.TRIG_BOX_COUNT}`);
    if (triglavianBoxes.length !== OPTIONS.TRIG_BOX_COUNT) { 
        console.log("🔧 createTriglavianBoxes: Recreating boxes...");
        triglavianBoxesRow.innerHTML = ''; 
        triglavianBoxes = []; 
        for (let i = 0; i < OPTIONS.TRIG_BOX_COUNT; i++) { 
            const box = document.createElement('div'); 
            box.classList.add('triglavian-box'); 
            box.id = `trig-box-${i}`; 
            triglavianBoxesRow.appendChild(box); 
            triglavianBoxes.push(box); 
        } 
        console.log(`✅ createTriglavianBoxes: Created ${OPTIONS.TRIG_BOX_COUNT} Triglavian boxes.`); 
    } else {
        console.log("✅ createTriglavianBoxes: Triglavian boxes already exist");
    }
}
function cycleTriglavianChars() {
    // Debug: log cycling
    console.log('[Triglavian] cycleTriglavianChars called', Date.now());
    if (!bodyElement.classList.contains('show-triglavian')) {
        if (triglavianCyclingIntervalId) { clearInterval(triglavianCyclingIntervalId); cyclingIntervalId = null; }
        return;
    }
    if (triglavianBoxesRow && !triglavianBoxesRow.classList.contains('visible')) {
        triglavianBoxesRow.classList.add('visible');
    }
    if (triglavianBoxes.length !== OPTIONS.TRIG_BOX_COUNT) return;
    triglavianBoxes.forEach((box) => {
        if (box && !box.classList.contains('showing-reveal')) {
            box.textContent = getRandomTrigGlyph();
        }
    });
}
function pulseTriglavianBox(boxElement, duration = OPTIONS.TRIG_PULSE_DURATION_MS) { if (boxElement) { boxElement.classList.remove('box-pulse'); void boxElement.offsetWidth; boxElement.classList.add('box-pulse'); setTimeout(() => { if (boxElement) boxElement.classList.remove('box-pulse'); }, duration); } }
function startTriglavianReveal(winnerName, revealIntervalMs) {
    console.log(`Starting Triglavian reveal for: ${winnerName} with interval ${revealIntervalMs}ms`);
    if (!triglavianWinnerNameSpan || !triglavianWinnerDisplay || !triglavianBoxes || triglavianBoxes.length === 0 || !triglavianBoxesRow) {
        console.error("Triglavian elements not found. Aborting.");
        checkRevealCompletionTriglavian(winnerName);
        return;
    }
    const upperCaseWinner = winnerName.toUpperCase();
    const letterCounts = {};
    const nameLength = upperCaseWinner.length;
    trigRevealSequence = [];
    if (nameLength === 0) {
        console.warn("Triglavian reveal: Winner name empty.");
        checkRevealCompletionTriglavian(winnerName);
        return;
    }
    for (let i = 0; i < nameLength; i++) {
        const letter = upperCaseWinner[i];
        if (!letterCounts[letter]) letterCounts[letter] = 0;
        letterCounts[letter]++;
        trigRevealSequence.push({ index: i, letter: letter });
    }
    trigRevealSequence.sort((a, b) => letterCounts[b.letter] - letterCounts[a.letter] || a.index - b.index);
    console.log("Triglavian Reveal Sequence (Freq Ordered):", trigRevealSequence.map(item => item.letter + '@' + item.index));
    trigRevealedLetters = Array(nameLength).fill(OPTIONS.TRIG_PLACEHOLDER_CHAR);
    triglavianWinnerNameSpan.innerHTML = trigRevealedLetters.join('');
    triglavianWinnerNameSpan.classList.remove('revealed');
    triglavianWinnerDisplay.classList.add('visible', 'standalone');
    bodyElement.classList.remove('show-triglavian');
    if(triglavianRevealMode) triglavianRevealMode.classList.remove('visible');
    if(triglavianBoxesRow) triglavianBoxesRow.classList.remove('visible');
    if (triglavianRevealTimeoutId) clearTimeout(triglavianRevealTimeoutId);
    triglavianRevealTimeoutId = null;
    Object.values(trigTempRevealTimeouts).forEach(clearTimeout);
    trigTempRevealTimeouts = {};
    if (triglavianCyclingIntervalId) clearInterval(triglavianCyclingIntervalId);
    triglavianCyclingIntervalId = null;

    function revealNextLetterFrequency() {
        if (trigRevealSequence.length === 0) {
            console.log("Triglavian frequency reveal complete.");
            checkRevealCompletionTriglavian();
            return;
        }
        const itemToReveal = trigRevealSequence.shift();
        if (!itemToReveal) {
            console.error("Shifted undefined item.");
            checkRevealCompletionTriglavian();
            return;
        }
        const { index, letter } = itemToReveal;
        const availablePingIndices = triglavianBoxes.map((box, idx) => (box && !box.classList.contains('showing-reveal')) ? idx : -1).filter(idx => idx !== -1);
        const pingBoxIndex = availablePingIndices.length > 0 ? availablePingIndices[getRandomInt(0, availablePingIndices.length - 1)] : getRandomInt(0, triglavianBoxes.length - 1);
        const pingBox = triglavianBoxes[pingBoxIndex];
        if(pingBox) {
            pulseTriglavianBox(pingBox, OPTIONS.TRIG_SCAN_PING_DURATION_MS);
        }
        const revealDelayTimeout = setTimeout(() => {
            trigRevealedLetters[index] = letter;
            triglavianWinnerNameSpan.innerHTML = trigRevealedLetters.join('');
            const availableRevealIndices = triglavianBoxes.map((box, idx) => (box && idx !== pingBoxIndex && !box.classList.contains('showing-reveal')) ? idx : -1).filter(idx => idx !== -1);
            let revealBoxIndex = availableRevealIndices.length > 0 ? availableRevealIndices[getRandomInt(0, availableRevealIndices.length - 1)] : (pingBoxIndex + 1) % triglavianBoxes.length;
            const revealBox = triglavianBoxes[revealBoxIndex];
            if (revealBox) {
                if (trigTempRevealTimeouts[revealBoxIndex]) {
                    clearTimeout(trigTempRevealTimeouts[revealBoxIndex]);
                    revealBox.classList.remove('showing-reveal');
                    revealBox.textContent = '';
                }
                revealBox.classList.add('showing-reveal');
                revealBox.textContent = letter;
                revealBox.style.backgroundColor = '';
                // --- Spark effect ---
                const sparkCount = 8;
                const sparksContainer = document.createElement('div');
                sparksContainer.className = 'triglavian-sparks';
                for (let s = 0; s < sparkCount; s++) {
                    const spark = document.createElement('div');
                    spark.className = 'triglavian-spark';
                    // Random direction and distance
                    const angle = (2 * Math.PI * s) / sparkCount + (Math.random() - 0.5) * 0.3;
                    const dist = 22 + Math.random() * 10;
                    const x = Math.cos(angle) * dist;
                    const y = Math.sin(angle) * dist;
                    const rot = (angle * 180 / Math.PI + 90) + (Math.random() - 0.5) * 40;
                    spark.style.setProperty('--spark-x', `${x.toFixed(1)}px`);
                    spark.style.setProperty('--spark-y', `${y.toFixed(1)}px`);
                    spark.style.setProperty('--spark-rot', `${rot.toFixed(1)}deg`);
                    sparksContainer.appendChild(spark);
                }
                revealBox.appendChild(sparksContainer);
                // --- End spark effect ---
                pulseTriglavianBox(revealBox, OPTIONS.TRIG_PULSE_DURATION_MS);
                callPythonBackend('jsRequestSound', OPTIONS.SOUND_NOTIFICATION_KEY);
                if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.notifyGenericReveal === 'function')
                    NetworkAnimation.notifyGenericReveal(revealBox);
                const clearDelay = OPTIONS.TRIG_PULSE_DURATION_MS + OPTIONS.TRIG_TEMP_REVEAL_CLEAR_DELAY_MS;
                trigTempRevealTimeouts[revealBoxIndex] = setTimeout(() => {
                    if (revealBox) {
                        revealBox.classList.remove('showing-reveal');
                        revealBox.textContent = '';
                        // Remove sparks
                        const sparks = revealBox.querySelectorAll('.triglavian-sparks');
                        sparks.forEach(s => s.remove());
                    }
                    delete trigTempRevealTimeouts[revealBoxIndex];
                }, clearDelay);
            } else {
                console.warn("Could not find revealBox for index:", revealBoxIndex);
            }
            triglavianRevealTimeoutId = setTimeout(revealNextLetterFrequency, revealIntervalMs);
            animationSequenceTimeoutIds.push(triglavianRevealTimeoutId);
        }, OPTIONS.TRIG_SCAN_PING_DELAY_BEFORE_REVEAL_MS);
        animationSequenceTimeoutIds.push(revealDelayTimeout);
    }
    const startTimeout = setTimeout(revealNextLetterFrequency, OPTIONS.TRIG_REVEAL_START_DELAY_MS);
    animationSequenceTimeoutIds.push(startTimeout);
}
function checkRevealCompletionTriglavian() { console.log("Triglavian Reveal Sequence Complete."); if (triglavianRevealTimeoutId) clearTimeout(triglavianRevealTimeoutId); triglavianRevealTimeoutId = null; Object.values(trigTempRevealTimeouts).forEach(clearTimeout); trigTempRevealTimeouts = {}; if (triglavianWinnerNameSpan && triglavianWinnerNameSpan.textContent !== currentWinnerNameForCallback.toUpperCase()) triglavianWinnerNameSpan.textContent = currentWinnerNameForCallback.toUpperCase(); if (triglavianRevealMode) triglavianRevealMode.classList.add('slide-up'); const countdownStartTimeoutId = setTimeout(() => { startCountdownPhase(); }, OPTIONS.COUNTDOWN_START_DELAY_AFTER_TRIG_MS); animationSequenceTimeoutIds.push(countdownStartTimeoutId); console.log(`JS checkRevealCompletionTriglavian: Sending original name back: '${currentWinnerNameForCallback}'`); callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback); }
function checkRevealCompletionTriglavian() {
    console.log("Triglavian Reveal Sequence Complete.");
    if (triglavianRevealTimeoutId) clearTimeout(triglavianRevealTimeoutId);
    triglavianRevealTimeoutId = null;
    Object.values(trigTempRevealTimeouts).forEach(clearTimeout);
    trigTempRevealTimeouts = {};
    if (triglavianWinnerNameSpan) {
        if (triglavianWinnerNameSpan.textContent !== currentWinnerNameForCallback.toUpperCase()) {
            triglavianWinnerNameSpan.textContent = currentWinnerNameForCallback.toUpperCase();
        }
        triglavianWinnerNameSpan.classList.add('revealed');
    }
    if (triglavianRevealMode) triglavianRevealMode.classList.add('slide-up');
    const countdownStartTimeoutId = setTimeout(() => {
        startCountdownPhase();
    }, OPTIONS.COUNTDOWN_START_DELAY_AFTER_TRIG_MS);
    animationSequenceTimeoutIds.push(countdownStartTimeoutId);
    console.log(`JS checkRevealCompletionTriglavian: Sending original name back: '${currentWinnerNameForCallback}'`);
    callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback);
}
function showTriglavianBoxes() { if (triglavianBoxesRow) { triglavianBoxesRow.classList.add('visible'); } else { console.error("Triglavian boxes row not found!"); } }


// --- Node Path Reveal Logic (Mode 6) ---
// ... (resetNodePathState, createNodePathGrid, generateNodePath, createPathLines, revealVowelsInDisplay, startNodePathReveal, checkRevealCompletionNodePath remain same) ...
function _calculateAndStoreNodeCenters() { if (!nodePathGridContainer || nodeGrid.length === 0) return false; const containerRect = nodePathGridContainer.getBoundingClientRect(); if (containerRect.width === 0 || containerRect.height === 0) return false; const numRows = nodeGrid.length; const numCols = nodeGrid[0].length; for (let r = 0; r < numRows; r++) { for (let c = 0; c < numCols; c++) { const nodeData = nodeGrid[r]?.[c]; if (nodeData?.element) { const nodeElement = nodeData.element; const rect = nodeElement.getBoundingClientRect(); nodeData.center = { x: rect.left - containerRect.left + rect.width / 2, y: rect.top - containerRect.top + rect.height / 2 }; } } } return true; }
function resetNodePathState() { console.log("Resetting Node Path State"); if (nodePathGridContainer) { nodePathGridContainer.innerHTML = ''; nodePathGridContainer.classList.remove('visible'); nodePathGridContainer.style.gridTemplateColumns = ''; nodePathGridContainer.style.gridTemplateRows = ''; } if (nodePathWinnerDisplay) nodePathWinnerDisplay.classList.remove('visible'); if (nodePathWinnerNameSpan) nodePathWinnerNameSpan.textContent = ''; if (nodePathRevealTimeoutId) clearTimeout(nodePathRevealTimeoutId); nodePathRevealTimeoutId = null; if (nodePathActiveNodeTimeoutId) clearTimeout(nodePathActiveNodeTimeoutId); nodePathActiveNodeTimeoutId = null; nodeGrid = []; nodePathLines = {}; currentPath = []; nodePathSvgOverlay = null; nodePathGenerationAttempts = 0; nodePathWinnerDisplayState = []; }
function createNodePathGrid() { if (!nodePathGridContainer) { console.error("Node Path Grid Container not found!"); return false; } resetNodePathState(); const containerWidth = nodePathGridContainer.offsetWidth; const containerHeight = nodePathGridContainer.offsetHeight; if (containerWidth <= 0 || containerHeight <= 0) { console.error("Node Path Grid Container has no dimensions yet."); return false; } const nodeSize = parseVmin(getCssVariableValue('--node-path-node-size')) || 20; const gap = parseVmin(getCssVariableValue('--node-path-grid-gap')) || 5; const nodePlusGap = nodeSize + gap; const numCols = Math.max(3, Math.floor((containerWidth - gap) / nodePlusGap)); const numRows = Math.max(4, Math.floor((containerHeight - gap) / nodePlusGap)); console.log(`Creating Node Grid: ${numCols} cols x ${numRows} rows (NodeSize: ${nodeSize}px, Gap: ${gap}px)`); nodePathGridContainer.style.gridTemplateColumns = `repeat(${numCols}, 1fr)`; nodePathGridContainer.style.gridTemplateRows = `repeat(${numRows}, 1fr)`; nodeGrid = []; const fragment = document.createDocumentFragment(); for (let r = 0; r < numRows; r++) { nodeGrid[r] = []; for (let c = 0; c < numCols; c++) { const nodeElement = document.createElement('div'); nodeElement.classList.add('node-path-node'); nodeElement.dataset.row = r; nodeElement.dataset.col = c; fragment.appendChild(nodeElement); nodeGrid[r][c] = { element: nodeElement, row: r, col: c, center: null }; } } nodePathGridContainer.appendChild(fragment); nodePathSvgOverlay = document.createElementNS("http://www.w3.org/2000/svg", "svg"); nodePathSvgOverlay.classList.add('node-path-svg-overlay'); nodePathSvgOverlay.setAttribute('width', '100%'); nodePathSvgOverlay.setAttribute('height', '100%'); nodePathGridContainer.appendChild(nodePathSvgOverlay); requestAnimationFrame(() => { _calculateAndStoreNodeCenters(); }); return true; }
function generateNodePath() { if (nodeGrid.length === 0 || nodeGrid[0].length === 0) { console.error("Cannot generate path, grid not initialized."); return false; } if (nodePathGenerationAttempts >= OPTIONS.NODE_PATH_MAX_PATH_ATTEMPTS) { console.error("Max path generation attempts reached. Failing."); return false; } nodePathGenerationAttempts++; const numRows = nodeGrid.length; const numCols = nodeGrid[0].length; const visited = new Set(); currentPath = []; let startCol = getRandomInt(0, numCols - 1); let currentRow = 0; let currentCol = startCol; currentPath.push({ row: currentRow, col: currentCol }); visited.add(`${currentRow},${currentCol}`); let attempts = 0; const maxAttempts = numRows * numCols * 2; while (attempts < maxAttempts) { attempts++; let possibleMoves = []; const candidates = [ { dr: 1, dc: 0 }, { dr: 1, dc: -1 }, { dr: 1, dc: 1 }, { dr: 0, dc: -1 }, { dr: 0, dc: 1 } ]; for (const move of candidates) { const nextRow = currentRow + move.dr; const nextCol = currentCol + move.dc; if (nextRow >= 0 && nextRow < numRows && nextCol >= 0 && nextCol < numCols) { if (!visited.has(`${nextRow},${nextCol}`)) { possibleMoves.push({ row: nextRow, col: nextCol, priority: move.dr }); } } } if (possibleMoves.length === 0) { console.log("Path generation stuck, ending path."); break; } possibleMoves.sort((a, b) => b.priority - a.priority || Math.random() - 0.5); const nextNode = possibleMoves[0]; currentRow = nextNode.row; currentCol = nextNode.col; currentPath.push({ row: currentRow, col: currentCol }); visited.add(`${currentRow},${currentCol}`); if (currentRow === numRows - 1 && currentPath.length >= OPTIONS.NODE_PATH_MIN_PATH_LENGTH) { console.log("Path reached bottom row."); break; } if(currentPath.length >= OPTIONS.NODE_PATH_MIN_PATH_LENGTH && possibleMoves.every(m => m.priority === 0)) { if(Math.random() < 0.3) { console.log("Path ending early based on length and available moves."); break; } } } if (currentPath.length < OPTIONS.NODE_PATH_MIN_PATH_LENGTH && attempts < maxAttempts) { console.warn(`Generated path too short (${currentPath.length}). Retrying (Attempt ${nodePathGenerationAttempts}).`); return generateNodePath(); } if (attempts >= maxAttempts) { console.error("Max attempts reached during path generation."); } console.log(`Generated Path (${currentPath.length} nodes):`, currentPath.map(n => `(${n.row},${n.col})`).join(' -> ')); _calculateAndStoreNodeCenters(); createPathLines(); return true; }
function createPathLines() { if (!nodePathSvgOverlay || currentPath.length < 2) { console.warn("Node Path: Cannot create path lines."); return; } nodePathSvgOverlay.innerHTML = ''; nodePathLines = {}; for (let i = 0; i < currentPath.length - 1; i++) { const node1Coords = currentPath[i]; const node2Coords = currentPath[i + 1]; const data1 = nodeGrid[node1Coords.row]?.[node1Coords.col]; const data2 = nodeGrid[node2Coords.row]?.[node2Coords.col]; if (data1?.center && data2?.center) { const line = document.createElementNS("http://www.w3.org/2000/svg", "line"); line.setAttribute('x1', data1.center.x); line.setAttribute('y1', data1.center.y); line.setAttribute('x2', data2.center.x); line.setAttribute('y2', data2.center.y); line.classList.add('node-path-line'); const lineKey = `${node1Coords.row}c${node1Coords.col}-${node2Coords.row}c${node2Coords.col}`; nodePathLines[lineKey] = line; nodePathSvgOverlay.appendChild(line); } else { console.warn(`Node Path: Missing center data for line between (${node1Coords.row},${node1Coords.col}) and (${node2Coords.row},${node2Coords.col})`); } } }
function revealVowelsInDisplay(winnerNameUpper) { const vowels = "AEIOU"; for(let i = 0; i < winnerNameUpper.length; i++) { if (vowels.includes(winnerNameUpper[i])) { nodePathWinnerDisplayState[i] = winnerNameUpper[i]; } } if (nodePathWinnerNameSpan) { nodePathWinnerNameSpan.textContent = nodePathWinnerDisplayState.join(''); } console.log("Node Path: Vowels revealed."); if (OPTIONS.NODE_PATH_VOWEL_REVEAL_SOUND) { callPythonBackend('jsRequestSound', OPTIONS.NODE_PATH_VOWEL_REVEAL_SOUND); } }
function startNodePathReveal(winnerName) { console.log("Starting Node Path Reveal for:", winnerName); if (!nodePathGridContainer || !nodePathWinnerDisplay || !nodePathWinnerNameSpan) { console.error("Node path elements missing."); checkRevealCompletionNodePath(winnerName); return; } if (!createNodePathGrid()) { console.error("Failed to create node path grid."); checkRevealCompletionNodePath(winnerName); return; } const winnerNameUpper = winnerName.toUpperCase(); const winnerNameLength = winnerNameUpper.length; nodePathWinnerDisplayState = Array(winnerNameLength).fill(OPTIONS.NODE_PATH_PLACEHOLDER_CHAR); nodePathWinnerDisplay.classList.remove('visible'); if (nodePathWinnerNameSpan) nodePathWinnerNameSpan.textContent = nodePathWinnerDisplayState.join(''); nodePathGridContainer.classList.add('visible'); setTimeout(() => { nodeGrid.flat().forEach(nodeData => nodeData?.element?.classList.add('visible')); }, 50); setTimeout(() => { nodePathGenerationAttempts = 0; if (!generateNodePath() || currentPath.length < 2) { console.error("Failed to generate valid node path."); checkRevealCompletionNodePath(winnerName); return; } let step = 0; let previousNodeElement = null; const stepDuration = currentNodePathStepDuration; const midPointIndex = Math.floor(currentPath.length / 2); console.log(`Node Path: Starting reveal. Step duration: ${stepDuration}ms. Path length: ${currentPath.length}. Midpoint: ${midPointIndex}`); if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.resetRevealState === 'function') { NetworkAnimation.resetRevealState(); } function revealNextStep() { if (step >= currentPath.length) { if (nodePathRevealTimeoutId) { checkRevealCompletionNodePath(winnerName); } nodePathRevealTimeoutId = null; return; } const nodeCoords = currentPath[step]; const nodeData = nodeGrid[nodeCoords.row]?.[nodeCoords.col]; if (!nodeData || !nodeData.element) { console.error(`Node data not found for step ${step}. Stopping.`); checkRevealCompletionNodePath(winnerName); return; } const currentNodeElement = nodeData.element; const isMidpoint = (step === midPointIndex); let nextStepDelay = stepDuration; if (nodePathActiveNodeTimeoutId) clearTimeout(nodePathActiveNodeTimeoutId); if (previousNodeElement) { previousNodeElement.classList.remove('active', 'vowel-reveal-node'); } currentNodeElement.classList.add('path', 'active'); if (step === currentPath.length - 1) currentNodeElement.classList.add('target'); if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.notifyGenericReveal === 'function') NetworkAnimation.notifyGenericReveal(currentNodeElement); if (step > 0) { const prevCoords = currentPath[step - 1]; const lineKey = `${prevCoords.row}c${prevCoords.col}-${nodeCoords.row}c${nodeCoords.col}`; const reverseLineKey = `${nodeCoords.row}c${nodeCoords.col}-${prevCoords.row}c${prevCoords.col}`; const lineElement = nodePathLines[lineKey] || nodePathLines[reverseLineKey]; if (lineElement) requestAnimationFrame(() => { lineElement.classList.add('visible'); }); } callPythonBackend('jsRequestSound', OPTIONS.SOUND_NOTIFICATION_KEY); if (isMidpoint) { console.log(`Node Path: Midpoint (Step ${step}). Vowel reveal & pause.`); currentNodeElement.classList.add('vowel-reveal-node'); revealVowelsInDisplay(winnerNameUpper); if (nodePathWinnerDisplay) nodePathWinnerDisplay.classList.add('visible'); nextStepDelay += OPTIONS.NODE_PATH_MIDPOINT_PAUSE_MS; } else { currentNodeElement.classList.remove('vowel-reveal-node'); } nodePathActiveNodeTimeoutId = setTimeout(() => { currentNodeElement.classList.remove('active'); }, stepDuration * 1.5); animationSequenceTimeoutIds.push(nodePathActiveNodeTimeoutId); previousNodeElement = currentNodeElement; step++; if (step < currentPath.length) { nodePathRevealTimeoutId = setTimeout(revealNextStep, nextStepDelay); animationSequenceTimeoutIds.push(nodePathRevealTimeoutId); } else { nodePathRevealTimeoutId = setTimeout(() => checkRevealCompletionNodePath(winnerName), nextStepDelay); animationSequenceTimeoutIds.push(nodePathRevealTimeoutId); } } const revealStartTimeout = setTimeout(revealNextStep, OPTIONS.NODE_PATH_REVEAL_START_DELAY_MS); animationSequenceTimeoutIds.push(revealStartTimeout); }, OPTIONS.NODE_PATH_GRID_APPEAR_DELAY_MS); }
function checkRevealCompletionNodePath(winnerName = "Unknown") { console.log("Node Path Reveal Complete."); if (nodePathRevealTimeoutId) clearTimeout(nodePathRevealTimeoutId); nodePathRevealTimeoutId = null; if (nodePathActiveNodeTimeoutId) clearTimeout(nodePathActiveNodeTimeoutId); nodePathActiveNodeTimeoutId = null; if (currentPath.length > 0) { const lastCoords = currentPath[currentPath.length - 1]; const lastNodeData = nodeGrid[lastCoords.row]?.[lastCoords.col]; if(lastNodeData?.element) { lastNodeData.element.classList.remove('active', 'vowel-reveal-node'); lastNodeData.element.classList.add('target'); } } const winnerDisplayDelay = parseFloat(getCssVariableValue('--node-path-winner-reveal-delay')) || OPTIONS.NODE_PATH_WINNER_REVEAL_DELAY_MS; const showWinnerTimeout = setTimeout(() => { if (!nodePathWinnerDisplay) return; if (nodePathWinnerNameSpan) nodePathWinnerNameSpan.textContent = winnerName.toUpperCase(); nodePathWinnerDisplay.classList.add('visible'); requestAnimationFrame(() => { if (_calculateAndStoreNodeCenters()) { for (const lineKey in nodePathLines) { const lineElement = nodePathLines[lineKey]; if (lineElement) { const [node1Str, node2Str] = lineKey.split('-'); const [r1, c1] = node1Str.replace('c', ',').split(',').map(Number); const [r2, c2] = node2Str.replace('c', ',').split(',').map(Number); const data1 = nodeGrid[r1]?.[c1]; const data2 = nodeGrid[r2]?.[c2]; if (data1?.center && data2?.center) { lineElement.setAttribute('x1', data1.center.x); lineElement.setAttribute('y1', data1.center.y); lineElement.setAttribute('x2', data2.center.x); lineElement.setAttribute('y2', data2.center.y); } } } } const revealMode = document.querySelector('.reveal-mode.visible'); if (revealMode) revealMode.classList.add('slide-up'); callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback); const countdownStartDelay = parseFloat(getCssVariableValue('--countdown-start-delay-after-node-path-ms')) || OPTIONS.COUNTDOWN_START_DELAY_AFTER_NODE_PATH_MS; const countdownStartTimeoutId = setTimeout(() => { startCountdownPhase(); }, countdownStartDelay); animationSequenceTimeoutIds.push(countdownStartTimeoutId); }); }, winnerDisplayDelay); animationSequenceTimeoutIds.push(showWinnerTimeout); }


// --- Triglavian Conduit Logic (Mode 7) ---
// ... (resetTrigConduitState, createTriglavianConduitNodes, startTriglavianConduitAnimation, checkRevealCompletionTrigConduit remain same) ...
function resetTrigConduitState() {
    console.log("Resetting Triglavian Conduit State");
    if (trigConduitIntervalId) { clearInterval(trigConduitIntervalId); trigConduitIntervalId = null; }
    Object.values(trigConduitScrambleIntervals).forEach(clearInterval);
    trigConduitScrambleIntervals = {};
    trigConduitNodes = [];
    trigConduitRevealPath = [];
    trigConduitNamePlaceholders = [];
    if (trigConduitNodesContainer) {
        trigConduitNodesContainer.innerHTML = '';
        trigConduitNodesContainer.classList.remove('visible', 'final-pulse-effect');
    }
    trigConduitSvgOverlay = null;
    trigConduitCore = null;
    if (trigConduitWinnerNameSpan) {
        trigConduitWinnerNameSpan.innerHTML = '';
        trigConduitWinnerNameSpan.classList.remove('revealed');
    }
    if (trigConduitWinnerDisplay) trigConduitWinnerDisplay.classList.remove('visible');
}

function createTriglavianConduitNodes() {
    if (!trigConduitNodesContainer) { console.error("Trig Conduit nodes container not found!"); return false; }
    trigConduitNodesContainer.innerHTML = '';
    trigConduitNodes = [];

    // NEW: Create SVG overlay for lines
    trigConduitSvgOverlay = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    trigConduitSvgOverlay.classList.add('trig-conduit-svg-overlay');
    trigConduitNodesContainer.appendChild(trigConduitSvgOverlay);

    const numNodes = OPTIONS.TRIG_CONDUIT_NODE_COUNT;
    const containerSize = trigConduitNodesContainer.offsetWidth;
    const radius = containerSize / 2.8;
    const angleStep = (2 * Math.PI) / numNodes;
    const nodeSize = parseVmin(getCssVariableValue('--trig-conduit-node-size')) || 40;

    for (let i = 0; i < numNodes; i++) {
        const node = document.createElement('div');
        node.classList.add('trig-conduit-node');
        node.id = `trig-conduit-node-${i}`;

        const angle = i * angleStep - (Math.PI / 2);
        const centerX = (containerSize / 2) + (radius * Math.cos(angle));
        const centerY = (containerSize / 2) + (radius * Math.sin(angle));
        node.style.left = `${centerX - nodeSize / 2}px`;
        node.style.top = `${centerY - nodeSize / 2}px`;

        const rotationDeg = (angle * 180 / Math.PI) + 90;
        node.style.setProperty('--node-rotation', `${rotationDeg}deg`);

        trigConduitNodesContainer.appendChild(node);
        trigConduitNodes.push(node);

        setTimeout(() => { node.classList.add('visible'); }, OPTIONS.TRIG_CONDUIT_NODE_APPEAR_STAGGER_MS * i);
    }
    // Create central conduit core
    const core = document.createElement('div');
    core.classList.add('trig-conduit-core');
    core.style.left = `50%`;
    core.style.top = `50%`;
    trigConduitNodesContainer.appendChild(core);
    // store reference for later pulses
    trigConduitCore = core;

    // NEW: create three visual arms (Y-shaped) that converge on the center
    const armCount = 3;
    for (let a = 0; a < armCount; a++) {
        const arm = document.createElement('div');
        arm.classList.add('trig-conduit-arm');
        const angle = a * (2 * Math.PI / armCount) - (Math.PI / 2);
        const deg = angle * 180 / Math.PI;
        // center the arm and rotate so the narrow end points to center
        arm.style.left = '50%';
        arm.style.top = '50%';
        arm.style.transform = `translate(-50%, -50%) rotate(${deg}deg)`;
        // stagger reveal for dramatic effect
        arm.style.transitionDelay = `${(a * 120)}ms`;
        trigConduitNodesContainer.appendChild(arm);
    }

    // store node centers for later animation targeting
    trigConduitNodeCenters = trigConduitNodes.map(node => ({
        x: node.offsetLeft + node.offsetWidth / 2,
        y: node.offsetTop + node.offsetHeight / 2
    }));
    // NEW: Calculate centers and draw initial faint lines after nodes are positioned
    requestAnimationFrame(() => {
        const nodeCenters = trigConduitNodes.map(node => {
            return {
                x: node.offsetLeft + node.offsetWidth / 2,
                y: node.offsetTop + node.offsetHeight / 2,
            };
        });

        // create inter-node mesh lines (faint) and spokes to the core
        for (let i = 0; i < numNodes; i++) {
            for (let j = i + 1; j < numNodes; j++) {
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute('x1', nodeCenters[i].x);
                line.setAttribute('y1', nodeCenters[i].y);
                line.setAttribute('x2', nodeCenters[j].x);
                line.setAttribute('y2', nodeCenters[j].y);
                line.classList.add('trig-conduit-line');
                // Create a consistent key for the line
                line.id = `conduit-line-${i}-${j}`;
                trigConduitSvgOverlay.appendChild(line);
            }
            // spoke to center
            const spoke = document.createElementNS("http://www.w3.org/2000/svg", "line");
            spoke.setAttribute('x1', nodeCenters[i].x);
            spoke.setAttribute('y1', nodeCenters[i].y);
            spoke.setAttribute('x2', containerSize/2);
            spoke.setAttribute('y2', containerSize/2);
            spoke.classList.add('trig-conduit-spoke');
            spoke.id = `conduit-spoke-${i}`;
            trigConduitSvgOverlay.appendChild(spoke);
        }
        // Also ensure arms visually point to center by updating their transform origin and length
        const arms = trigConduitNodesContainer.querySelectorAll('.trig-conduit-arm');
        // Staggered reveal for the three arms so they become visible after node positioning
        arms.forEach((arm, idx) => {
            // start slightly after nodes appear
            const delay = 200 + (idx * 120);
            // ensure initial opacity state is consistent
            arm.style.opacity = '0';
            setTimeout(() => {
                try {
                    arm.classList.add('visible');
                    // small nudge to ensure transition triggers in some WebEngine builds
                    arm.style.transform = arm.style.transform + ' translateZ(0)';
                } catch (e) {
                    console.warn('Failed to show trig-conduit arm', e);
                }
            }, delay);
        });
    });

    console.log(`Created ${numNodes} Trig Conduit nodes and SVG overlay.`);
    return true;
}

// Animate a small orb from (fromX,fromY) to (toX,toY) then call callback
function animateOrb(fromX, fromY, toX, toY, glyph, callback) {
    if (!trigConduitNodesContainer) { if (callback) callback(); return; }
    const orb = document.createElement('div');
    orb.className = 'conduit-orb';
    orb.style.left = `${fromX}px`;
    orb.style.top = `${fromY}px`;
    orb.textContent = '';
    trigConduitNodesContainer.appendChild(orb);

    // Force layout then animate
    requestAnimationFrame(() => {
        const dx = toX - fromX;
        const dy = toY - fromY;
        // shorter, punchier motion
        orb.style.transition = 'transform 0.45s cubic-bezier(.2,.9,.2,1), opacity 0.25s ease-out';
        orb.style.transform = `translate(${dx}px, ${dy}px) scale(0.6)`;
        orb.style.opacity = '1';
        // after transition, reveal glyph at target
        const onEnd = () => {
            try {
                if (glyph && typeof glyph === 'string' && glyph.length > 0) {
                    if (callback) callback(glyph);
                } else if (callback) callback();
            } finally {
                if (orb && orb.parentNode) orb.parentNode.removeChild(orb);
            }
        };
        orb.addEventListener('transitionend', onEnd, { once: true });
        // safety timeout
        setTimeout(() => { if (document.body.contains(orb)) { onEnd(); } }, 700);
    });
}

// Send orbs from a node to one or more placeholder indices
function sendOrbsFromNode(nodeIndex, targetIndices) {
    if (!trigConduitNodesContainer) return;
    const nodeCenter = trigConduitNodeCenters?.[nodeIndex];
    if (!nodeCenter) return;
    targetIndices.forEach((ti, i) => {
        const span = trigConduitNamePlaceholders[ti];
        if (!span) return;
        const spanRect = span.getBoundingClientRect();
        const containerRect = trigConduitNodesContainer.getBoundingClientRect();
        const toX = spanRect.left + spanRect.width / 2 - containerRect.left;
        const toY = spanRect.top + spanRect.height / 2 - containerRect.top;
        const fromX = nodeCenter.x;
        const fromY = nodeCenter.y;
        const glyph = getRandomTrigGlyph();
        // stagger slightly
        setTimeout(() => {
            animateOrb(fromX, fromY, toX, toY, glyph, (g) => {
                span.textContent = g;
                span.classList.remove('letter-placeholder');
                span.classList.add('letter-arrived');
                // small flash
                span.animate([{ transform: 'scale(1.2)', opacity: 1 }, { transform: 'scale(1)', opacity: 1 }], { duration: 250, easing: 'ease-out' });
            });
        }, i * 80);
    });
}

function startTriglavianConduitAnimation(winnerName, stepDurationMs) {
    console.log(`Starting Trig Conduit animation for: ${winnerName}, step: ${stepDurationMs}ms`);
    if (!trigConduitNodesContainer || !trigConduitWinnerDisplay || !trigConduitWinnerNameSpan) {
        console.error("Trig Conduit elements missing."); checkRevealCompletionTrigConduit(winnerName); return;
    }
    if (!createTriglavianConduitNodes()) { console.error("Failed to create Trig Conduit nodes."); checkRevealCompletionTrigConduit(winnerName); return; }

    trigConduitNodesContainer.classList.add('visible');
    trigConduitWinnerDisplay.classList.add('visible');
    trigConduitWinnerNameSpan.classList.remove('revealed');

    const winnerNameUpper = winnerName.toUpperCase();
    const nameLength = winnerNameUpper.length;
    trigConduitWinnerNameSpan.innerHTML = '';
    trigConduitNamePlaceholders = [];
    for (let i = 0; i < nameLength; i++) {
        const span = document.createElement('span');
        span.textContent = OPTIONS.TRIG_CONDUIT_PLACEHOLDER_CHAR;
        span.classList.add('letter-placeholder');
        trigConduitWinnerNameSpan.appendChild(span);
        trigConduitNamePlaceholders.push(span);
    }
    // NEW: Generate a randomized path that visits each node once
    trigConduitRevealPath = shuffleArray([...Array(OPTIONS.TRIG_CONDUIT_NODE_COUNT).keys()]);
    console.log("Trig Conduit Reveal Path:", trigConduitRevealPath.join(' -> '));

    let currentStepIndex = 0;

    if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.resetRevealState === 'function') { NetworkAnimation.resetRevealState(); }

    // NEW: Separate function for the stabilization (power-up) phase
    function stabilizationStep() {
        if (currentStepIndex >= trigConduitRevealPath.length) {
            // Last node has been activated, now trigger the name scramble
            triggerNameScramble();
            return;
        }
        const currentNodeIndex = trigConduitRevealPath[currentStepIndex];
        const node = trigConduitNodes[currentNodeIndex];

        if (node) {
            // Deactivate previous node and mark its path as complete
            if (currentStepIndex > 0) {
                const prevNodeIndex = trigConduitRevealPath[currentStepIndex - 1];
                if (trigConduitNodes[prevNodeIndex]) {
                    trigConduitNodes[prevNodeIndex].classList.remove('active');
                    trigConduitNodes[prevNodeIndex].classList.add('path-complete');
                }
            }

            // Animate the line connecting to the previous node and make it stable
            if (currentStepIndex > 0) {
                const prevNodeIndex = trigConduitRevealPath[currentStepIndex - 1];
                const lineKey = `conduit-line-${Math.min(prevNodeIndex, currentNodeIndex)}-${Math.max(prevNodeIndex, currentNodeIndex)}`;
                const lineElement = document.getElementById(lineKey);
                if (lineElement) {
                    lineElement.classList.add('stable');
                }
            }

            node.classList.add('active');
            // make core pulse and enable spoke for this node
            try {
                if (trigConduitCore) {
                    trigConduitCore.classList.add('pulse');
                    // remove pulse class after animation completes so it can be re-triggered
                    setTimeout(() => { try { trigConduitCore.classList.remove('pulse'); } catch(e){} }, 800);
                }
                const spokeEl = document.getElementById(`conduit-spoke-${currentNodeIndex}`);
                if (spokeEl) {
                    spokeEl.classList.add('active');
                }
                // Apply node tilt (lean-in) towards the core while the spoke is active
                try {
                    if (node) {
                        // Apply static rotational-lean preset (one-shot)
                        node.style.setProperty('--node-lean-x', '4px');
                        node.style.setProperty('--node-lean-y', '-3px');
                        node.style.setProperty('--node-lean-rot', '-6deg');
                    }
                } catch(e) { console.warn('Failed to apply node lean', e); }
            } catch (e) { console.warn('Error activating core/spoke', e); }
            // emit a small orb or two from this node to random placeholder positions to show powering-up
            try {
                if (trigConduitNamePlaceholders && trigConduitNamePlaceholders.length > 0) {
                    const availableIndices = trigConduitNamePlaceholders.map((s, idx) => ({ s, idx })).filter(o => o.s && o.s.classList && o.s.classList.contains && o.s.classList.contains('letter-placeholder')).map(o => o.idx);
                    if (availableIndices.length === 0) {
                        // fallback: pick random indices
                        const r = getRandomInt(0, trigConduitNamePlaceholders.length - 1);
                        sendOrbsFromNode(currentNodeIndex, [r]);
                    } else {
                        const picks = shuffleArray(availableIndices).slice(0, Math.min(2, availableIndices.length));
                                sendOrbsFromNode(currentNodeIndex, picks);
                                // small delay to then dim the spoke after orbs are emitted
                                setTimeout(() => {
                                    try {
                                        const spokeEl2 = document.getElementById(`conduit-spoke-${currentNodeIndex}`);
                                        if (spokeEl2) spokeEl2.classList.remove('active');
                                        // also clear node lean variables
                                        try {
                                            if (node) {
                                                node.style.removeProperty('--node-lean-x');
                                                node.style.removeProperty('--node-lean-y');
                                                node.style.removeProperty('--node-lean-rot');
                                            }
                                        } catch (e) {}
                                    } catch (e) {}
                                }, Math.max(400, stepDurationMs * 0.6));
                    }
                }
            } catch (e) { console.warn('Error emitting conduit orb during stabilization', e); }
            callPythonBackend('jsRequestSound', OPTIONS.SOUND_NOTIFICATION_KEY);
        }
        currentStepIndex++;

        trigConduitIntervalId = setTimeout(stabilizationStep, stepDurationMs);
        animationSequenceTimeoutIds.push(trigConduitIntervalId);
    }

    // NEW: Separate function for the decoding (scramble) phase
    function triggerNameScramble() {
        // Deactivate the final node
        const lastNodeIndex = trigConduitRevealPath[trigConduitRevealPath.length - 1];
        if (trigConduitNodes[lastNodeIndex]) {
            trigConduitNodes[lastNodeIndex].classList.remove('active');
            trigConduitNodes[lastNodeIndex].classList.add('path-complete');
        }

    callPythonBackend('jsRequestSound', OPTIONS.SOUND_CONDUIT_STABLE_KEY);
    // show a stronger final effect on core
        try {
            if (trigConduitCore) {
                trigConduitCore.classList.add('stable');
                setTimeout(() => { try { trigConduitCore.classList.remove('stable'); } catch(e){} }, 1400);
            }
        } catch(e){}

        let revealedCount = 0;
        trigConduitNamePlaceholders.forEach((span, index) => {
            let scrambleCycles = 0;
            const scrambleInterval = OPTIONS.TRIG_CONDUIT_SCRAMBLE_DURATION_MS / OPTIONS.TRIG_CONDUIT_SCRAMBLE_CYCLES_PER_CHAR;
            // send a decoding orb from a random node aimed at this placeholder
                try {
                const nodeToUse = getRandomInt(0, trigConduitNodes.length - 1);
                // briefly highlight spoke when decoding orb is sent and tilt node
                const spokeEl = document.getElementById(`conduit-spoke-${nodeToUse}`);
                const nodeEl = trigConduitNodes[nodeToUse];
                if (spokeEl) spokeEl.classList.add('active');
                // apply a short lean for scramble highlight
                try {
                    if (nodeEl) {
                        // Apply static rotational-lean preset for scramble highlight
                        nodeEl.style.setProperty('--node-lean-x', '4px');
                        nodeEl.style.setProperty('--node-lean-y', '-3px');
                        nodeEl.style.setProperty('--node-lean-rot', '-6deg');
                    }
                } catch(e) { console.warn('Failed to apply scramble node lean', e); }
                setTimeout(() => sendOrbsFromNode(nodeToUse, [index]), index * 60);
                setTimeout(() => { 
                    if (spokeEl) spokeEl.classList.remove('active'); 
                    try { if (nodeEl) { nodeEl.style.removeProperty('--node-lean-x'); nodeEl.style.removeProperty('--node-lean-y'); nodeEl.style.removeProperty('--node-lean-rot'); } } catch(e){}
                }, index * 60 + 500);
            } catch (e) { /* ignore */ }

            trigConduitScrambleIntervals[index] = setInterval(() => {
                span.textContent = getRandomTrigGlyph();
                scrambleCycles++;
                if (scrambleCycles >= OPTIONS.TRIG_CONDUIT_SCRAMBLE_CYCLES_PER_CHAR) {
                    clearInterval(trigConduitScrambleIntervals[index]);
                    delete trigConduitScrambleIntervals[index];
                    span.textContent = winnerNameUpper[index];
                    span.classList.remove('letter-placeholder');
                    span.classList.add('letter-revealed');
                    revealedCount++;

                    // When the last letter is revealed, call the completion function
                    if (revealedCount === nameLength) {
                        checkRevealCompletionTrigConduit(winnerName);
                    }
                }
            }, scrambleInterval);
            animationSequenceTimeoutIds.push(trigConduitScrambleIntervals[index]);
        });
    }

    trigConduitIntervalId = setTimeout(stabilizationStep, stepDurationMs / 2 + OPTIONS.TRIG_CONDUIT_NODE_APPEAR_STAGGER_MS * OPTIONS.TRIG_CONDUIT_NODE_COUNT);
    animationSequenceTimeoutIds.push(trigConduitIntervalId);
}

function checkRevealCompletionTrigConduit(winnerName = "Unknown") {
    console.log("Triglavian Conduit Reveal Complete.");
    if (trigConduitIntervalId) { clearTimeout(trigConduitIntervalId); trigConduitIntervalId = null; }
    Object.values(trigConduitScrambleIntervals).forEach(clearInterval);
    trigConduitScrambleIntervals = {};

    trigConduitNodes.forEach((node, index) => {
        if (node) node.classList.remove('active');
    });
    if (trigConduitNodesContainer) trigConduitNodesContainer.classList.add('final-pulse-effect');

    if (trigConduitWinnerNameSpan) {
        const winnerNameUpper = winnerName.toUpperCase();
        let finalHtml = "";
        for(let i = 0; i < winnerNameUpper.length; i++) {
            finalHtml += `<span class="letter-revealed">${winnerNameUpper[i]}</span>`;
        }
        trigConduitWinnerNameSpan.innerHTML = finalHtml;
        trigConduitWinnerNameSpan.classList.add('revealed');
    }

    callPythonBackend('jsRequestSound', OPTIONS.SOUND_CONDUIT_STABLE_KEY);

    const revealMode = document.querySelector('.reveal-mode.visible');
    if (revealMode) revealMode.classList.add('slide-up');

    const countdownStartTimeoutId = setTimeout(() => {
        startCountdownPhase();
    }, OPTIONS.TRIG_CONDUIT_COUNTDOWN_DELAY_MS);
    animationSequenceTimeoutIds.push(countdownStartTimeoutId);

    console.log(`JS checkRevealCompletionTrigConduit: Sending original name back: '${currentWinnerNameForCallback}'`);
    callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback);
}


// --- Triglavian Code Reveal Logic ---
// ... (resetTrigCodeRevealState, generateTriglavianCode, populateTrigCodeParticipants, startTrigCodeReveal, revealNextTrigCodeChar, checkRevealCompletionTrigCode remain same) ...
function resetTrigCodeRevealState() {
    console.log("Resetting Triglavian Code Reveal State");
    if (trigCodeRevealIntervalId) { clearInterval(trigCodeRevealIntervalId); trigCodeRevealIntervalId = null; }
    if (trigCodeParticipantsContainer) trigCodeParticipantsContainer.innerHTML = '';
    if (trigCodeWinnerCodeDisplay) trigCodeWinnerCodeDisplay.innerHTML = '';
    if (trigCodeWinnerNameDisplay) trigCodeWinnerNameDisplay.classList.remove('visible');
    if (trigCodeWinnerNameSpan) trigCodeWinnerNameSpan.textContent = '';

    trigCodeParticipantsData = [];
    trigCodeWinnerCode = "";
    trigCodeRevealedChars = [];
    trigCodeCurrentRevealIndex = 0;
    currentTrigCodeCharSet = OPTIONS.TRIG_CODE_DEFAULT_CHAR_SET;
    currentTrigCodeFinalistCount = OPTIONS.TRIG_CODE_DEFAULT_FINALIST_COUNT;
}

function generateTriglavianCode(length, charSet = OPTIONS.TRIG_CODE_DEFAULT_CHAR_SET) {
    let code = "";
    const effectiveCharSet = (typeof charSet === 'string' && charSet.length > 0) ? charSet : OPTIONS.TRIG_CODE_DEFAULT_CHAR_SET;
    if (effectiveCharSet.length === 0) {
        console.error("Trig Code: Character set is empty! Using fallback 'X'.");
        return 'X'.repeat(length);
    }
    for (let i = 0; i < length; i++) {
        code += effectiveCharSet[Math.floor(Math.random() * effectiveCharSet.length)];
    }
    return code;
}

function populateTrigCodeParticipants(winnerName, allParticipants, codeLength, charSet, finalistTargetCount) {
    if (!trigCodeParticipantsContainer) {
        console.error("Trig Code Participants container not found!");
        return false;
    }
    trigCodeParticipantsContainer.innerHTML = '';
    trigCodeParticipantsData = [];
    currentTrigCodeCharSet = (typeof charSet === 'string' && charSet.length > 0) ? charSet : OPTIONS.TRIG_CODE_DEFAULT_CHAR_SET;
    currentTrigCodeFinalistCount = finalistTargetCount || OPTIONS.TRIG_CODE_DEFAULT_FINALIST_COUNT;

    const participantsToUse = (allParticipants && allParticipants.length > 0) ? [...allParticipants] : [..._cachedParticipantList];
    if (!participantsToUse || participantsToUse.length === 0) {
        console.warn("populateTrigCodeParticipants: No participants available.");
        trigCodeParticipantsContainer.innerHTML = '<div>--- NO ENTRANTS ---</div>';
        return false;
    }

    if (!participantsToUse.includes(winnerName)) {
        console.warn(`Winner "${winnerName}" not in participant list. Adding.`);
        participantsToUse.push(winnerName);
    }
    const shuffledDisplayParticipants = shuffleArray(participantsToUse);
    const assignedNonWinnerCodes = new Set();

    trigCodeWinnerCode = generateTriglavianCode(codeLength, currentTrigCodeCharSet);
    console.log(`Trig Code: Generated Winner Code for ${winnerName}: ${trigCodeWinnerCode}`);

    shuffledDisplayParticipants.forEach(name => {
        let participantCode;
        if (name === winnerName) {
            participantCode = trigCodeWinnerCode;
        } else {
            let attempts = 0;
            const maxAttemptsPerParticipant = 50;
            let minMutations = OPTIONS.TRIG_CODE_MIN_MUTATIONS;
            let maxMutations = OPTIONS.TRIG_CODE_MAX_MUTATIONS;

            maxMutations = Math.min(maxMutations, codeLength);
            minMutations = Math.min(minMutations, maxMutations);
            if (minMutations <=0) minMutations = 1; // Ensure at least one mutation

            do {
                let mutatedCodeArray = trigCodeWinnerCode.split('');
                const mutationsToApply = getRandomInt(minMutations, maxMutations);
                const mutationIndices = new Set();

                while(mutationIndices.size < mutationsToApply && mutationIndices.size < codeLength) {
                    mutationIndices.add(getRandomInt(0, codeLength - 1));
                }

                mutationIndices.forEach(idx => {
                    let newChar;
                    let charAttempts = 0;
                    do {
                        newChar = currentTrigCodeCharSet[Math.floor(Math.random() * currentTrigCodeCharSet.length)];
                        charAttempts++;
                    } while (newChar === mutatedCodeArray[idx] && charAttempts < 10);
                    mutatedCodeArray[idx] = newChar;
                });
                participantCode = mutatedCodeArray.join('');
                attempts++;
            } while ((participantCode === trigCodeWinnerCode || assignedNonWinnerCodes.has(participantCode)) && attempts < maxAttemptsPerParticipant);

            if (participantCode === trigCodeWinnerCode && attempts >= maxAttemptsPerParticipant) {
                console.warn(`Trig Code: Force-mutating code for ${name} again as it matched winner's after many attempts.`);
                let diffIndex = getRandomInt(0, codeLength - 1);
                let newChar;
                let forceAttempts = 0;
                do {
                    newChar = currentTrigCodeCharSet[Math.floor(Math.random() * currentTrigCodeCharSet.length)];
                    forceAttempts++;
                } while (newChar === participantCode[diffIndex] && forceAttempts < 20);
                let tempArray = participantCode.split('');
                tempArray[diffIndex] = newChar;
                participantCode = tempArray.join('');
            }
            assignedNonWinnerCodes.add(participantCode);
        }

        const itemDiv = document.createElement('div');
        itemDiv.classList.add('trig-code-participant-item');
        const nameSpan = document.createElement('span');
        nameSpan.classList.add('name');
        nameSpan.textContent = name;
        const codeSpan = document.createElement('span');
        codeSpan.classList.add('code');
        codeSpan.innerHTML = participantCode.split('').map(char => `<span>${char}</span>`).join('');

        itemDiv.appendChild(nameSpan);
        itemDiv.appendChild(codeSpan);
        trigCodeParticipantsContainer.appendChild(itemDiv);

        trigCodeParticipantsData.push({
            name: name,
            code: participantCode,
            element: itemDiv,
            codeElement: codeSpan,
            isEliminated: false,
            isVisiblyRemoved: false
        });
    });
    console.log(`Trig Code: Populated ${trigCodeParticipantsData.length} participants. Finalist target: ${currentTrigCodeFinalistCount}`);
    return true;
}


function startTrigCodeReveal(winnerName, codeLength, revealSpeedLabel, charSetFromOptions, finalistCount) {
    console.log(`Starting Trig Code Reveal for: ${winnerName}, Code Length: ${codeLength}, Speed: ${revealSpeedLabel}, Finalists: ${finalistCount}`);
    if (!trigCodeRevealMode || !trigCodeParticipantsContainer || !trigCodeWinnerCodeDisplay || !trigCodeWinnerNameDisplay || !trigCodeWinnerNameSpan) {
        console.error("Trig Code Reveal elements missing.");
        checkRevealCompletionTrigCode(winnerName);
        return;
    }

    currentTrigCodeCharSet = (typeof charSetFromOptions === 'string' && charSetFromOptions.length > 0)
                                ? charSetFromOptions
                                : OPTIONS.TRIG_CODE_DEFAULT_CHAR_SET;
    currentTrigCodeFinalistCount = finalistCount || OPTIONS.TRIG_CODE_DEFAULT_FINALIST_COUNT;


    switch (revealSpeedLabel) {
        case 'Fast': currentTrigCodeRevealStepDuration = OPTIONS.TRIG_CODE_REVEAL_INTERVAL_MS_FAST; break;
        case 'Slow': currentTrigCodeRevealStepDuration = OPTIONS.TRIG_CODE_REVEAL_INTERVAL_MS_SLOW; break;
        default: currentTrigCodeRevealStepDuration = OPTIONS.TRIG_CODE_REVEAL_INTERVAL_MS_NORMAL;
    }

    resetTrigCodeRevealState();
    currentTrigCodeCharSet = (typeof charSetFromOptions === 'string' && charSetFromOptions.length > 0)
                                ? charSetFromOptions
                                : OPTIONS.TRIG_CODE_DEFAULT_CHAR_SET;
    currentTrigCodeFinalistCount = finalistCount || OPTIONS.TRIG_CODE_DEFAULT_FINALIST_COUNT;


    if (!populateTrigCodeParticipants(winnerName, _cachedParticipantList, codeLength, currentTrigCodeCharSet, currentTrigCodeFinalistCount)) {
        console.error("Failed to populate Trig Code participants.");
        checkRevealCompletionTrigCode(winnerName);
        return;
    }

    trigCodeRevealedChars = Array(codeLength).fill(OPTIONS.TRIG_CODE_PLACEHOLDER_CHAR);
    trigCodeWinnerCodeDisplay.innerHTML = trigCodeRevealedChars.map(char => `<span class="placeholder-char">${char}</span>`).join('');

    setTimeout(() => {
        if (trigCodeWinnerCodeDisplay) trigCodeWinnerCodeDisplay.classList.add('visible');
        if (trigCodeParticipantsContainer) trigCodeParticipantsContainer.classList.add('visible');
    }, OPTIONS.TRIG_CODE_APPEAR_DELAY_MS);


    if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.resetRevealState === 'function') {
        NetworkAnimation.resetRevealState();
    }

    trigCodeCurrentRevealIndex = 0;
    trigCodeRevealIntervalId = setTimeout(() => {
        revealNextTrigCodeChar(winnerName);
    }, OPTIONS.TRIG_CODE_WINNER_CODE_REVEAL_START_DELAY_MS + OPTIONS.TRIG_CODE_APPEAR_DELAY_MS);
    animationSequenceTimeoutIds.push(trigCodeRevealIntervalId);
}

function revealNextTrigCodeChar(winnerName) {
    if (trigCodeCurrentRevealIndex >= trigCodeWinnerCode.length) {
        checkRevealCompletionTrigCode(winnerName);
        return;
    }

    let stepDelay = currentTrigCodeRevealStepDuration;
    const activeParticipantsBeforeStep = trigCodeParticipantsData.filter(p => !p.isEliminated && !p.isVisiblyRemoved).length;

    // Check for pause condition *before* revealing the next character IF it's the final character
    if (trigCodeCurrentRevealIndex === trigCodeWinnerCode.length - 1 && activeParticipantsBeforeStep === 2) {
        console.log("Trig Code: Down to final 2. Pausing...");
        stepDelay += OPTIONS.TRIG_CODE_FINAL_TWO_PAUSE_MS;
    }


    // Delay the actual reveal and elimination logic
    trigCodeRevealIntervalId = setTimeout(() => {
        const charToReveal = trigCodeWinnerCode[trigCodeCurrentRevealIndex];
        trigCodeRevealedChars[trigCodeCurrentRevealIndex] = charToReveal;

        let winnerCodeHtml = "";
        for(let i=0; i < trigCodeRevealedChars.length; i++) {
            const char = trigCodeRevealedChars[i];
            const charClass = (char === OPTIONS.TRIG_CODE_PLACEHOLDER_CHAR) ? 'placeholder-char' : 'revealed-char';
            winnerCodeHtml += `<span class="${charClass} ${(i === trigCodeCurrentRevealIndex) ? 'just-revealed' : ''}">${char}</span>`;
        }
        trigCodeWinnerCodeDisplay.innerHTML = winnerCodeHtml;
        setTimeout(() => {
            const justRevSpan = trigCodeWinnerCodeDisplay.querySelector('.just-revealed');
            if(justRevSpan) justRevSpan.classList.remove('just-revealed');
        }, currentTrigCodeRevealStepDuration * 0.8);

        callPythonBackend('jsRequestSound', OPTIONS.SOUND_NOTIFICATION_KEY);
        if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.notifyGenericReveal === 'function' && trigCodeWinnerCodeDisplay) {
            NetworkAnimation.notifyGenericReveal(trigCodeWinnerCodeDisplay);
        }

        const currentRevealedPrefix = trigCodeWinnerCode.substring(0, trigCodeCurrentRevealIndex + 1);

        setTimeout(() => {
            let activeParticipantsAfterUpdate = 0;
             trigCodeParticipantsData.forEach(participant => {
                if (participant.isVisiblyRemoved) return;

                if (!participant.isEliminated) {
                    if (!participant.code.startsWith(currentRevealedPrefix)) {
                        participant.isEliminated = true;

                        const countBeforeThisOneIsRemoved = trigCodeParticipantsData.filter(p => !p.isEliminated && !p.isVisiblyRemoved).length;

                        if (countBeforeThisOneIsRemoved > currentTrigCodeFinalistCount) {
                             if (!participant.isVisiblyRemoved) {
                                participant.element.classList.add('eliminating');
                                setTimeout(() => {
                                    participant.element.style.display = 'none';
                                    participant.isVisiblyRemoved = true;
                                }, OPTIONS.TRIG_CODE_ELIMINATION_ANIM_DURATION_MS);
                            }
                        } else {
                            participant.element.classList.add('eliminated');
                            participant.element.classList.remove('highlight-match');
                        }
                    } else {
                        activeParticipantsAfterUpdate++;
                        let codeHtml = "";
                        for(let k=0; k < participant.code.length; k++) {
                            if (k <= trigCodeCurrentRevealIndex && participant.code[k] === trigCodeWinnerCode[k]) {
                                codeHtml += `<span class="matching-char">${participant.code[k]}</span>`;
                            } else {
                                codeHtml += `<span>${participant.code[k]}</span>`;
                            }
                        }
                        participant.codeElement.innerHTML = codeHtml;
                        if(!participant.element.classList.contains('eliminated')) {
                           participant.element.classList.add('highlight-match');
                           setTimeout(() => {
                               if (participant.name !== winnerName || trigCodeCurrentRevealIndex < trigCodeWinnerCode.length -1) {
                                   participant.element.classList.remove('highlight-match');
                               }
                           }, currentTrigCodeRevealStepDuration * 0.8);
                        }
                    }
                }
            });
             const finalVisibleCount = trigCodeParticipantsData.filter(p => !p.isVisiblyRemoved).length;
            console.log(`Trig Code: Char '${charToReveal}' revealed. Prefix: '${currentRevealedPrefix}'. Remaining visible: ${finalVisibleCount}`);

        }, OPTIONS.TRIG_CODE_ELIMINATION_DELAY_MS);

        trigCodeCurrentRevealIndex++;
        if (trigCodeCurrentRevealIndex < trigCodeWinnerCode.length) {
             trigCodeRevealIntervalId = setTimeout(() => revealNextTrigCodeChar(winnerName), currentTrigCodeRevealStepDuration);
             animationSequenceTimeoutIds.push(trigCodeRevealIntervalId);
        } else {
            trigCodeRevealIntervalId = setTimeout(() => checkRevealCompletionTrigCode(winnerName), Math.max(currentTrigCodeRevealStepDuration, OPTIONS.TRIG_CODE_ELIMINATION_DELAY_MS + OPTIONS.TRIG_CODE_ELIMINATION_ANIM_DURATION_MS + 100));
            animationSequenceTimeoutIds.push(trigCodeRevealIntervalId);
        }
    }, stepDelay);
    animationSequenceTimeoutIds.push(trigCodeRevealIntervalId);
}


function checkRevealCompletionTrigCode(winnerName) {
    console.log("Triglavian Code Reveal Complete.");
    if (trigCodeRevealIntervalId) { clearTimeout(trigCodeRevealIntervalId); trigCodeRevealIntervalId = null; }

    if (trigCodeWinnerNameSpan) trigCodeWinnerNameSpan.textContent = winnerName;
    if (trigCodeWinnerNameDisplay) trigCodeWinnerNameDisplay.classList.add('visible');

    trigCodeParticipantsData.forEach(p => {
        p.element.classList.remove('highlight-match', 'eliminating');
        if (p.name === winnerName) {
            p.isEliminated = false;
            p.isVisiblyRemoved = false;
            p.element.style.display = 'flex';
            p.element.classList.remove('eliminated');
            p.element.classList.add('highlight-match');
            p.codeElement.innerHTML = p.code.split('').map(c => `<span class="matching-char">${c}</span>`).join('');
            if (p.element.scrollIntoView) {
                 p.element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        } else {
            if (!p.isVisiblyRemoved) {
                p.element.classList.add('eliminated');
                p.codeElement.innerHTML = p.code.split('').map(c => `<span>${c}</span>`).join('');
            }
        }
    });

    const revealMode = document.querySelector('.reveal-mode.visible');
    if (revealMode) revealMode.classList.add('slide-up');

    const countdownStartTimeoutId = setTimeout(() => {
        startCountdownPhase();
    }, OPTIONS.COUNTDOWN_START_DELAY_AFTER_TRIG_CODE_MS);
    animationSequenceTimeoutIds.push(countdownStartTimeoutId);

    console.log(`JS checkRevealCompletionTrigCode: Sending original name back: '${currentWinnerNameForCallback}'`);
    callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback);
}

// --- ESI Data Handling ---
function handleESIDataUpdate(esiData) {
    console.log("JS_DEBUG: handleESIDataUpdate received:", esiData);
    if (!esiData) {
        console.warn("JS_DEBUG: handleESIDataUpdate received null or undefined data.");
        return;
    }
    // console.log("JS_DEBUG: RAW DATA:", JSON.stringify(esiData));

    console.log(`JS_DEBUG: Portrait base64 present: ${!!esiData.portrait_base64}, Length: ${esiData.portrait_base64 ? esiData.portrait_base64.length : 0}, Type: ${esiData.portrait_content_type}`);
    console.log(`JS_DEBUG: ESI Data: Name=${esiData.name}, Corp=${esiData.corporation_name}, Alliance=${esiData.alliance_name}`);

    // Determine which animation mode's winner display is currently active
    let activeWinnerDisplayContainer = null;
    let portraitImgElem = null;
    let nameSpanElem = null;
    let corpSpanElem = null;
    let allianceSpanElem = null;

    console.log("JS_DEBUG: Checking active modes for ESI update:");
    if(boxRevealMode) console.log(`JS_DEBUG: boxRevealMode.classList.contains('visible') = ${boxRevealMode.classList.contains('visible')}`);
    if(listRevealMode) console.log(`JS_DEBUG: listRevealMode.classList.contains('visible') = ${listRevealMode.classList.contains('visible')}`);
    if (triglavianRevealMode) console.log(`JS_DEBUG: triglavianRevealMode.classList.contains('visible') = ${triglavianRevealMode.classList.contains('visible')}`);
    if (nodePathRevealMode) console.log(`JS_DEBUG: nodePathRevealMode.classList.contains('visible') = ${nodePathRevealMode.classList.contains('visible')}`);
    if (trigConduitRevealMode) console.log(`JS_DEBUG: trigConduitRevealMode.classList.contains('visible') = ${trigConduitRevealMode.classList.contains('visible')}`);
    if (trigCodeRevealMode) console.log(`JS_DEBUG: trigCodeRevealMode.classList.contains('visible') = ${trigCodeRevealMode.classList.contains('visible')}`);


    if (boxRevealMode && boxRevealMode.classList.contains('visible')) {
        activeWinnerDisplayContainer = boxRevealMode;
        portraitImgElem = document.getElementById('hacking-winner-portrait');
        nameSpanElem = document.getElementById('hacking-winner-name'); // Main name span for this mode
        corpSpanElem = document.getElementById('hacking-winner-corp');
        allianceSpanElem = document.getElementById('hacking-winner-alliance');
        console.log("JS_DEBUG: Targeting Hacking/Box Reveal display elements for ESI.");
    } else if (listRevealMode && listRevealMode.classList.contains('visible')) {
        activeWinnerDisplayContainer = listWinnerDisplay;
        portraitImgElem = document.getElementById('list-winner-portrait');
        nameSpanElem = listWinnerNameSpan; // This is the main name span for this mode
        corpSpanElem = document.getElementById('list-winner-corp');
        allianceSpanElem = document.getElementById('list-winner-alliance');
        console.log("JS_DEBUG: Targeting List Reveal display elements for ESI.");
    } else if (triglavianRevealMode && triglavianRevealMode.classList.contains('visible')) {
        activeWinnerDisplayContainer = triglavianWinnerDisplay;
        portraitImgElem = triglavianWinnerPortraitImg;
        nameSpanElem = triglavianWinnerNameSpan; // Main name span for this mode
        corpSpanElem = triglavianWinnerCorpSpan;
        allianceSpanElem = triglavianWinnerAllianceSpan;
         console.log("JS_DEBUG: Targeting Triglavian display elements for ESI.");
    } else if (nodePathRevealMode && nodePathRevealMode.classList.contains('visible')) {
        activeWinnerDisplayContainer = nodePathWinnerDisplay;
        portraitImgElem = nodePathWinnerPortraitImg;
        nameSpanElem = nodePathWinnerNameSpan; // Main name span for this mode
        corpSpanElem = nodePathWinnerCorpSpan;
        allianceSpanElem = nodePathWinnerAllianceSpan;
        console.log("JS_DEBUG: Targeting Node Path display elements for ESI.");
    } else if (trigConduitRevealMode && trigConduitRevealMode.classList.contains('visible')) {
        activeWinnerDisplayContainer = trigConduitWinnerDisplay;
        portraitImgElem = trigConduitWinnerPortraitImg;
        nameSpanElem = trigConduitWinnerNameSpan; // Main name span for this mode
        corpSpanElem = trigConduitWinnerCorpSpan;
        allianceSpanElem = trigConduitWinnerAllianceSpan;
        console.log("JS_DEBUG: Targeting Trig Conduit display elements for ESI.");
    } else if (trigCodeRevealMode && trigCodeRevealMode.classList.contains('visible')) {
        activeWinnerDisplayContainer = trigCodeWinnerNameDisplay;
        portraitImgElem = trigCodeWinnerPortraitImg;
        nameSpanElem = trigCodeWinnerNameSpan; // Main name span for this mode
        corpSpanElem = trigCodeWinnerCorpSpan;
        allianceSpanElem = trigCodeWinnerAllianceSpan;
        console.log("JS_DEBUG: Targeting Trig Code Reveal display elements for ESI.");
    }


    if (activeWinnerDisplayContainer) {
        // Update name if ESI provided one (typically animation already did, but for consistency)
        if (nameSpanElem && esiData.name && nameSpanElem.textContent.toUpperCase() !== esiData.name.toUpperCase()) {
             // It's generally better to let the core animation logic handle the main winner name text
             // unless this is the *only* place it's set for a particular mode.
             // For now, let's assume other parts of the animation set the main name.
             // nameSpanElem.textContent = (esiData.name || "N/A").toUpperCase();
        }

        if (portraitImgElem) {
            if (esiData.portrait_base64 && esiData.portrait_content_type) {
                portraitImgElem.src = `data:${esiData.portrait_content_type};base64,${esiData.portrait_base64}`;
                portraitImgElem.alt = "";
                portraitImgElem.style.display = 'block';
                console.log("JS_DEBUG: Winner portrait SRC set and displayed.");
            } else {
                portraitImgElem.src = "#";
                portraitImgElem.style.display = 'none';
                console.log("JS_DEBUG: No portrait base64/type, hiding image.");
            }
        } else {
            console.warn("JS_DEBUG: Portrait img element not found in active display for ESI update.");
        }

        if (corpSpanElem) {
            corpSpanElem.textContent = `Corp: ${esiData.corporation_name || "N/A"}`;
            corpSpanElem.style.display = 'block';
        } else {
            console.warn("JS_DEBUG: Corp span element not found in active display.");
        }

        if (allianceSpanElem) {
            if (esiData.alliance_name) {
                allianceSpanElem.textContent = `Alliance: ${esiData.alliance_name}`;
                allianceSpanElem.style.display = 'block';
            } else {
                 allianceSpanElem.textContent = '';
                 allianceSpanElem.style.display = 'none';
            }
        } else {
            console.warn("JS_DEBUG: Alliance span element not found in active display.");
        }

    } else {
        console.warn("JS_DEBUG: No active/targeted winner display found to update with ESI data.");
    }
}
window.handleESIDataUpdate = handleESIDataUpdate;


// --- Countdown Phase Logic ---
// ... (startCountdownPhase, updateCountdown, stopCountdownPhase remain same) ...
function startCountdownPhase() {
    console.log("JS: startCountdownPhase() called");
    console.log("JS: Countdown elements check - container:", !!countdownContainer, "text:", !!countdownText, "progress:", !!countdownProgress);
    if (!countdownContainer || !countdownText || !countdownProgress) {
        console.error("Countdown elements missing!");
        return;
    }
    console.log(`JS: Starting countdown VISUAL phase (${currentCountdownDurationS}s)`);
    console.log("JS: About to add 'visible' class to countdown container");
    isCountdownActive = true;
    countdownStartTime = performance.now();
    countdownContainer.classList.add('visible');
    countdownText.textContent = Math.ceil(currentCountdownDurationS);
    countdownProgress.style.transition = 'none';
    countdownProgress.style.strokeDashoffset = 0;
    void countdownProgress.offsetWidth;
    countdownProgress.style.transition = 'stroke-dashoffset 0.1s linear, stroke 0.5s ease-out';
    countdownProgress.style.stroke = 'var(--countdown-yellow)';
    console.log("JS: Countdown visual setup complete. Container should now be visible.");

    if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.startCountdownEffects === 'function') {
        console.log("JS: Triggering NetworkAnimation countdown effects.");
        NetworkAnimation.startCountdownEffects(currentCountdownDurationS);
    } else {
        console.warn("NetworkAnimation module or startCountdownEffects function missing!");
    }
}
function updateCountdown() { if (!isCountdownActive || !countdownText || !countdownProgress) return; const elapsedTime = performance.now() - countdownStartTime; const currentCountdownValue = Math.max(0, currentCountdownDurationS - elapsedTime / 1000); const displayValue = Math.ceil(currentCountdownValue); if (countdownText.textContent !== String(displayValue)) { countdownText.textContent = displayValue; } const progressFraction = currentCountdownValue / currentCountdownDurationS; const offset = progressRingCircumference * (1 - progressFraction); countdownProgress.style.strokeDashoffset = Math.max(0, offset); if (currentCountdownValue <= 5 && currentCountdownValue > 0) { if (countdownProgress.style.stroke !== 'var(--countdown-red)') { countdownProgress.style.stroke = 'var(--countdown-red)'; } } else if (currentCountdownValue > 5) { if (countdownProgress.style.stroke !== 'var(--countdown-yellow)') { countdownProgress.style.stroke = 'var(--countdown-yellow)'; } } else { if (countdownProgress.style.stroke !== 'var(--countdown-red)') { countdownProgress.style.stroke = 'var(--countdown-red)'; } stopCountdownPhase(true); } }
function stopCountdownPhase(finishedNaturally = false) { if (!isCountdownActive) return; isCountdownActive = false; console.log(`JS: Stopping countdown VISUAL phase. Finished Naturally: ${finishedNaturally}`); if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.stopCountdownEffects === 'function') { NetworkAnimation.stopCountdownEffects(finishedNaturally); } if (countdownContainer) countdownContainer.classList.remove('visible'); if(countdownProgress) { countdownProgress.style.transition = 'none'; countdownProgress.style.strokeDashoffset = 0; void countdownProgress.offsetWidth; countdownProgress.style.transition = 'stroke-dashoffset 0.1s linear, stroke 0.5s ease-out'; } }


// --- Stop / Cleanup ---
function stopAnimationSequence() {
    console.log("JS: Stopping ALL animation sequences...");
    clearAnimationSequenceTimeouts();
    if (listAnimationFrameId) { cancelAnimationFrame(listAnimationFrameId); listAnimationFrameId = null; }
    if(cyclingIntervalId) clearInterval(cyclingIntervalId); cyclingIntervalId = null;
    if(revealTimeoutId) clearTimeout(revealTimeoutId); revealTimeoutId = null;

    if (triglavianCyclingIntervalId) clearInterval(triglavianCyclingIntervalId); triglavianCyclingIntervalId = null;
    if (triglavianRevealTimeoutId) clearTimeout(triglavianRevealTimeoutId); triglavianRevealTimeoutId = null;
    Object.values(trigTempRevealTimeouts).forEach(clearTimeout); trigTempRevealTimeouts = {};
    if (nodePathRevealTimeoutId) clearTimeout(nodePathRevealTimeoutId); nodePathRevealTimeoutId = null;
    if (nodePathActiveNodeTimeoutId) clearTimeout(nodePathActiveNodeTimeoutId); nodePathActiveNodeTimeoutId = null;
    if (trigConduitIntervalId) { clearInterval(trigConduitIntervalId); trigConduitIntervalId = null; }
    Object.values(trigConduitScrambleIntervals).forEach(clearInterval); trigConduitScrambleIntervals = {};
    if (trigCodeRevealIntervalId) { clearInterval(trigCodeRevealIntervalId); trigCodeRevealIntervalId = null; }

    if (prizeRevealContainer) {
        prizeRevealContainer.classList.remove('visible');
        // <<< THIS IS THE KEY CHANGE >>>
        // Removed the setTimeout to prevent a race condition when starting the prize reveal animation.
        // The calling function is now responsible for any desired fade-out transition.
        prizeRevealContainer.style.display = 'none';
    }
    if (animationContent) { 
        animationContent.style.display = 'flex';
    }

    isListScrolling = false;
    stopCountdownPhase(false);
    resetListState();
    resetTriglavianState();
    resetNodePathState();
    resetTrigConduitState();
    resetTrigCodeRevealState();
    boxes.forEach(box => { if (box) { box.classList.remove('box-pulse', 'revealed'); box.textContent = ''; } });
    revealedIndices.clear();
}

// --- Main Animation Trigger ---
// ... (startAnimation remains the same) ...
function startAnimation(winnerName, animationType = 'random', options = {}) {
    console.log(`JS: startAnimation called. Winner: ${winnerName}, Type: '${animationType}', Opts:`, options);
    console.log(`JS: Animation type comparison: animationType='${animationType}', typeof='${typeof animationType}'`);
    console.log(`JS: Checking if '${animationType}' === 'Triglavian Translation': ${animationType === 'Triglavian Translation'}`);
    
    // SEND DEBUG INFO BACK TO PYTHON
    if (pythonBackend && typeof pythonBackend.jsDebugMessage === 'function') {
        try {
            pythonBackend.jsDebugMessage(`JS_DEBUG: startAnimation called with type='${animationType}', winner='${winnerName}'`);
            pythonBackend.jsDebugMessage(`JS_DEBUG: About to start condition checks...`);
        } catch (e) {
            console.error("Failed to send debug to Python:", e);
        }
    }
    
    if (!isWebChannelReady) { console.warn("WebChannel not ready. Retrying..."); setTimeout(() => startAnimation(winnerName, animationType, options), 200); return; }
    if (!document.body || !animationContent) { console.warn("DOM not ready. Retrying..."); setTimeout(() => startAnimation(winnerName, animationType, options), 100); return; }

    currentCountdownDurationS = parseInt(options.countdownDurationS, 10) || parseInt(options.countdownDuration, 10) || 30; // Added fallback for older key
    console.log(`JS: Setting visual countdown duration to ${currentCountdownDurationS}s`);

    // <<< KEY CHANGE: Don't do a full reset if this is a continuation of a prize reveal sequence >>>
    if (!options.isContinuation) {
        if (!initializeDisplay()) { console.error("initializeDisplay failed."); return; };
    } else {
        // For continuation, just ensure countdown elements are properly initialized
        console.log("JS: Continuation mode - ensuring countdown elements are ready");
        countdownContainer = document.getElementById('countdown-container'); 
        countdownProgress = document.getElementById('countdown-progress'); 
        countdownText = document.getElementById('countdown-text');
        
        // Initialize progress ring circumference if not already done
        if (countdownProgress && progressRingCircumference === 0) { 
            const radiusEl = countdownProgress.r?.baseVal; 
            if (radiusEl) { 
                const radius = radiusEl.value; 
                progressRingCircumference = 2 * Math.PI * radius; 
            } else { 
                console.error("Could not get countdown radius."); 
                progressRingCircumference = 283; 
            } 
            countdownProgress.style.strokeDasharray = `${progressRingCircumference} ${progressRingCircumference}`; 
        }
        
        // Ensure countdown container is ready to be shown
        if (countdownContainer) {
            countdownContainer.classList.remove('visible'); // Reset state
        }
        
        if (!countdownContainer || !countdownProgress || !countdownText) {
            console.error("Continuation Error: Countdown elements missing!");
            return;
        }
        
        console.log("JS: Continuation mode - countdown elements verified and ready");
    }
    
    if (animationContent) animationContent.style.display = 'flex';

    currentWinnerNameForCallback = String(winnerName || "Unknown");
    console.log(`JS: Stored original winner name: '${currentWinnerNameForCallback}'`);

    const revealInterval = options.revealInterval ?? OPTIONS.DEFAULT_REVEAL_INTERVAL_MS;

    const listPythonDurationSetting = options.listTotalDurationS ?? options.listDuration ?? 7; // Added fallback for older key
    if (listPythonDurationSetting <= 4) {
        listScrollState.currentFastScrollDurationMs = OPTIONS.LIST_FAST_SCROLL_DURATION_MS_FAST;
    } else if (listPythonDurationSetting >= 11) {
        listScrollState.currentFastScrollDurationMs = OPTIONS.LIST_FAST_SCROLL_DURATION_MS_SLOW;
    } else {
        listScrollState.currentFastScrollDurationMs = OPTIONS.LIST_FAST_SCROLL_DURATION_MS_NORMAL;
    }


    const trigRevealSpeedLabel = options.trigRevealSpeed || 'Slow';
    let trigRevealIntervalMs = OPTIONS.TRIG_REVEAL_INTERVAL_MS_SLOW;

    const nodePathSpeedLabel = options.nodePathSpeed || 'Normal';
    currentNodePathStepDuration = NODE_PATH_SPEED_DURATIONS[nodePathSpeedLabel] || NODE_PATH_SPEED_DURATIONS['Normal'];

    const trigConduitSpeedLabel = options.trigConduitSpeed || 'Normal';
    if (trigConduitSpeedLabel === 'Fast') currentTrigConduitStepDuration = OPTIONS.TRIG_CONDUIT_REVEAL_BASE_INTERVAL_MS_FAST;
    else if (trigConduitSpeedLabel === 'Slow') currentTrigConduitStepDuration = OPTIONS.TRIG_CONDUIT_REVEAL_BASE_INTERVAL_MS_SLOW;
    else currentTrigConduitStepDuration = OPTIONS.TRIG_CONDUIT_REVEAL_BASE_INTERVAL_MS_NORMAL;
    console.log(`JS: Trig Conduit Step Duration set to ${currentTrigConduitStepDuration}ms for speed '${trigConduitSpeedLabel}'`);

    const trigCodeLength = parseInt(options.animation_trig_code_length || options.trigCodeLength, 10) || OPTIONS.TRIG_CODE_DEFAULT_LENGTH; // Support older key
    const trigCodeRevealSpeedLabel = options.animation_trig_code_reveal_speed || options.trigCodeRevealSpeed || 'Normal';
    const trigCodeCharSet = options.animation_trig_code_char_set || options.trigCodeCharSet || OPTIONS.TRIG_CODE_DEFAULT_CHAR_SET;
    const trigCodeFinalistCount = parseInt(options.animation_trig_code_finalist_count || options.trigCodeFinalistCount, 10) || OPTIONS.TRIG_CODE_DEFAULT_FINALIST_COUNT;

    currentRevealInterval = revealInterval;

    const winnerNameToAnimate = String(winnerName || "").trim();
    const finalWinnerName = winnerNameToAnimate || "WINNER";

    bodyElement.classList.remove('show-boxes', 'show-list', 'show-triglavian', 'show-node-path', 'show-trig-conduit', 'show-trig-code');
    let modeElement = null;
    let appearDelay = OPTIONS.SLIDE_UP_DELAY_MS;

    if (typeof NetworkAnimation !== 'undefined' && typeof NetworkAnimation.resetRevealState === 'function') { NetworkAnimation.resetRevealState(); }

    if (animationType === 'Vertical List') {
         console.log(`[LIST SOUND] List animation selected. Ticking sound will be handled by scrollListWithRAF.`);
    } else if (['Hacking', 'Triglavian Translation', 'Node Path Reveal', 'Triglavian Conduit', 'Triglavian Code Reveal'].includes(animationType)) {
        // Python Main.py handles playing "animation_start" for these before calling this JS function.
    }


    if (animationType === 'Vertical List') {
        console.log(`🎯 JS: Taking VERTICAL LIST path`);
        modeElement = listRevealMode; appearDelay = OPTIONS.LIST_APPEAR_DELAY_MS; bodyElement.classList.add('show-list');
         if (!modeElement) { console.error("List mode container missing!"); return; }
         requestAnimationFrame(() => {
             requestAnimationFrame(() => {
                if (!bodyElement.classList.contains('show-list')) return;
                if (!buildList(finalWinnerName, _cachedParticipantList)) {
                    console.error("Failed to build vertical list.");
                    if (listWinnerNameSpan) listWinnerNameSpan.textContent = finalWinnerName;
                    if (listWinnerDisplay) listWinnerDisplay.classList.add('visible');
                    callPythonBackend("jsVisualsComplete", currentWinnerNameForCallback);
                    const cdTimeout = setTimeout(() => startCountdownPhase(), OPTIONS.COUNTDOWN_START_DELAY_AFTER_LIST_MS);
                    animationSequenceTimeoutIds.push(cdTimeout);
                    return;
                }
                const scrollStartTimeout = setTimeout(() => {
                    scrollListWithRAF(finalWinnerName);
                }, appearDelay + OPTIONS.LIST_SCROLL_START_DELAY_MS);
                animationSequenceTimeoutIds.push(scrollStartTimeout);
            });
         });
    }
     else if (animationType === 'Triglavian Translation') {
        console.log("� JS: Taking TRIGLAVIAN TRANSLATION path for PRIZE REVEAL!");
        console.log(`🎯 JS: Triglavian elements check - triglavianRevealMode: ${triglavianRevealMode}, triglavianBoxesRow: ${triglavianBoxesRow}, triglavianBoxes.length: ${triglavianBoxes.length}, OPTIONS.TRIG_BOX_COUNT: ${OPTIONS.TRIG_BOX_COUNT}`);
        
        // Send debug message to Python
        if (pythonBackend && typeof pythonBackend.jsDebugMessage === 'function') {
            try {
                pythonBackend.jsDebugMessage(`JS_DEBUG: Taking TRIGLAVIAN TRANSLATION path!`);
                pythonBackend.jsDebugMessage(`JS_DEBUG: Element check - triglavianRevealMode: ${!!triglavianRevealMode}, triglavianBoxesRow: ${!!triglavianBoxesRow}, triglavianBoxes.length: ${triglavianBoxes ? triglavianBoxes.length : 'undefined'}, expected: ${OPTIONS.TRIG_BOX_COUNT}`);
            } catch (e) {
                console.error("Failed to send Triglavian debug to Python:", e);
            }
        }
        modeElement = triglavianRevealMode; appearDelay = OPTIONS.TRIG_APPEAR_DELAY_MS; bodyElement.classList.add('show-triglavian');
        if (!modeElement || !triglavianBoxesRow || triglavianBoxes.length !== OPTIONS.TRIG_BOX_COUNT ) { 
            console.error("🚨 JS: Triglavian elements missing! Falling back to default."); 
            console.error(`🚨 JS: Missing elements - modeElement: ${modeElement}, triglavianBoxesRow: ${triglavianBoxesRow}, triglavianBoxes.length: ${triglavianBoxes.length}, expected: ${OPTIONS.TRIG_BOX_COUNT}`);
            
            // Send debug message to Python about fallback
            if (pythonBackend && typeof pythonBackend.jsDebugMessage === 'function') {
                try {
                    pythonBackend.jsDebugMessage(`JS_DEBUG: FALLING BACK TO HACKING! Missing - modeElement: ${!!modeElement}, triglavianBoxesRow: ${!!triglavianBoxesRow}, triglavianBoxes.length: ${triglavianBoxes ? triglavianBoxes.length : 'undefined'}`);
                } catch (e) {
                    console.error("Failed to send fallback debug to Python:", e);
                }
            }
            
            // FORCE CREATION OF TRIGLAVIAN BOXES IF THEY'RE MISSING
            if (!triglavianBoxes || triglavianBoxes.length !== OPTIONS.TRIG_BOX_COUNT) {
                console.log("🔧 JS: Attempting to create missing Triglavian boxes...");
                createTriglavianBoxes();
                console.log(`🔧 JS: After createTriglavianBoxes() - triglavianBoxes.length: ${triglavianBoxes.length}`);
                
                // TRY AGAIN AFTER CREATION
                if (triglavianRevealMode && triglavianBoxesRow && triglavianBoxes.length === OPTIONS.TRIG_BOX_COUNT) {
                    console.log("✅ JS: Triglavian elements successfully created, proceeding with Triglavian animation");
                    modeElement = triglavianRevealMode;
                } else {
                    console.error("🚨 JS: Still can't create Triglavian elements, forcing hacking mode");
                    modeElement = boxRevealMode; 
                    appearDelay = OPTIONS.BOXES_APPEAR_DELAY_MS; 
                    bodyElement.classList.remove('show-triglavian'); 
                    bodyElement.classList.add('show-boxes');
                    if (!modeElement || !boxesRow || boxes.length !== OPTIONS.BOX_COUNT ) { 
                        console.error("Hacking mode elements missing too."); 
                        return; 
                    }
                    // START HACKING ANIMATION INSTEAD
                    const boxesAppearTimeout = setTimeout(showBoxes, appearDelay); 
                    animationSequenceTimeoutIds.push(boxesAppearTimeout);
                    const revealStartTimeout = setTimeout(() => { 
                        revealedIndices.clear(); 
                        if (OPTIONS.CYCLE_INTERVAL_MS > 0) { 
                            if (cyclingIntervalId) clearInterval(cyclingIntervalId); 
                            if (bodyElement.classList.contains('show-boxes')) { 
                                cyclingIntervalId = setInterval(cycleChars, OPTIONS.CYCLE_INTERVAL_MS); 
                                cycleChars(); 
                                animationSequenceTimeoutIds.push(cyclingIntervalId); 
                            } 
                        } else { 
                            boxes.forEach((box, index) => { 
                                if (!revealedIndices.has(index)) box.textContent = '-'; 
                            }); 
                        } 
                        let nameLength = finalWinnerName.length; 
                        let displayName = finalWinnerName; 
                        if (nameLength > OPTIONS.BOX_COUNT) { 
                            nameLength = OPTIONS.BOX_COUNT; 
                            displayName = finalWinnerName.substring(0, OPTIONS.BOX_COUNT); 
                            console.warn(`Winner name truncated: '${displayName}' (Original: '${finalWinnerName}')`); 
                        } 
                        const leftPadding = Math.floor((OPTIONS.BOX_COUNT - nameLength) / 2); 
                        let targetIndices = []; 
                        for (let i = 0; i < nameLength; i++) { 
                            targetIndices.push(leftPadding + i); 
                        } 
                        if (revealTimeoutId) clearTimeout(revealTimeoutId); 
                        const firstRevealDelay = Math.min(150, currentRevealInterval / 2); 
                        const firstRevealTimeout = setTimeout(() => { 
                            let unrevealedTargetIndices = [...targetIndices]; 
                            revealRandomLetter(displayName, leftPadding, unrevealedTargetIndices); 
                        }, firstRevealDelay); 
                        animationSequenceTimeoutIds.push(firstRevealTimeout); 
                    }, OPTIONS.REVEAL_START_DELAY_MS); 
                    animationSequenceTimeoutIds.push(revealStartTimeout);
                    return; // Exit after starting hacking animation
                }
            } else {
                console.error("🚨 JS: Other Triglavian elements missing, forcing hacking mode");
                return; // Complete failure, just exit
            }
        }
        console.log("✅ JS: Triglavian elements verified, starting animation");
        const boxesAppearTimeout = setTimeout(showTriglavianBoxes, OPTIONS.TRIG_BOXES_APPEAR_DELAY_MS); animationSequenceTimeoutIds.push(boxesAppearTimeout);
        if (OPTIONS.TRIG_CYCLE_INTERVAL_MS > 0) { if (triglavianCyclingIntervalId) clearInterval(triglavianCyclingIntervalId); const cycleStartTimeout = setTimeout(() => { if (bodyElement.classList.contains('show-triglavian')) { triglavianCyclingIntervalId = setInterval(cycleTriglavianChars, OPTIONS.TRIG_CYCLE_INTERVAL_MS); cycleTriglavianChars(); animationSequenceTimeoutIds.push(triglavianCyclingIntervalId); } }, OPTIONS.TRIG_BOXES_APPEAR_DELAY_MS + 50); animationSequenceTimeoutIds.push(cycleStartTimeout); } else { triglavianBoxes.forEach(box => box.textContent = '-'); }
        startTriglavianReveal(finalWinnerName, trigRevealIntervalMs);
    } else if (animationType === 'Node Path Reveal') {
        modeElement = nodePathRevealMode; appearDelay = OPTIONS.NODE_PATH_APPEAR_DELAY_MS; bodyElement.classList.add('show-node-path');
        if (!modeElement) { console.error("Node Path container missing!"); return; }
        const startRevealTimeout = setTimeout(() => { startNodePathReveal(finalWinnerName); }, appearDelay);
        animationSequenceTimeoutIds.push(startRevealTimeout);
    } else if (animationType === 'Triglavian Conduit') {
        modeElement = trigConduitRevealMode;
        appearDelay = OPTIONS.TRIG_CONDUIT_APPEAR_DELAY_MS;
        bodyElement.classList.add('show-trig-conduit');
        if (!modeElement) { console.error("Triglavian Conduit mode container missing!"); return; }
        const startConduitTimeout = setTimeout(() => {
            startTriglavianConduitAnimation(finalWinnerName, currentTrigConduitStepDuration);
        }, appearDelay);
        animationSequenceTimeoutIds.push(startConduitTimeout);
    } else if (animationType === 'Triglavian Code Reveal') {
        modeElement = trigCodeRevealMode;
        appearDelay = OPTIONS.TRIG_CODE_APPEAR_DELAY_MS;
        bodyElement.classList.add('show-trig-code');
        if (!modeElement) { console.error("Triglavian Code Reveal mode container missing!"); return; }
        const startCodeRevealTimeout = setTimeout(() => {
            startTrigCodeReveal(finalWinnerName, trigCodeLength, trigCodeRevealSpeedLabel, trigCodeCharSet, trigCodeFinalistCount);
        }, appearDelay);
        animationSequenceTimeoutIds.push(startCodeRevealTimeout);
    }
    else { // Default to Hacking
        console.log("🚨 JS: Taking DEFAULT HACKING path! AnimationType was:", animationType);
        console.log("🚨 JS: This means none of the animation type conditions matched!");
        if (pythonBackend && typeof pythonBackend.jsDebugMessage === 'function') {
            try {
                pythonBackend.jsDebugMessage(`JS_DEBUG: ❌ TAKING HACKING PATH! animationType='${animationType}' did not match any conditions`);
            } catch (e) {
                console.error("Failed to send debug to Python:", e);
            }
        }
        modeElement = boxRevealMode; appearDelay = OPTIONS.BOXES_APPEAR_DELAY_MS; bodyElement.classList.add('show-boxes');
        if (!modeElement || !boxesRow || boxes.length !== OPTIONS.BOX_COUNT ) { console.error("Hacking mode elements missing."); return; }
        const boxesAppearTimeout = setTimeout(showBoxes, appearDelay); animationSequenceTimeoutIds.push(boxesAppearTimeout);
        const revealStartTimeout = setTimeout(() => { revealedIndices.clear(); if (OPTIONS.CYCLE_INTERVAL_MS > 0) { if (cyclingIntervalId) clearInterval(cyclingIntervalId); if (bodyElement.classList.contains('show-boxes')) { cyclingIntervalId = setInterval(cycleChars, OPTIONS.CYCLE_INTERVAL_MS); cycleChars(); animationSequenceTimeoutIds.push(cyclingIntervalId); } } else { boxes.forEach((box, index) => { if (!revealedIndices.has(index)) box.textContent = '-'; }); } let nameLength = finalWinnerName.length; let displayName = finalWinnerName; if (nameLength > OPTIONS.BOX_COUNT) { nameLength = OPTIONS.BOX_COUNT; displayName = finalWinnerName.substring(0, OPTIONS.BOX_COUNT); console.warn(`Winner name truncated: '${displayName}' (Original: '${finalWinnerName}')`); } const leftPadding = Math.floor((OPTIONS.BOX_COUNT - nameLength) / 2); let targetIndices = []; for (let i = 0; i < nameLength; i++) { targetIndices.push(leftPadding + i); } if (revealTimeoutId) clearTimeout(revealTimeoutId); const firstRevealDelay = Math.min(150, currentRevealInterval / 2); const firstRevealTimeout = setTimeout(() => { let unrevealedTargetIndices = [...targetIndices]; revealRandomLetter(displayName, leftPadding, unrevealedTargetIndices); }, firstRevealDelay); animationSequenceTimeoutIds.push(firstRevealTimeout); }, OPTIONS.REVEAL_START_DELAY_MS); animationSequenceTimeoutIds.push(revealStartTimeout);
    }

    if (modeElement) {
        modeElement.style.display = 'flex';
        const modeVisibleTimeout = setTimeout(() => { if (modeElement) modeElement.classList.add('visible'); }, 50);
        animationSequenceTimeoutIds.push(modeVisibleTimeout);
    }
}

// <<< NEW/REWRITTEN: Prize Reveal with 2 lines >>>
function startPrizeRevealAnimation(prizeName, donatorName, options = {}) {
    console.log(`JS: Starting PRIZE reveal for: ${prizeName}`);
    if (!prizeRevealContainer || !prizeRevealDisplay || !prizeRevealName || !prizeRevealDonator) {
        console.error("Prize reveal elements are missing!");
        callPythonBackend('jsPrizeRevealComplete', prizeName || "", donatorName || "");
        return;
    }
    stopAnimationSequence(); // Clean up previous animations first
    
    // Hide the main animation area to prevent overlap
    if (animationContent) animationContent.style.display = 'none';

    prizeRevealName.textContent = (prizeName || "UNKNOWN PRIZE").toUpperCase();
    if (donatorName && donatorName !== "<NO DONATOR SET>") {
        prizeRevealDonator.textContent = `(DONATED BY: ${donatorName.toUpperCase()})`;
        prizeRevealDonator.style.display = 'block';
    } else {
        prizeRevealDonator.textContent = '';
        prizeRevealDonator.style.display = 'none';
    }

    prizeRevealDisplay.classList.remove('revealed');
    prizeRevealContainer.style.display = 'flex';
    
    // Use requestAnimationFrame to ensure display is set before transition starts
    requestAnimationFrame(() => {
        prizeRevealContainer.classList.add('visible');
    });

    const translationDelay = 2500;
    const holdDelay = 2000;
    const fadeoutDelay = 400;

    // 1. After a delay, "translate" the text to normal font
    const translateTimeout = setTimeout(() => {
        callPythonBackend('jsRequestSound', OPTIONS.SOUND_NOTIFICATION_KEY);
        prizeRevealDisplay.classList.add('revealed');
    }, translationDelay);
    animationSequenceTimeoutIds.push(translateTimeout);

    // 2. After another delay, start fading out
    const hideTimeout = setTimeout(() => {
        prizeRevealContainer.classList.remove('visible');
    }, translationDelay + holdDelay);
    animationSequenceTimeoutIds.push(hideTimeout);

    // 3. After the fade out is complete, hide the element and call back to Python
    const finalTimeout = setTimeout(() => {
        prizeRevealContainer.style.display = 'none';
        callPythonBackend('jsPrizeRevealComplete', prizeName || "", donatorName || "");
    }, translationDelay + holdDelay + fadeoutDelay);
    animationSequenceTimeoutIds.push(finalTimeout);
}


// --- Initial Setup & Cleanup ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM Loaded. Initializing...");
    initializeWebChannel();
    isBackgroundListsReady = false;
    if (typeof BackgroundLists !== 'undefined' && typeof BackgroundLists.init === 'function') {
        isBackgroundListsReady = BackgroundLists.init();
    } else { console.error("BackgroundLists module not found or init function missing!"); }
    if (!isBackgroundListsReady) { console.error("BackgroundLists initialization FAILED (DOM load)."); }
    else { console.log("BackgroundLists initialized successfully (DOM load)."); BackgroundLists.clear(); }
    initializeDisplay();
});

window.addEventListener('beforeunload', () => {
    stopAnimationSequence();
});

// --- Expose functions ---
window.startAnimation = startAnimation;
window.startPrizeRevealAnimation = startPrizeRevealAnimation;
window.cancelAnimationAndCountdown = stopAnimationSequence;
// window.updateParticipantsJS is already exposed
// window.handleESIDataUpdate is already exposed

// END script.js
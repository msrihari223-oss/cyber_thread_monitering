/**
 * ==========================================================================
 * CYBER SENTINEL AI AGENT - REAL-TIME DEVICE DETECTION & VOICE REACTION
 * ==========================================================================
 * Omnipresent Cyber Security AI Agent that:
 * 1. Analyzes and detects client hardware, OS, browser, display, and network.
 * 2. Provides interactive voice speech synthesis and cyber sound alarms.
 * 3. Actively reacts with voice warnings ("There is a risk!") when toxic/bad
 *    comments or posts are detected.
 * 4. Displays real-time device telemetry and threat intervention logs.
 */

class CyberSecurityAgent {
    constructor() {
        this.version = "2.4.0";
        this.agentName = "Sentinel-AI Guardian";
        this.state = "idle"; // idle, scanning, risk_alert
        this.voiceEnabled = true;
        this.soundFxEnabled = true;
        this.speechRate = 1.0;
        this.speechPitch = 1.0;
        this.deviceInfo = this.detectDevice();
        this.threatLogs = [];
        this.isModalOpen = false;
        this.synth = window.speechSynthesis;
        this.audioCtx = null;
        this.speechTimeout = null;

        // Initialize HUD and event listeners
        this.initDOM();
        this.initVoiceEngine();
        this.bindEvents();

        // Broadcast agent ready
        console.log(`[CyberAgent] 🛡️ ${this.agentName} v${this.version} initialized on ${this.deviceInfo.deviceTitle}`);
    }

    /**
     * ── 1. COMPREHENSIVE CLIENT DEVICE DETECTION ──
     */
    detectDevice() {
        const ua = navigator.userAgent || "";
        const platform = navigator.platform || "";
        const vendor = navigator.vendor || "";

        // 1. Detect Operating System & Architecture
        let os = "Unknown OS";
        let osVersion = "";
        let arch = "64-bit";

        if (/Windows NT 10.0/i.test(ua)) {
            os = "Windows";
            osVersion = "10 / 11";
        } else if (/Windows NT 6.3/i.test(ua)) {
            os = "Windows";
            osVersion = "8.1";
        } else if (/Windows NT 6.1/i.test(ua)) {
            os = "Windows";
            osVersion = "7";
        } else if (/Android/i.test(ua)) {
            os = "Android";
            const match = ua.match(/Android\s([0-9\.]+)/i);
            osVersion = match ? match[1] : "";
        } else if (/iPhone|iPad|iPod/i.test(ua)) {
            os = "iOS";
            const match = ua.match(/OS\s([\d_]+)/i);
            osVersion = match ? match[1].replace(/_/g, '.') : "";
        } else if (/Macintosh|Mac OS X/i.test(ua)) {
            os = "macOS";
            const match = ua.match(/Mac OS X\s([\d_]+)/i);
            osVersion = match ? match[1].replace(/_/g, '.') : "";
        } else if (/Linux/i.test(ua)) {
            os = "Linux";
            osVersion = /Ubuntu/i.test(ua) ? "Ubuntu" : "Standard";
        } else if (/CrOS/i.test(ua)) {
            os = "ChromeOS";
        }

        if (/WOW64|Win64|x86_64|x86-64|x64;/i.test(ua)) {
            arch = "64-bit";
        } else if (/i686|i386|Win32|x86/i.test(ua)) {
            arch = "32-bit";
        } else if (/ARM|aarch64/i.test(ua)) {
            arch = "ARM64";
        }

        // 2. Detect Browser Engine & Version
        let browser = "Unknown Browser";
        let browserVersion = "";

        if (/Edg\/([0-9\.]+)/i.test(ua)) {
            browser = "Microsoft Edge";
            browserVersion = ua.match(/Edg\/([0-9\.]+)/i)[1];
        } else if (/OPR\/([0-9\.]+)/i.test(ua) || /Opera/i.test(ua)) {
            browser = "Opera";
            const m = ua.match(/OPR\/([0-9\.]+)/i);
            browserVersion = m ? m[1] : "";
        } else if (/Chrome\/([0-9\.]+)/i.test(ua) && !/Chromium/i.test(ua)) {
            browser = "Google Chrome";
            browserVersion = ua.match(/Chrome\/([0-9\.]+)/i)[1];
        } else if (/Firefox\/([0-9\.]+)/i.test(ua)) {
            browser = "Mozilla Firefox";
            browserVersion = ua.match(/Firefox\/([0-9\.]+)/i)[1];
        } else if (/Safari\/([0-9\.]+)/i.test(ua) && !/Chrome/i.test(ua)) {
            browser = "Apple Safari";
            const m = ua.match(/Version\/([0-9\.]+)/i);
            browserVersion = m ? m[1] : "";
        }

        // 3. Detect Device Type
        let deviceType = "Desktop / Laptop";
        let isMobile = false;
        let isTablet = false;

        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            deviceType = "Tablet";
            isTablet = true;
        } else if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/i.test(ua)) {
            deviceType = "Smartphone / Mobile";
            isMobile = true;
        }

        // 4. Screen & Viewport Metrics
        const screenWidth = window.screen ? window.screen.width : window.innerWidth;
        const screenHeight = window.screen ? window.screen.height : window.innerHeight;
        const dpr = window.devicePixelRatio || 1;
        const colorDepth = window.screen ? window.screen.colorDepth || 24 : 24;
        const orientation = (window.screen && window.screen.orientation) ? window.screen.orientation.type : (screenWidth > screenHeight ? 'landscape' : 'portrait');

        // 5. Hardware Capabilities
        const cpuCores = navigator.hardwareConcurrency || 4;
        const deviceMemory = navigator.deviceMemory ? `${navigator.deviceMemory} GB` : "4+ GB";
        const touchSupport = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);

        // 6. Network & Connection
        const isOnline = navigator.onLine !== undefined ? navigator.onLine : true;
        let networkType = "Broadband / WiFi";
        let downlink = "High Speed";
        let rtt = "Low Latency";

        if (navigator.connection) {
            networkType = (navigator.connection.effectiveType || navigator.connection.type || "WiFi").toUpperCase();
            if (navigator.connection.downlink) downlink = `${navigator.connection.downlink} Mbps`;
            if (navigator.connection.rtt) rtt = `${navigator.connection.rtt} ms`;
        }

        // 7. Timezone & Locale
        let timezone = "UTC";
        try {
            timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
        } catch (e) {}
        const language = navigator.language || "en-US";

        // 8. Device Title
        let deviceTitle = `${os} ${deviceType.includes("Mobile") ? "Mobile" : "PC"}`;
        if (browser !== "Unknown Browser") {
            const shortBrowser = browser.replace("Google ", "").replace("Mozilla ", "").replace("Apple ", "").replace("Microsoft ", "");
            deviceTitle = `${os} (${shortBrowser})`;
        }

        // 9. Hardware Fingerprint hash
        const rawFP = `${os}-${arch}-${browser}-${screenWidth}x${screenHeight}-${cpuCores}-${timezone}-${language}`;
        const fingerprint = "SEC-" + Math.abs(this.hashString(rawFP)).toString(16).toUpperCase().padStart(8, '0');

        return {
            deviceTitle,
            os: `${os} ${osVersion}`.trim(),
            arch,
            browser: `${browser} ${browserVersion.split('.')[0]}`.trim(),
            browserFull: `${browser} ${browserVersion}`.trim(),
            deviceType,
            isMobile,
            isTablet,
            resolution: `${screenWidth}x${screenHeight} (@${dpr}x)`,
            colorDepth: `${colorDepth}-bit`,
            orientation,
            cpuCores: `${cpuCores} Cores`,
            deviceMemory,
            touchSupport: touchSupport ? "Yes" : "No",
            networkType,
            downlink,
            rtt,
            isOnline,
            timezone,
            language,
            fingerprint,
            userAgent: ua
        };
    }

    hashString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash |= 0;
        }
        return hash;
    }

    /**
     * ── 2. WEB AUDIO SOUND EFFECTS GENERATOR ──
     */
    getAudioContext() {
        if (!this.audioCtx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.audioCtx = new AudioContext();
            }
        }
        if (this.audioCtx && this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }
        return this.audioCtx;
    }

    playCyberSound(type = "alarm") {
        if (!this.soundFxEnabled) return;
        try {
            const ctx = this.getAudioContext();
            if (!ctx) return;

            const now = ctx.currentTime;

            if (type === "alarm") {
                // High-urgency dual-tone cyber threat siren
                const osc1 = ctx.createOscillator();
                const osc2 = ctx.createOscillator();
                const gain = ctx.createGain();

                osc1.type = "sawtooth";
                osc2.type = "sine";

                // Frequency sweep for critical alarm
                osc1.frequency.setValueAtTime(880, now);
                osc1.frequency.exponentialRampToValueAtTime(440, now + 0.18);
                osc1.frequency.exponentialRampToValueAtTime(920, now + 0.35);
                osc1.frequency.exponentialRampToValueAtTime(440, now + 0.55);

                osc2.frequency.setValueAtTime(440, now);
                osc2.frequency.linearRampToValueAtTime(220, now + 0.55);

                gain.gain.setValueAtTime(0.3, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.6);

                osc1.connect(gain);
                osc2.connect(gain);
                gain.connect(ctx.destination);

                osc1.start(now);
                osc2.start(now);
                osc1.stop(now + 0.6);
                osc2.stop(now + 0.6);

            } else if (type === "scan") {
                // Cyber blip
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(600, now);
                osc.frequency.exponentialRampToValueAtTime(1200, now + 0.12);
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.15);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 0.15);

            } else if (type === "shield") {
                // Futuristic shield power-on tone
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "triangle";
                osc.frequency.setValueAtTime(320, now);
                osc.frequency.exponentialRampToValueAtTime(880, now + 0.28);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.35);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 0.35);
            }
        } catch (e) {
            console.warn("[CyberAgent] AudioContext sound failed:", e);
        }
    }

    /**
     * ── 3. VOICE SPEECH SYNTHESIS ENGINE ──
     */
    initVoiceEngine() {
        if (!('speechSynthesis' in window)) {
            console.warn("[CyberAgent] Web Speech Synthesis not supported in this browser environment.");
            return;
        }

        // Preload voices
        window.speechSynthesis.onvoiceschanged = () => {
            this.getBestVoice();
            this.populateVoiceList();
        };
    }

    getBestVoice() {
        if (!this.synth) return null;
        const voices = this.synth.getVoices();
        if (!voices || voices.length === 0) return null;

        // Preferred cyber/english voices
        const preferred = [
            "Google UK English Male",
            "Google UK English Female",
            "Google US English",
            "Microsoft David",
            "Microsoft Mark",
            "Microsoft Zira",
            "Samantha",
            "Daniel",
            "Alex"
        ];

        for (const name of preferred) {
            const found = voices.find(v => v.name.includes(name) && v.lang.startsWith("en"));
            if (found) return found;
        }

        // Fallback to any English voice
        return voices.find(v => v.lang.startsWith("en")) || voices[0];
    }

    speak(text, options = {}) {
        if (!this.voiceEnabled || !('speechSynthesis' in window)) {
            this.showSpeechBubble(text, options.isRisk);
            return;
        }

        try {
            // Cancel current speech if any
            this.synth.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            const voice = options.voice || this.getBestVoice();
            if (voice) utterance.voice = voice;

            utterance.rate = options.rate || this.speechRate;
            utterance.pitch = options.pitch || (options.isRisk ? 1.15 : this.speechPitch);
            utterance.volume = options.volume || 1.0;

            utterance.onstart = () => {
                this.showSpeechBubble(text, options.isRisk);
            };

            utterance.onend = () => {
                this.hideSpeechBubble(4000);
            };

            utterance.onerror = (e) => {
                console.warn("[CyberAgent] Speech error:", e);
                this.hideSpeechBubble(3000);
            };

            this.synth.speak(utterance);
        } catch (e) {
            console.warn("[CyberAgent] Failed to synthesize speech:", e);
            this.showSpeechBubble(text, options.isRisk);
        }
    }

    /**
     * ── 4. THREAT INTERCEPTION & VOICE REACTION ──
     * Triggered when bad/toxic comments or posts are submitted.
     */
    reactToThreat(details = {}) {
        const {
            score = 0.95,
            level = "CRITICAL",
            comment = "",
            warningsCount = 1,
            isBlocked = false,
            action = "Policy Violation Warning"
        } = details;

        // 1. Update State to Critical Risk Alert
        this.setAgentState("risk_alert");

        // 2. Play urgent cyber siren sound
        this.playCyberSound("alarm");

        // 3. Construct specific spoken voice warning with detected device context
        const deviceName = this.deviceInfo.deviceTitle;
        let voiceMessage = "";

        if (isBlocked || warningsCount >= 3) {
            voiceMessage = `Critical Risk Alert! Hazardous behavior detected from your ${deviceName}. Maximum violation limit reached. Account has been permanently locked down by the Cyber Threat Monitoring Agent.`;
        } else if (warningsCount === 2) {
            voiceMessage = `Warning! There is a high risk! Severe policy violation detected originating from your ${deviceName}. Second warning issued. One more violation will trigger an immediate permanent ban.`;
        } else {
            voiceMessage = `Warning! There is a risk! Toxic content detected originating from your ${deviceName}. Threat analysis identified policy violations. Warning ${warningsCount} of 3 recorded against this client device.`;
        }

        // 4. Speak aloud immediately
        this.speak(voiceMessage, { isRisk: true, pitch: 1.1 });

        // 5. Log the threat intervention
        const logEntry = {
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            device: deviceName,
            comment: comment.length > 50 ? comment.substring(0, 50) + "..." : comment,
            score: (score * 100).toFixed(1) + "%",
            level: level,
            warningsCount: warningsCount,
            isBlocked: isBlocked
        };
        this.threatLogs.unshift(logEntry);
        this.updateThreatLogsUI();

        // 6. Reset visual alert back to shield active after 10 seconds
        setTimeout(() => {
            if (this.state === "risk_alert") {
                this.setAgentState("idle");
            }
        }, 10000);

        return {
            device: this.deviceInfo,
            voiceMessage,
            logEntry
        };
    }

    /**
     * ── 5. ANNOUNCE DETECTED DEVICE SPECS ──
     */
    announceDevice() {
        this.playCyberSound("scan");
        const info = this.deviceInfo;
        const msg = `Cyber Threat Sentinel Agent initialized. Client device identified as ${info.deviceType}, running ${info.os} ${info.arch} with ${info.browser}. Display resolution is ${info.resolution}. Hardware contains ${info.cpuCores}. Real-time cyber shield is fully active.`;
        this.speak(msg, { isRisk: false });
    }

    /**
     * ── 6. HUD UI CONTROLLER & DOM INJECTION ──
     */
    initDOM() {
        // Create Host Container
        const container = document.createElement("div");
        container.id = "cyberAgentHost";
        container.innerHTML = `
            <!-- Floating Agent Orb Trigger -->
            <div class="cyber-agent-orb" id="cyberAgentOrb" title="Cyber Sentinel AI Agent (Click to open HUD)">
                <div class="cyber-agent-pill" id="cyberAgentPill">
                    <div class="cyber-agent-pill-header">
                        <span class="cyber-agent-pill-indicator"></span>
                        <span id="cyberAgentPillState">Shield Active</span>
                    </div>
                    <div class="cyber-agent-pill-device" id="cyberAgentPillDevice">${this.deviceInfo.deviceTitle}</div>
                </div>
                <div class="cyber-agent-avatar" id="cyberAgentAvatar">
                    <div class="cyber-agent-avatar-icon">🛡️</div>
                </div>
            </div>

            <!-- Interactive Speech Transcript Bubble -->
            <div class="cyber-agent-speech-bubble" id="cyberAgentBubble">
                <div class="cyber-agent-speech-title">
                    <span id="cyberAgentBubbleHeader">🛡️ Sentinel-AI Reaction</span>
                    <span style="font-size: 10px; opacity: 0.8;">LIVE</span>
                </div>
                <div class="cyber-agent-speech-text" id="cyberAgentBubbleText">
                    Cyber Sentinel monitoring shield is standing by.
                </div>
                <div class="cyber-agent-speech-waveform">
                    <span></span><span></span><span></span><span></span><span></span>
                </div>
            </div>

            <!-- Full Agent Cyber Console Modal -->
            <div class="cyber-agent-modal" id="cyberAgentModal">
                <div class="cyber-agent-modal-header">
                    <div class="cyber-agent-header-left">
                        <div class="cyber-agent-header-icon">🛡️</div>
                        <div>
                            <div class="cyber-agent-header-title">
                                Cyber Sentinel AI
                                <span class="cyber-agent-header-badge" id="cyberAgentBadge">SHIELD ACTIVE</span>
                            </div>
                            <div style="font-size: 11px; color: var(--agent-muted); font-weight: 500;">
                                Device Protection & Threat Interceptor
                            </div>
                        </div>
                    </div>
                    <button class="cyber-agent-close-btn" id="cyberAgentCloseBtn" title="Close">✕</button>
                </div>

                <!-- Navigation Tabs inside Agent -->
                <div class="cyber-agent-tabs">
                    <button class="cyber-agent-tab-btn active" data-tab="telemetry">💻 Device Specs</button>
                    <button class="cyber-agent-tab-btn" data-tab="voice">🎙️ Voice & Audio</button>
                    <button class="cyber-agent-tab-btn" data-tab="threats">🚨 Threat Logs (<span id="cyberThreatCount">0</span>)</button>
                </div>

                <div class="cyber-agent-body">
                    <!-- Tab 1: Device Telemetry -->
                    <div class="cyber-agent-tab-panel active" id="panel-telemetry">
                        <div class="cyber-telemetry-card">
                            <div class="cyber-telemetry-title">
                                <span>📱 Client Device Identification</span>
                                <span style="color: var(--agent-success); font-size: 10px;">VERIFIED</span>
                            </div>
                            <div class="cyber-telemetry-grid">
                                <div class="cyber-telemetry-item">
                                    <div class="cyber-telemetry-label">Device Type</div>
                                    <div class="cyber-telemetry-val">${this.deviceInfo.deviceType}</div>
                                </div>
                                <div class="cyber-telemetry-item">
                                    <div class="cyber-telemetry-label">Operating System</div>
                                    <div class="cyber-telemetry-val">${this.deviceInfo.os} (${this.deviceInfo.arch})</div>
                                </div>
                                <div class="cyber-telemetry-item">
                                    <div class="cyber-telemetry-label">Browser Engine</div>
                                    <div class="cyber-telemetry-val">${this.deviceInfo.browser}</div>
                                </div>
                                <div class="cyber-telemetry-item">
                                    <div class="cyber-telemetry-label">Display Resolution</div>
                                    <div class="cyber-telemetry-val">${this.deviceInfo.resolution}</div>
                                </div>
                                <div class="cyber-telemetry-item">
                                    <div class="cyber-telemetry-label">CPU Cores</div>
                                    <div class="cyber-telemetry-val">${this.deviceInfo.cpuCores}</div>
                                </div>
                                <div class="cyber-telemetry-item">
                                    <div class="cyber-telemetry-label">Network Protocol</div>
                                    <div class="cyber-telemetry-val">${this.deviceInfo.networkType} (${this.deviceInfo.downlink})</div>
                                </div>
                            </div>
                            <div style="font-size: 10.5px; color: var(--agent-muted); display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px;">
                                <span>Security Token: <strong style="color: var(--agent-primary);">${this.deviceInfo.fingerprint}</strong></span>
                                <span>Locale: <strong>${this.deviceInfo.timezone}</strong></span>
                            </div>
                        </div>

                        <div class="cyber-agent-btn-row">
                            <button class="cyber-agent-btn cyber-agent-btn-primary" id="btnAnnounceDevice">
                                📢 Speak Device Info
                            </button>
                            <button class="cyber-agent-btn cyber-agent-btn-danger" id="btnTestThreatAlarm">
                                🚨 Test Threat Alarm
                            </button>
                        </div>
                    </div>

                    <!-- Tab 2: Voice & Audio Settings -->
                    <div class="cyber-agent-tab-panel" id="panel-voice">
                        <div class="cyber-telemetry-card">
                            <div class="cyber-telemetry-title">
                                <span>🎙️ Agent Speech Synthesizer</span>
                            </div>

                            <div class="cyber-voice-setting-row">
                                <span class="cyber-voice-setting-label">Voice Speech Output</span>
                                <label class="cyber-toggle-switch">
                                    <input type="checkbox" id="agentVoiceToggle" checked>
                                    <span class="cyber-toggle-slider"></span>
                                </label>
                            </div>

                            <div class="cyber-voice-setting-row">
                                <span class="cyber-voice-setting-label">Cyber Sound FX (Siren/Blips)</span>
                                <label class="cyber-toggle-switch">
                                    <input type="checkbox" id="agentSoundFxToggle" checked>
                                    <span class="cyber-toggle-slider"></span>
                                </label>
                            </div>

                            <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 8px;">
                                <label class="cyber-voice-setting-label">Agent Voice Persona</label>
                                <select id="agentVoiceSelect" style="width:100%; padding:8px 10px; background:rgba(15,23,42,0.8); border:1px solid var(--agent-border); color:var(--agent-text); border-radius:8px; font-size:12px; outline:none;">
                                    <option>Default Cyber Security Voice</option>
                                </select>
                            </div>
                        </div>

                        <div class="cyber-agent-btn-row">
                            <button class="cyber-agent-btn cyber-agent-btn-secondary" id="btnTestVoiceSpeech">
                                🔊 Test Voice Synthesizer
                            </button>
                        </div>
                    </div>

                    <!-- Tab 3: Threat Logs -->
                    <div class="cyber-agent-tab-panel" id="panel-threats">
                        <div class="cyber-telemetry-title" style="margin-bottom: 6px;">
                            <span>🚨 Intercepted Policy Violations</span>
                            <span style="font-size: 10px; color: var(--agent-muted);">Live Audit Trail</span>
                        </div>
                        <div class="cyber-threat-logs" id="cyberThreatLogsList">
                            <div style="text-align: center; color: var(--agent-muted); font-size: 12px; padding: 24px 0;">
                                ✅ No threat violations detected from this device.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(container);
    }

    bindEvents() {
        const orb = document.getElementById("cyberAgentOrb");
        const modal = document.getElementById("cyberAgentModal");
        const closeBtn = document.getElementById("cyberAgentCloseBtn");
        const btnAnnounce = document.getElementById("btnAnnounceDevice");
        const btnTestAlarm = document.getElementById("btnTestThreatAlarm");
        const btnTestVoice = document.getElementById("btnTestVoiceSpeech");
        const voiceToggle = document.getElementById("agentVoiceToggle");
        const soundFxToggle = document.getElementById("agentSoundFxToggle");
        const tabBtns = document.querySelectorAll(".cyber-agent-tab-btn");

        // Toggle Console Modal
        if (orb) {
            orb.addEventListener("click", () => {
                this.toggleModal();
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                this.closeModal();
            });
        }

        // Tab Switching
        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTab = btn.getAttribute("data-tab");
                tabBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");

                document.querySelectorAll(".cyber-agent-tab-panel").forEach(p => {
                    p.classList.remove("active");
                });
                const panel = document.getElementById(`panel-${targetTab}`);
                if (panel) panel.classList.add("active");
            });
        });

        // Announce Device Button
        if (btnAnnounce) {
            btnAnnounce.addEventListener("click", () => {
                this.announceDevice();
            });
        }

        // Test Threat Alarm Button
        if (btnTestAlarm) {
            btnTestAlarm.addEventListener("click", () => {
                this.reactToThreat({
                    score: 0.95,
                    level: "CRITICAL",
                    comment: "Sample violation test keyword: 'hack scam abusive threat'",
                    warningsCount: 1,
                    isBlocked: false
                });
            });
        }

        // Test Voice Button
        if (btnTestVoice) {
            btnTestVoice.addEventListener("click", () => {
                this.playCyberSound("shield");
                this.speak(`Cyber Sentinel Voice Synthesizer is operational. Connected to ${this.deviceInfo.deviceTitle}.`);
            });
        }

        // Voice and Sound toggles
        if (voiceToggle) {
            voiceToggle.addEventListener("change", (e) => {
                this.voiceEnabled = e.target.checked;
            });
        }
        if (soundFxToggle) {
            soundFxToggle.addEventListener("change", (e) => {
                this.soundFxEnabled = e.target.checked;
            });
        }
    }

    toggleModal() {
        this.isModalOpen = !this.isModalOpen;
        const modal = document.getElementById("cyberAgentModal");
        if (modal) {
            if (this.isModalOpen) {
                modal.classList.add("open");
                this.playCyberSound("scan");
                this.populateVoiceList();
            } else {
                modal.classList.remove("open");
            }
        }
    }

    closeModal() {
        this.isModalOpen = false;
        const modal = document.getElementById("cyberAgentModal");
        if (modal) modal.classList.remove("open");
    }

    setAgentState(state = "idle") {
        this.state = state;
        const orb = document.getElementById("cyberAgentOrb");
        const modal = document.getElementById("cyberAgentModal");
        const badge = document.getElementById("cyberAgentBadge");
        const statePill = document.getElementById("cyberAgentPillState");

        if (!orb) return;

        orb.classList.remove("agent-risk-alert", "agent-scanning");
        if (modal) modal.classList.remove("risk-mode");

        if (state === "risk_alert") {
            orb.classList.add("agent-risk-alert");
            if (modal) modal.classList.add("risk-mode");
            if (badge) {
                badge.textContent = "CRITICAL RISK";
                badge.style.borderColor = "var(--agent-danger)";
                badge.style.color = "var(--agent-danger)";
                badge.style.background = "rgba(239, 68, 68, 0.2)";
            }
            if (statePill) statePill.textContent = "RISK DETECTED";
        } else if (state === "scanning") {
            orb.classList.add("agent-scanning");
            if (badge) {
                badge.textContent = "SCANNING MATRIX";
                badge.style.borderColor = "var(--agent-warning)";
                badge.style.color = "var(--agent-warning)";
                badge.style.background = "rgba(245, 158, 11, 0.2)";
            }
            if (statePill) statePill.textContent = "Scanning...";
        } else {
            if (badge) {
                badge.textContent = "SHIELD ACTIVE";
                badge.style.borderColor = "var(--agent-primary)";
                badge.style.color = "var(--agent-primary)";
                badge.style.background = "rgba(56, 189, 248, 0.15)";
            }
            if (statePill) statePill.textContent = "Shield Active";
        }
    }

    showSpeechBubble(text, isRisk = false) {
        const bubble = document.getElementById("cyberAgentBubble");
        const bubbleText = document.getElementById("cyberAgentBubbleText");
        const bubbleHeader = document.getElementById("cyberAgentBubbleHeader");

        if (!bubble || !bubbleText) return;

        bubbleText.textContent = text;
        if (isRisk) {
            bubble.classList.add("risk-alert");
            if (bubbleHeader) bubbleHeader.textContent = "🚨 THREAT INTERCEPTED";
        } else {
            bubble.classList.remove("risk-alert");
            if (bubbleHeader) bubbleHeader.textContent = "🛡️ Sentinel-AI Reaction";
        }

        bubble.classList.add("active");

        if (this.speechTimeout) clearTimeout(this.speechTimeout);
    }

    hideSpeechBubble(delayMs = 4000) {
        if (this.speechTimeout) clearTimeout(this.speechTimeout);
        this.speechTimeout = setTimeout(() => {
            const bubble = document.getElementById("cyberAgentBubble");
            if (bubble) bubble.classList.remove("active");
        }, delayMs);
    }

    updateThreatLogsUI() {
        const list = document.getElementById("cyberThreatLogsList");
        const countSpan = document.getElementById("cyberThreatCount");
        if (countSpan) countSpan.textContent = this.threatLogs.length;
        if (!list) return;

        if (this.threatLogs.length === 0) {
            list.innerHTML = `<div style="text-align: center; color: var(--agent-muted); font-size: 12px; padding: 24px 0;">✅ No threat violations detected from this device.</div>`;
            return;
        }

        list.innerHTML = this.threatLogs.map(item => `
            <div class="cyber-threat-item">
                <div class="cyber-threat-header">
                    <span class="cyber-threat-badge">${item.level} RISK (${item.score})</span>
                    <span class="cyber-threat-time">${item.time}</span>
                </div>
                <div class="cyber-threat-comment">"${item.comment}"</div>
                <div class="cyber-threat-device">
                    📍 Device: <strong>${item.device}</strong> ${item.isBlocked ? '• <span style="color:#ef4444;font-weight:700;">BLOCKED</span>' : `• Warning ${item.warningsCount}/3`}
                </div>
            </div>
        `).join('');
    }

    populateVoiceList() {
        const select = document.getElementById("agentVoiceSelect");
        if (!select || !this.synth) return;

        const voices = this.synth.getVoices();
        if (!voices || voices.length === 0) return;

        select.innerHTML = voices
            .filter(v => v.lang.startsWith("en"))
            .map(v => `<option value="${v.name}">${v.name} (${v.lang})</option>`)
            .join('');
    }
}

// Instantiate globally on page load
window.addEventListener("DOMContentLoaded", () => {
    if (!window.cyberAgentInstance) {
        window.cyberAgentInstance = new CyberSecurityAgent();
    }
});

// Provide fallback immediate initialization if script loads after DOMContentLoaded
if (document.readyState === "complete" || document.readyState === "interactive") {
    if (!window.cyberAgentInstance) {
        window.cyberAgentInstance = new CyberSecurityAgent();
    }
}

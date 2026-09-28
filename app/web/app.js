/**
 * Antigravity AI Banking Assistant - Frontend Client
 * Powers interactive chat, live Web Speech STT/TTS, Hindsight memory tabs,
 * and real-time judge compliance inspection.
 */

// State
let currentCustomerId = "CUST-1001";
let currentCustomerData = null;
let currentMemoryTab = "facts";
let selectedLanguage = "auto";
let recognition = null;
let isListening = false;

// DOM Elements
const customerSelect = document.getElementById("customerSelect");
const languageSelect = document.getElementById("languageSelect");
const langChips = document.querySelectorAll(".lang-chip");
const custName = document.getElementById("custName");
const custId = document.getElementById("custId");
const custLang = document.getElementById("custLang");
const custAvatar = document.getElementById("custAvatar");
const custAccount = document.getElementById("custAccount");
const custBalance = document.getElementById("custBalance");
const custLoan = document.getElementById("custLoan");
const custMobile = document.getElementById("custMobile");

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const micBtn = document.getElementById("micBtn");
const ttsToggle = document.getElementById("ttsToggle");
const voiceActivityBar = document.getElementById("voiceActivityBar");
const voiceStatusText = document.getElementById("voiceStatusText");

const memTabContent = document.getElementById("memTabContent");
const memTabs = document.querySelectorAll(".mem-tab");

const escBadge = document.getElementById("escBadge");
const escRule = document.getElementById("escRule");
const escDept = document.getElementById("escDept");
const escPriority = document.getElementById("escPriority");
const escReason = document.getElementById("escReason");

const approvedPills = document.getElementById("approvedPills");
const blockedPills = document.getElementById("blockedPills");
const protectedPills = document.getElementById("protectedPills");
const memoryTimeline = document.getElementById("memoryTimeline");
const btnResetMemory = document.getElementById("btnResetMemory");
const chatDialog = document.getElementById("chatDialog");

// Initialize even if this script is loaded after DOMContentLoaded (for example, from cache).
function initializeAgentUi() {
  setupEventListeners();
  loadCustomer(currentCustomerId);
  setupSpeechRecognition();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeAgentUi, { once: true });
} else {
  initializeAgentUi();
}

function setupEventListeners() {
  const chatLauncher = document.getElementById("chatLauncher");
  const chatClose = document.getElementById("chatClose");
  chatLauncher?.addEventListener("click", () => chatDialog?.showModal());
  chatClose?.addEventListener("click", () => chatDialog?.close());
  chatDialog?.addEventListener("click", (event) => {
    if (event.target === chatDialog) chatDialog.close();
  });

  customerSelect.addEventListener("change", (e) => {
    currentCustomerId = e.target.value;
    loadCustomer(currentCustomerId);
  });

  if (languageSelect) {
    languageSelect.addEventListener("change", (e) => {
      selectedLanguage = e.target.value;
      updateActiveLangChip(selectedLanguage);
      if (selectedLanguage !== "auto") {
        custLang.textContent = selectedLanguage;
      }
    });
  }

  langChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const lang = chip.dataset.lang;
      selectedLanguage = lang;
      if (languageSelect) languageSelect.value = lang;
      updateActiveLangChip(lang);
      if (lang !== "auto") {
        custLang.textContent = lang;
      }
      if (chip.dataset.sample) {
        userInput.value = chip.dataset.sample;
        userInput.focus();
      }
    });
  });

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;
    userInput.value = "";
    sendMessage(text, "text");
  });

  micBtn.addEventListener("click", toggleSpeechInput);

  memTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      memTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentMemoryTab = tab.dataset.tab;
      renderMemoryTab();
    });
  });

  btnResetMemory.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/reset", { method: "POST" });
      if (res.ok) {
        addSystemBubble("Hindsight Cloud memory banks reset to initial state.");
        loadCustomer(currentCustomerId);
      }
    } catch (err) {
      console.error("Reset failed:", err);
    }
  });

  // Setup Quick Demo Scenario buttons
  document.getElementById("scenario1Btn").addEventListener("click", () => {
    setScenarioButtonActive("scenario1Btn");
    customerSelect.value = "CUST-1001";
    currentCustomerId = "CUST-1001";
    loadCustomer("CUST-1001").then(() => {
      sendMessage("What is the current status of my PM Mudra loan application?", "text");
    });
  });

  document.getElementById("scenario2Btn").addEventListener("click", () => {
    setScenarioButtonActive("scenario2Btn");
    customerSelect.value = "CUST-1002";
    currentCustomerId = "CUST-1002";
    loadCustomer("CUST-1002").then(() => {
      sendMessage("My mutual fund SIP auto-debit failed again this month!", "text");
    });
  });

  document.getElementById("scenario3Btn").addEventListener("click", () => {
    setScenarioButtonActive("scenario3Btn");
    customerSelect.value = "CUST-1003";
    currentCustomerId = "CUST-1003";
    loadCustomer("CUST-1003").then(() => {
      sendMessage("I want to dispute a transaction charge of ₹48,500 on my credit card in Dubai!", "text");
    });
  });

  document.getElementById("scenario4Btn").addEventListener("click", () => {
    setScenarioButtonActive("scenario4Btn");
    customerSelect.value = "CUST-1004";
    currentCustomerId = "CUST-1004";
    loadCustomer("CUST-1004").then(() => {
      sendMessage("Mera svanidhi ka agla loan kab milega?", "voice", "hi-IN");
    });
  });
}

function setScenarioButtonActive(btnId) {
  document.querySelectorAll(".btn-scenario").forEach(b => b.classList.remove("active"));
  document.getElementById(btnId).classList.add("active");
}

// Fetch Customer & Memory
async function loadCustomer(cid) {
  try {
    const res = await fetch(`/api/customers/${cid}`);
    if (!res.ok) throw new Error("Customer load failed");
    const data = await res.json();
    currentCustomerData = data;
    renderCustomerCard(data.profile);
    renderMemoryTab();
  } catch (err) {
    console.error("Error loading customer:", err);
  }
}

function renderCustomerCard(profile) {
  custName.textContent = profile.customer_name;
  custId.textContent = profile.customer_id;
  const lang = profile.contact?.preferred_language || "en-IN";
  custLang.textContent = lang;

  // Initials for avatar
  const initials = profile.customer_name.split(" ").map(n => n[0]).join("");
  custAvatar.textContent = initials;

  const primaryAcc = (profile.accounts || []).find(a => a.is_primary) || profile.accounts?.[0];
  custAccount.textContent = primaryAcc ? primaryAcc.account_number : "None";
  custBalance.textContent = primaryAcc ? `₹${primaryAcc.balance_inr.toLocaleString("en-IN")}` : "₹0";

  const activeLoan = (profile.loans || []).find(l => l.is_current && l.approved_for_display);
  custLoan.textContent = activeLoan ? activeLoan.loan_id : "None";

  custMobile.textContent = profile.contact?.registered_mobile || "—";
}

function renderMemoryTab() {
  if (!currentCustomerData) return;
  const bank = currentCustomerData.memory_bank || {};

  if (currentMemoryTab === "facts") {
    const facts = bank.recalled_facts || {};
    let html = '<div class="facts-list">';
    const entries = Object.entries(facts);
    if (entries.length === 0) {
      html += '<p class="scenario-sub">No known facts stored yet.</p>';
    } else {
      entries.forEach(([k, v]) => {
        html += `
          <div class="fact-card">
            <span class="fact-key">${k.replace(/_/g, " ")}</span>
            <span class="fact-val">${v}</span>
          </div>`;
      });
    }
    html += '</div>';
    memTabContent.innerHTML = html;
  } else if (currentMemoryTab === "episodes") {
    const episodes = bank.relevant_episodes || [];
    let html = '<div class="facts-list">';
    if (episodes.length === 0) {
      html += '<p class="scenario-sub">No past tickets or episodes on record.</p>';
    } else {
      episodes.forEach(ep => {
        const isResolved = ep.status === "RESOLVED";
        const badgeColor = isResolved ? "pill-green" : "pill-red";
        html += `
          <div class="fact-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <span class="fact-key">${ep.episode_id || ep.ticket_id}</span>
              <span class="pill ${badgeColor}">${ep.status}</span>
            </div>
            <span class="fact-val">${ep.summary || ep.category}</span>
            ${ep.resolution_notes ? `<p class="scenario-sub" style="margin-top:4px;">${ep.resolution_notes}</p>` : ''}
          </div>`;
      });
    }
    html += '</div>';
    memTabContent.innerHTML = html;
  } else if (currentMemoryTab === "reflections") {
    const reflections = bank.reflection_insights || [];
    let html = '<div class="facts-list">';
    if (reflections.length === 0) {
      html += '<p class="scenario-sub">No reflection patterns synthesized yet.</p>';
    } else {
      reflections.forEach(ref => {
        html += `
          <div class="fact-card">
            <span class="fact-key">Synthesized Insight</span>
            <span class="fact-val">${ref}</span>
          </div>`;
      });
    }
    html += '</div>';
    memTabContent.innerHTML = html;
  }
}

function updateActiveLangChip(lang) {
  langChips.forEach(chip => {
    if (chip.dataset.lang === lang) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });
}

function detectScriptLanguage(text) {
  if (!text) return "en-IN";
  if (/[\u0B80-\u0BFF]/.test(text)) return "ta-IN"; // Tamil
  if (/[\u0C00-\u0C7F]/.test(text)) return "te-IN"; // Telugu
  if (/[\u0980-\u09FF]/.test(text)) return "bn-IN"; // Bengali
  if (/[\u0A80-\u0AFF]/.test(text)) return "gu-IN"; // Gujarati
  if (/[\u0C80-\u0CFF]/.test(text)) return "kn-IN"; // Kannada
  if (/[\u0900-\u097F]/.test(text)) {
    const marathiWords = ["माझे", "खाते", "कर्ज", "पैसे", "कधी", "आहे", "मिळेल", "करा"];
    if (marathiWords.some(w => text.includes(w))) return "mr-IN";
    return "hi-IN"; // Hindi
  }
  const hinglishTokens = ["mera", "meri", "kya", "kab", "aayega", "khata", "paise", "paisa", "batao", "chahiye", "hai", "namaste", "dhanyawad"];
  const lower = text.toLowerCase();
  const words = lower.split(/\s+/);
  const matchCount = words.filter(w => hinglishTokens.includes(w)).length;
  if (matchCount >= 2) return "hi-IN";

  return "en-IN";
}

// Send Message Flow
async function sendMessage(text, channel = "text", language = "auto") {
  addMessageBubble("user", text, channel);

  // Determine effective language: if user explicitly selected language, use it; otherwise detect from text!
  let effectiveLang;
  if (selectedLanguage !== "auto") {
    effectiveLang = selectedLanguage;
  } else if (language !== "auto" && language !== "en-IN") {
    effectiveLang = language;
  } else {
    effectiveLang = detectScriptLanguage(text);
  }
  custLang.textContent = effectiveLang;

  try {
    let payload;
    let res;

    if (channel === "voice") {
      res = await fetch("/api/voice/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: currentCustomerId,
          client_transcript: text,
          client_lang: effectiveLang
        })
      });
      const voiceRes = await res.json();
      payload = voiceRes.pipeline_response || voiceRes;
      
      // Auto-speak synthesized response if toggle checked
      if (ttsToggle.checked && voiceRes.tts?.synthesized_text) {
        speakResponse(voiceRes.tts.synthesized_text, voiceRes.tts.language, voiceRes.tts.audio_base64);
      }
    } else {
      res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: currentCustomerId,
          message: text,
          channel: "text",
          detected_language: effectiveLang
        })
      });
      payload = await res.json();

      if (ttsToggle.checked && payload.response) {
        speakResponse(payload.response, payload.detected_language);
      }
    }

    // Render response
    const isEscalated = payload.is_escalated;
    const respLang = payload.detected_language || effectiveLang;
    addMessageBubble("agent", payload.response, channel, isEscalated, respLang);

    // Update Live Inspector Panels
    updateInspector(payload);

    // Refresh customer memory bank in background
    loadCustomer(currentCustomerId);

  } catch (err) {
    console.error("Message send error:", err);
    addMessageBubble("agent", "An error occurred while connecting to the banking orchestrator.");
  }
}

function updateInspector(payload) {
  const esc = payload.escalation || {};
  const isEsc = payload.is_escalated;

  if (isEsc) {
    escBadge.textContent = "ESCALATED";
    escBadge.className = "badge-verdict badge-escalated";
    escRule.textContent = esc.rule_id ? `${esc.rule_id}: ${esc.rule_name}` : "Triggered";
    escDept.textContent = esc.department || "Human Support Desk";
    escPriority.textContent = esc.priority || "HIGH";
    escReason.textContent = esc.reason || "Case escalated deterministically.";
  } else {
    escBadge.textContent = "AUTONOMOUS";
    escBadge.className = "badge-verdict badge-cleared";
    escRule.textContent = "None (Cleared for AI)";
    escDept.textContent = "—";
    escPriority.textContent = "—";
    escReason.textContent = "Within autonomous resolution bounds. Zero escalation rules tripped.";
  }

  // Update Guardrail pills
  const audit = payload.guardrail_audit || {};
  const approved = audit.approved_fields_passed || ["customer_name"];
  approvedPills.innerHTML = approved.slice(0, 5).map(f => `<span class="pill pill-green">${f}</span>`).join("");

  const blocked = audit.blocked_unapproved_fields || [];
  if (blocked.length === 0) {
    blockedPills.innerHTML = '<span class="pill pill-blue">None</span>';
  } else {
    blockedPills.innerHTML = blocked.slice(0, 4).map(f => `<span class="pill pill-red">🔒 ${f}</span>`).join("");
  }

  const protectedEntities = audit.known_entities_protected || [];
  protectedPills.innerHTML = protectedEntities.slice(0, 4).map(e => `<span class="pill pill-blue">${e}</span>`).join("");

  // Timeline entry
  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const newTimelineItem = `
    <div class="timeline-item">
      <div class="timeline-bullet ${isEsc ? 'retain' : ''}"></div>
      <div class="timeline-body">
        <strong>${isEsc ? 'Escalation Handover' : 'Retain() & Resolve'} (${now})</strong>
        <p>${payload.response.slice(0, 80)}...</p>
      </div>
    </div>`;
  memoryTimeline.insertAdjacentHTML("afterbegin", newTimelineItem);
}

function addMessageBubble(sender, text, channel = "text", isEscalation = false, lang = "en-IN") {
  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const bubble = document.createElement("div");
  bubble.className = `message-bubble ${sender}-bubble ${isEscalation ? 'escalation-alert-bubble' : ''}`;

  const header = document.createElement("div");
  header.className = "bubble-header";
  header.innerHTML = `
    <span>${sender === 'user' ? '👤 Customer' : (isEscalation ? '🚨 Escalation Manager' : '🤖 Banking Assistant')} ${channel === 'voice' ? '🎙️' : ''}</span>
    <span class="bubble-time">${timeStr}</span>
  `;

  const body = document.createElement("p");
  body.textContent = text;

  bubble.appendChild(header);
  bubble.appendChild(body);

  // Add 🔊 Speak button to agent responses so user can re-listen in that language at any time
  if (sender === 'agent') {
    const actions = document.createElement("div");
    actions.className = "bubble-actions";
    const speakBtn = document.createElement("button");
    speakBtn.type = "button";
    speakBtn.className = "bubble-speak-btn";
    speakBtn.innerHTML = `<span>🔊</span> Listen (${lang || "voice"})`;
    speakBtn.onclick = () => speakResponse(text, lang);
    actions.appendChild(speakBtn);
    bubble.appendChild(actions);
  }

  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSystemBubble(text) {
  const bubble = document.createElement("div");
  bubble.className = "message-bubble system-bubble";
  bubble.innerHTML = `<p>${text}</p>`;
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Global Voice Cache & Async Preloader
let availableVoices = [];

function loadBrowserVoices() {
  if ('speechSynthesis' in window) {
    availableVoices = window.speechSynthesis.getVoices();
  }
}
loadBrowserVoices();
if ('speechSynthesis' in window && window.speechSynthesis.onvoiceschanged !== undefined) {
  window.speechSynthesis.onvoiceschanged = loadBrowserVoices;
}

function getBestVoiceForLanguage(targetLang) {
  if (!availableVoices || availableVoices.length === 0) {
    availableVoices = window.speechSynthesis.getVoices();
  }
  const langLower = (targetLang || "en-IN").toLowerCase();
  const langPrefix = langLower.split("-")[0];

  // 1. Exact locale match (e.g. 'ta-in', 'hi-in', 'te-in', 'en-in', 'bn-in', 'mr-in', 'gu-in', 'kn-in')
  let match = availableVoices.find(v => v.lang.toLowerCase() === langLower || v.lang.toLowerCase().replace("_", "-") === langLower);
  if (match) return match;

  // 2. Language prefix match (e.g. starts with 'ta', 'te', 'hi', 'bn', 'mr', 'gu', 'kn', 'en')
  match = availableVoices.find(v => v.lang.toLowerCase().startsWith(langPrefix));
  if (match) return match;

  // 3. Check for name match (e.g. 'Google தமிழ்', 'Microsoft Valluvar', 'Hindi', etc.)
  const langNameMap = {
    'ta': 'tamil',
    'te': 'telugu',
    'hi': 'hindi',
    'bn': 'bengali',
    'mr': 'marathi',
    'gu': 'gujarati',
    'kn': 'kannada',
    'en': 'english'
  };
  const nameKeyword = langNameMap[langPrefix];
  if (nameKeyword) {
    match = availableVoices.find(v => v.name.toLowerCase().includes(nameKeyword));
    if (match) return match;
  }

  // If no matching voice for this language family, return null
  // Do NOT force an incompatible voice (e.g. an English voice will choke on Tamil characters)
  return null;
}

// Web Speech STT
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("Web Speech API not supported in this browser.");
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add("listening");
    voiceActivityBar.classList.add("active");
    voiceStatusText.textContent = "Listening to speech...";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    voiceStatusText.textContent = `Transcribed: "${transcript}"`;
    sendMessage(transcript, "voice", recognition.lang);
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    if (event.error === 'language-not-supported') {
      console.log("[STT] Language not supported by browser STT, falling back to en-IN/hi-IN");
      recognition.lang = 'en-IN';
      recognition.start();
      return;
    }
    stopListening();
  };

  recognition.onend = () => {
    stopListening();
  };
}

function toggleSpeechInput() {
  if (!recognition) {
    alert("Web Speech API is not supported in this browser. Please use Chrome/Edge or type your message.");
    return;
  }

  if (isListening) {
    recognition.stop();
    stopListening();
  } else {
    // Set recognition language based on selected language
    // If 'auto', listen in 'en-IN' (Indian English handles English, names, and loan words smoothly)
    const lang = selectedLanguage !== "auto" ? selectedLanguage : "en-IN";
    recognition.lang = lang;
    recognition.start();
  }
}

function stopListening() {
  isListening = false;
  micBtn.classList.remove("listening");
  voiceActivityBar.classList.remove("active");
}

let currentAudioPlayer = null;

function stopCurrentAudio() {
  if (currentAudioPlayer) {
    currentAudioPlayer.pause();
    currentAudioPlayer = null;
  }
  if ('speechSynthesis' in window && (window.speechSynthesis.speaking || window.speechSynthesis.pending)) {
    window.speechSynthesis.cancel();
  }
  voiceActivityBar.classList.remove("active");
}

function playBase64Audio(b64Data, lang) {
  stopCurrentAudio();
  try {
    const audio = new Audio("data:audio/mp3;base64," + b64Data);
    currentAudioPlayer = audio;
    voiceActivityBar.classList.add("active");
    voiceStatusText.textContent = `Speaking (${lang} - Neural Indic Audio)...`;

    audio.onended = () => {
      voiceActivityBar.classList.remove("active");
      currentAudioPlayer = null;
    };
    audio.onerror = (e) => {
      console.warn("[TTS] Base64 audio playback failed, falling back to server stream:", e);
      voiceActivityBar.classList.remove("active");
      currentAudioPlayer = null;
    };

    audio.play().catch(err => {
      console.warn("[TTS] Autoplay prevented, click listen button to play:", err);
      voiceActivityBar.classList.remove("active");
    });
  } catch (err) {
    console.error("[TTS] Failed to initialize Base64 Audio:", err);
  }
}

function playServerAudio(text, lang) {
  stopCurrentAudio();
  const cleanSnippet = text.replace(/[*#`_]/g, "").slice(0, 190);
  const streamUrl = `/api/voice/tts?text=${encodeURIComponent(cleanSnippet)}&lang=${encodeURIComponent(lang)}`;

  voiceActivityBar.classList.add("active");
  voiceStatusText.textContent = `Speaking (${lang} - Neural Indic Voice)...`;

  const audio = new Audio(streamUrl);
  currentAudioPlayer = audio;

  audio.onended = () => {
    voiceActivityBar.classList.remove("active");
    currentAudioPlayer = null;
  };
  audio.onerror = (e) => {
    console.warn("[TTS] Server audio stream failed:", e);
    voiceActivityBar.classList.remove("active");
    currentAudioPlayer = null;
  };

  audio.play().catch(err => {
    console.warn("[TTS] Autoplay prevented, click listen button to play:", err);
    voiceActivityBar.classList.remove("active");
  });
}

// Guaranteed Multi-Language Speech Engine: Uses native browser SAPI voice if installed,
// or seamless neural server audio streaming across all 8 Indic/global languages
function speakResponse(text, lang = "en-IN", audioBase64 = null) {
  stopCurrentAudio();

  // 1. If base64 audio payload was returned by backend, play immediately
  if (audioBase64) {
    playBase64Audio(audioBase64, lang);
    return;
  }

  // 2. Check if the browser has a native local voice installed for this language
  const chosenVoice = getBestVoiceForLanguage(lang);

  // If language is an Indic language and browser has NO native local voice for it,
  // stream directly from the neural audio endpoint
  const isIndicNonEnglish = lang && !lang.toLowerCase().startsWith("en");
  if (!chosenVoice && isIndicNonEnglish) {
    console.log(`[TTS] No local voice for [${lang}], streaming neural audio`);
    playServerAudio(text, lang);
    return;
  }

  if (!('speechSynthesis' in window)) {
    playServerAudio(text, lang);
    return;
  }

  // Resume synthesis if browser paused it
  window.speechSynthesis.resume();

  setTimeout(() => {
    try {
      const utterance = new SpeechSynthesisUtterance(text);
      if (chosenVoice) {
        utterance.voice = chosenVoice;
        utterance.lang = chosenVoice.lang;
        console.log(`[TTS] Speaking with native local voice: ${chosenVoice.name} (${chosenVoice.lang}) for [${lang}]`);
      } else {
        utterance.lang = lang || "en-IN";
      }

      utterance.rate = 0.95;
      utterance.pitch = 1.0;

      utterance.onstart = () => {
        voiceActivityBar.classList.add("active");
        const voiceName = chosenVoice ? chosenVoice.name.split(" ")[0] : "Browser";
        voiceStatusText.textContent = `Speaking (${lang || "en"} - ${voiceName})...`;
      };

      utterance.onend = () => {
        voiceActivityBar.classList.remove("active");
      };

      utterance.onerror = (e) => {
        console.warn("[TTS] Local voice notice, falling back to neural audio:", e.error);
        voiceActivityBar.classList.remove("active");
        playServerAudio(text, lang);
      };

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error("[TTS] Speech synthesis invocation failed, falling back to neural stream:", err);
      playServerAudio(text, lang);
    }
  }, 60);
}


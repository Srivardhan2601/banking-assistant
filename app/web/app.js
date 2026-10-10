/**
 * AI Banking Support & Haq Saathi - Unified Frontend Client
 * Powers interactive chat, live Web Speech STT/TTS, Hindsight memory tabs,
 * real-time compliance inspector, and Haq Saathi worker rights companion.
 */

// ============================================================================
// State Variables
// ============================================================================
let currentMode = "banking"; // "banking" | "haq"
let activeTab = "customer"; // "customer" | "tickets" | "insights" | "guardrails"

// Banking State
let currentCustomerId = "CUST-1005";
let currentCustomerData = null;
let selectedLanguage = "auto";
let recognition = null;
let isListening = false;
let availableVoices = [];

// Haq Saathi State
let currentHaqWorkerId = "WRK-201";
let haqSessionId = "haq_sess_" + Math.random().toString(36).substring(2, 9);
let currentHaqComplaintId = null;
let currentHaqRights = null;
let lastSpokenText = "";

// Worker Persona Dictionary
const HAQ_WORKERS = {
  "WRK-201": {
    name: "లక్ష్మి (Lakshmi)",
    trade: "ఇళ్ల పని (Domestic Worker)",
    amount: "₹18,000 [3 నెలలు బాకీ]",
    employer: "రావు గారు (Banjara Hills)",
    district: "Hyderabad, Telangana",
    right: "Payment of Wages Act, 1936",
    lang: "te-IN",
    sampleQuery: "గత మూడు నెలలుగా యజమాని జీతం ఇవ్వలేదు, మొత్తం 18000 రూపాయలు బాకీ ఉంది."
  },
  "WRK-202": {
    name: "अमित (Amit)",
    trade: "डिलीवरी राइडर (Delivery Partner)",
    amount: "₹9,500 [न्यूनतम दर व इंसेंटिव]",
    employer: "क्विक डिलीवरी हब (Warangal)",
    district: "Warangal, Telangana",
    right: "Code on Wages & Minimum Wages Act",
    lang: "hi-IN",
    sampleQuery: "कंपनी ने दो महीनों से न्यूनतम गारंटी और डिलीवरी इंसेंटिव के 9500 रुपये नहीं दिए हैं।"
  },
  "WRK-203": {
    name: "محمد راشد (Rashid)",
    trade: "تعمیراتی کام (Construction Mason)",
    amount: "₹25,000 [علاج کے اخراجات و مزدوری]",
    employer: "کریم بھائی کنسٹرکشن (Gachibowli)",
    district: "Rangareddy, Telangana",
    right: "BOCW Welfare & Compensation Act",
    lang: "ur-IN",
    sampleQuery: "سائట్ پر اونچائی سے گر کر چوٹ لگی، ٹھیکیدار علاج اور 25000 روپے کی مزدوری نہیں دے رہا ہے۔"
  }
};


// ============================================================================
// Initialization
// ============================================================================
function initializeApp() {
  setupThemeSwitcher();
  setupLoginPortal();
  setupEventListeners();
  loadCustomer(currentCustomerId);
  setupSpeechRecognition();
  loadBrowserVoices();
  
  // Auto open modal if URL contains ?chat=1
  if (new URLSearchParams(window.location.search).get("chat") === "1") {
    openChatModal();
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeApp, { once: true });
} else {
  initializeApp();
}


// ============================================================================
// Theme Switcher
// ============================================================================
function setupThemeSwitcher() {
  let savedTheme = localStorage.getItem("banking_assistant_theme") || "dark";
  applyTheme(savedTheme);

  document.querySelectorAll(".theme-icon-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTheme = btn.getAttribute("data-theme-val");
      if (targetTheme) applyTheme(targetTheme);
    });
  });
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("banking_assistant_theme", theme);

  document.querySelectorAll(".theme-icon-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-theme-val") === theme);
  });
}


// ============================================================================
// Authentication & Login Portal
// ============================================================================
function setupLoginPortal() {
  const loginPortalView = document.getElementById("loginPortalView");
  const dashboardView = document.getElementById("dashboardView");
  const loginForm = document.getElementById("loginForm");
  const loginAccountNumber = document.getElementById("loginAccountNumber");
  const loginPin = document.getElementById("loginPin");
  const keepSignedIn = document.getElementById("keepSignedIn");
  const togglePinVisibility = document.getElementById("togglePinVisibility");
  const loginStatusFeedback = document.getElementById("loginStatusFeedback");
  const btnSubmitLogin = document.getElementById("btnSubmitLogin");
  const btnEnterpriseSso = document.getElementById("btnEnterpriseSso");
  const btnSignOut = document.getElementById("btnSignOut");
  const authUserName = document.getElementById("authUserName");
  const tabSignIn = document.getElementById("tabSignIn");
  const tabRegister = document.getElementById("tabRegister");
  const customerSelect = document.getElementById("customerSelect");

  function showDashboard(customer) {
    if (loginPortalView) loginPortalView.style.display = "none";
    if (dashboardView) dashboardView.style.display = "block";
    if (customer) {
      currentCustomerId = customer.id || currentCustomerId;
      if (customerSelect) customerSelect.value = currentCustomerId;
      if (authUserName) authUserName.textContent = customer.name || "Customer";
    }
  }

  function showLoginPortal() {
    if (dashboardView) dashboardView.style.display = "none";
    if (loginPortalView) loginPortalView.style.display = "flex";
  }

  // 1. Initial State: Show Login Portal by default (use ?dashboard=1 to bypass)
  const urlParams = new URLSearchParams(window.location.search);
  const bypassToDashboard = urlParams.get("dashboard") === "1";

  if (bypassToDashboard) {
    const savedAuthStr = localStorage.getItem("banking_auth_customer") || sessionStorage.getItem("banking_auth_customer");
    if (savedAuthStr) {
      try {
        const savedUser = JSON.parse(savedAuthStr);
        if (savedUser && savedUser.id) {
          currentCustomerId = savedUser.id;
          if (customerSelect) customerSelect.value = savedUser.id;
          if (authUserName) authUserName.textContent = savedUser.name || "Customer";
        }
      } catch (e) {
        console.warn("Could not parse saved user session:", e);
      }
    }
    showDashboard();
  } else {
    showLoginPortal();
  }

  // 2. Quick Persona Selection Pills
  document.querySelectorAll(".quick-acc-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".quick-acc-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const acc = btn.getAttribute("data-acc");
      const pin = btn.getAttribute("data-pin") || "1234";
      if (loginAccountNumber) loginAccountNumber.value = acc;
      if (loginPin) loginPin.value = pin;
      if (loginStatusFeedback) {
        loginStatusFeedback.textContent = "";
        loginStatusFeedback.className = "login-feedback";
      }
    });
  });

  // 3. PIN Visibility Toggle
  togglePinVisibility?.addEventListener("click", () => {
    if (!loginPin) return;
    if (loginPin.type === "password") {
      loginPin.type = "text";
      togglePinVisibility.title = "Hide PIN";
      togglePinVisibility.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
          <line x1="1" y1="1" x2="23" y2="23" />
        </svg>
      `;
    } else {
      loginPin.type = "password";
      togglePinVisibility.title = "Show PIN";
      togglePinVisibility.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      `;
    }
  });

  // 4. Tab switcher (Sign In vs Register)
  tabSignIn?.addEventListener("click", () => {
    tabSignIn.classList.add("active");
    tabRegister?.classList.remove("active");
    if (loginStatusFeedback) {
      loginStatusFeedback.textContent = "";
      loginStatusFeedback.className = "login-feedback";
    }
  });

  tabRegister?.addEventListener("click", () => {
    tabRegister.classList.add("active");
    tabSignIn?.classList.remove("active");
    if (loginStatusFeedback) {
      loginStatusFeedback.className = "login-feedback info";
      loginStatusFeedback.textContent = "Instant registration: Enter Account # and 4-digit PIN to activate.";
    }
  });

  // 5. Submit Login Form
  loginForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    let accountNum = loginAccountNumber?.value.trim();
    let pin = loginPin?.value.trim();

    // Auto-populate default demo credentials if user directly clicks Sign In
    if (!accountNum && !pin) {
      accountNum = "AC-5002938491";
      pin = "1234";
      if (loginAccountNumber) loginAccountNumber.value = accountNum;
      if (loginPin) loginPin.value = pin;
    } else if (!accountNum) {
      accountNum = "AC-5002938491";
      if (loginAccountNumber) loginAccountNumber.value = accountNum;
    } else if (!pin) {
      pin = "1234";
      if (loginPin) loginPin.value = pin;
    }

    if (pin.length !== 4) {
      if (loginStatusFeedback) {
        loginStatusFeedback.className = "login-feedback error";
        loginStatusFeedback.textContent = "PIN must be exactly 4 digits";
      }
      return;
    }

    if (btnSubmitLogin) {
      btnSubmitLogin.disabled = true;
      btnSubmitLogin.innerHTML = `<span>Verifying credentials...</span>`;
    }

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account_number: accountNum, pin: pin })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        if (loginStatusFeedback) {
          loginStatusFeedback.className = "login-feedback success";
          loginStatusFeedback.textContent = `✓ Access granted. Welcome ${data.customer.name}!`;
        }

        const storage = keepSignedIn?.checked ? localStorage : sessionStorage;
        storage.setItem("banking_auth_customer", JSON.stringify(data.customer));

        setTimeout(() => {
          if (btnSubmitLogin) {
            btnSubmitLogin.disabled = false;
            btnSubmitLogin.innerHTML = `<span>Sign In</span>`;
          }
          showDashboard(data.customer);
          loadCustomer(data.customer.id);
        }, 300);
      } else {
        if (loginStatusFeedback) {
          loginStatusFeedback.className = "login-feedback error";
          loginStatusFeedback.textContent = data.detail || "Authentication failed. Default PIN is 1234.";
        }
        if (btnSubmitLogin) {
          btnSubmitLogin.disabled = false;
          btnSubmitLogin.innerHTML = `<span>Sign In</span>`;
        }
      }
    } catch (err) {
      console.error("Login request error:", err);
      if (loginStatusFeedback) {
        loginStatusFeedback.className = "login-feedback error";
        loginStatusFeedback.textContent = "Connection error. Please try again.";
      }
      if (btnSubmitLogin) {
        btnSubmitLogin.disabled = false;
        btnSubmitLogin.innerHTML = `<span>Sign In</span>`;
      }
    }
  });

  // 6. Enterprise SSO 1-Click Login
  btnEnterpriseSso?.addEventListener("click", () => {
    if (btnEnterpriseSso) {
      btnEnterpriseSso.disabled = true;
      btnEnterpriseSso.innerHTML = `<span>Authenticating via SSO...</span>`;
    }

    if (loginStatusFeedback) {
      loginStatusFeedback.className = "login-feedback success";
      loginStatusFeedback.textContent = "✓ SSO token verified. Welcome Rohan Verma (CUST-1005).";
    }

    const defaultCustomer = {
      id: "CUST-1005",
      name: "Rohan Verma",
      account_number: "AC-5002938491",
      account_type: "Advantage Savings"
    };

    const storage = keepSignedIn?.checked ? localStorage : sessionStorage;
    storage.setItem("banking_auth_customer", JSON.stringify(defaultCustomer));

    setTimeout(() => {
      if (btnEnterpriseSso) {
        btnEnterpriseSso.disabled = false;
        btnEnterpriseSso.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
          <span>Enterprise SSO</span>
        `;
      }
      showDashboard(defaultCustomer);
      loadCustomer(defaultCustomer.id);
    }, 350);
  });

  // 7. Sign Out Button
  btnSignOut?.addEventListener("click", () => {
    localStorage.removeItem("banking_auth_customer");
    sessionStorage.removeItem("banking_auth_customer");
    showLoginPortal();
    if (loginStatusFeedback) {
      loginStatusFeedback.className = "login-feedback info";
      loginStatusFeedback.textContent = "You have signed out securely.";
    }
  });

  // 8. Forgot PIN Link
  document.getElementById("forgotPinLink")?.addEventListener("click", (e) => {
    e.preventDefault();
    if (loginPin) loginPin.value = "1234";
    if (loginStatusFeedback) {
      loginStatusFeedback.className = "login-feedback info";
      loginStatusFeedback.textContent = "Demo Master PIN is 1234 for all accounts.";
    }
  });
}


// ============================================================================
// Event Listeners Setup
// ============================================================================
function setupEventListeners() {
  // 1. "Powered by ⌄" Dropdown Toggle
  const btnPoweredBy = document.getElementById("btnPoweredBy");
  const poweredDropdownMenu = document.getElementById("poweredDropdownMenu");

  btnPoweredBy?.addEventListener("click", (e) => {
    e.stopPropagation();
    const isExpanded = btnPoweredBy.getAttribute("aria-expanded") === "true";
    btnPoweredBy.setAttribute("aria-expanded", !isExpanded);
    poweredDropdownMenu?.classList.toggle("active");
  });

  document.addEventListener("click", (e) => {
    if (!btnPoweredBy?.contains(e.target) && !poweredDropdownMenu?.contains(e.target)) {
      btnPoweredBy?.setAttribute("aria-expanded", "false");
      poweredDropdownMenu?.classList.remove("active");
    }
  });

  // 2. "Chat with us" Pop-Up Modal Controls
  const btnChatWithUs = document.getElementById("btnChatWithUs");
  const floatingChatLauncher = document.getElementById("floatingChatLauncher");
  const chatClose = document.getElementById("chatClose");
  const chatDialog = document.getElementById("chatDialog");

  btnChatWithUs?.addEventListener("click", openChatModal);
  floatingChatLauncher?.addEventListener("click", openChatModal);
  chatClose?.addEventListener("click", () => chatDialog?.close());
  chatDialog?.addEventListener("click", (event) => {
    if (event.target === chatDialog) chatDialog.close();
  });

  // 3. Navigation Tabs
  const tabCustomerBtn = document.getElementById("tabCustomerBtn");
  const tabTicketsBtn = document.getElementById("tabTicketsBtn");
  const tabInsightsBtn = document.getElementById("tabInsightsBtn");
  const tabGuardrailsBtn = document.getElementById("tabGuardrailsBtn");
  const tabHaqSwitchBtn = document.getElementById("tabHaqSwitchBtn");

  tabCustomerBtn?.addEventListener("click", () => switchNavTab("customer"));
  tabTicketsBtn?.addEventListener("click", () => switchNavTab("tickets"));
  tabInsightsBtn?.addEventListener("click", () => switchNavTab("insights"));
  tabGuardrailsBtn?.addEventListener("click", () => switchNavTab("guardrails"));
  tabHaqSwitchBtn?.addEventListener("click", toggleMode);

  // 4. Dropdowns (Worker for Haq Saathi)
  const haqWorkerSelect = document.getElementById("haqWorkerSelect");
  haqWorkerSelect?.addEventListener("change", (e) => {
    currentHaqWorkerId = e.target.value;
    loadHaqWorker(currentHaqWorkerId);
  });

  // 5. Language Selector
  const languageSelect = document.getElementById("languageSelect");
  languageSelect?.addEventListener("change", (e) => {
    selectedLanguage = e.target.value;
  });

  // 6. Inline Chat Form
  const chatForm = document.getElementById("chatForm");
  const userInput = document.getElementById("userInput");
  chatForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = userInput?.value.trim();
    if (!text) return;
    if (userInput) userInput.value = "";
    sendMessage(text, "text");
  });

  // 7. Modal Chat Form
  const modalChatForm = document.getElementById("modalChatForm");
  const modalUserInput = document.getElementById("modalUserInput");
  modalChatForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = modalUserInput?.value.trim();
    if (!text) return;
    if (modalUserInput) modalUserInput.value = "";
    sendMessage(text, "text");
  });

  // 8. Microphones (Inline & Modal)
  const micBtn = document.getElementById("micBtn");
  const modalMicBtn = document.getElementById("modalMicBtn");
  micBtn?.addEventListener("click", toggleSpeechInput);
  modalMicBtn?.addEventListener("click", toggleSpeechInput);

  // 9. Replay Voice Button
  const replayVoiceBtn = document.getElementById("replayVoiceBtn");
  replayVoiceBtn?.addEventListener("click", () => {
    if (lastSpokenText) {
      speakResponse(lastSpokenText, selectedLanguage !== "auto" ? selectedLanguage : "en-IN");
    }
  });

  // 10. Reset State Button
  const btnResetMemory = document.getElementById("btnResetMemory");
  btnResetMemory?.addEventListener("click", async () => {
    try {
      if (currentMode === "banking") {
        await fetch("/api/reset", { method: "POST" });
        clearChatUI();
        addSystemBubble("Hindsight Cloud memory banks and session state have been reset.");
        loadCustomer(currentCustomerId);
      } else {
        haqSessionId = "haq_sess_" + Math.random().toString(36).substring(2, 9);
        currentHaqComplaintId = null;
        clearChatUI();
        addHaqWelcomeBubble();
        updateHaqInspectorState("GREETING", 0, "UNDERSTAND_PROBLEM");
      }
    } catch (err) {
      console.error("Reset failed:", err);
    }
  });



  // 12. Haq Saathi Demo Scenarios
  document.getElementById("haqScenario1Btn")?.addEventListener("click", () => {
    runHaqDemoScenario("scenario_te_domestic", "haqScenario1Btn", "WRK-201");
  });
  document.getElementById("haqScenario2Btn")?.addEventListener("click", () => {
    runHaqDemoScenario("scenario_hi_delivery", "haqScenario2Btn", "WRK-202");
  });
  document.getElementById("haqScenario3Btn")?.addEventListener("click", () => {
    runHaqDemoScenario("scenario_ur_construction", "haqScenario3Btn", "WRK-203");
  });

  // 13. Haq Saathi Quick Problem Chips
  document.querySelectorAll(".haq-pill-btn").forEach((chip) => {
    chip.addEventListener("click", () => {
      const issue = chip.getAttribute("data-issue");
      triggerHaqQuickProblem(issue);
    });
  });

  // 14. PDF Downloads
  const haqDownloadLocalPdf = document.getElementById("haqDownloadLocalPdf");
  const haqDownloadEngPdf = document.getElementById("haqDownloadEngPdf");

  haqDownloadLocalPdf?.addEventListener("click", () => {
    if (currentHaqComplaintId) {
      const lang = selectedLanguage !== "auto" ? selectedLanguage : "te-IN";
      window.open(`/api/haq/complaint/${currentHaqComplaintId}/pdf?lang=${lang}`, "_blank");
    } else {
      alert("Please complete the grievance questions first to generate the petition.");
    }
  });

  haqDownloadEngPdf?.addEventListener("click", () => {
    if (currentHaqComplaintId) {
      window.open(`/api/haq/complaint/${currentHaqComplaintId}/pdf?lang=en-IN`, "_blank");
    } else {
      alert("Please complete the grievance questions first to generate the petition.");
    }
  });

  // 15. Modals & Dialogs
  const btnWhyHaqAnswer = document.getElementById("btnWhyHaqAnswer");
  const whyModal = document.getElementById("whyModal");
  const closeWhyBtn = document.getElementById("closeWhyBtn");
  const dangerModal = document.getElementById("dangerModal");
  const closeDangerBtn = document.getElementById("closeDangerBtn");

  btnWhyHaqAnswer?.addEventListener("click", showWhyModal);
  closeWhyBtn?.addEventListener("click", () => { if (whyModal) whyModal.style.display = "none"; });
  closeDangerBtn?.addEventListener("click", () => { if (dangerModal) dangerModal.style.display = "none"; });
}


// ============================================================================
// Modal & Pop-Up Dialog Functions
// ============================================================================
function openChatModal() {
  const chatDialog = document.getElementById("chatDialog");
  if (!chatDialog) return;
  if (!chatDialog.open) {
    chatDialog.showModal();
    const modalUserInput = document.getElementById("modalUserInput");
    modalUserInput?.focus();
  }
}


// ============================================================================
// Navigation Tabs & View Switching
// ============================================================================
function switchNavTab(tabName) {
  activeTab = tabName;

  document.querySelectorAll(".nav-tab:not(.service-switch-tab)").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tabName);
  });

  const cardFactsTitle = document.getElementById("cardFactsTitle");
  const factsTabBadge = document.getElementById("factsTabBadge");
  const paneFacts = document.getElementById("paneFacts");
  const paneTickets = document.getElementById("paneTickets");
  const paneInsights = document.getElementById("paneInsights");
  const cardInspector = document.getElementById("cardInspector");

  // Reset highlight
  cardInspector?.classList.remove("highlight");

  if (tabName === "customer") {
    if (cardFactsTitle) cardFactsTitle.textContent = currentMode === "banking" ? "VERIFIED FACTS" : "WORKER DETAILS";
    if (factsTabBadge) factsTabBadge.textContent = "Profile";
    if (paneFacts) paneFacts.style.display = "flex";
    if (paneTickets) paneTickets.style.display = "none";
    if (paneInsights) paneInsights.style.display = "none";

  } else if (tabName === "tickets") {
    if (cardFactsTitle) cardFactsTitle.textContent = currentMode === "banking" ? "SUPPORT TICKETS & EPISODES" : "GRIEVANCE DISPUTES";
    if (factsTabBadge) factsTabBadge.textContent = "Tickets";
    if (paneFacts) paneFacts.style.display = "none";
    if (paneTickets) paneTickets.style.display = "flex";
    if (paneInsights) paneInsights.style.display = "none";
    renderTicketsPane();

  } else if (tabName === "insights") {
    if (cardFactsTitle) cardFactsTitle.textContent = currentMode === "banking" ? "HINDSIGHT REFLECTION INSIGHTS" : "LEGAL RIGHTS OVERVIEW";
    if (factsTabBadge) factsTabBadge.textContent = "Memory";
    if (paneFacts) paneFacts.style.display = "none";
    if (paneTickets) paneTickets.style.display = "none";
    if (paneInsights) paneInsights.style.display = "flex";
    renderInsightsPane();

  } else if (tabName === "guardrails") {
    // Focus and highlight the Right Card
    cardInspector?.classList.add("highlight");
    cardInspector?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}


// ============================================================================
// Mode Toggle: Banking Support vs Haq Saathi
// ============================================================================
function toggleMode() {
  setMode(currentMode === "banking" ? "haq" : "banking");
}

function setMode(mode) {
  currentMode = mode;
  document.body.setAttribute("data-mode", mode);

  const bankingLogoSvg = document.getElementById("bankingLogoSvg");
  const haqLogoEmoji = document.getElementById("haqLogoEmoji");
  const appHeaderTitle = document.getElementById("appHeaderTitle");
  const appHeaderSubtitle = document.getElementById("appHeaderSubtitle");
  const tabHaqSwitchBtn = document.getElementById("tabHaqSwitchBtn");
  const cardFactsTitle = document.getElementById("cardFactsTitle");
  const conversationTitle = document.getElementById("conversationTitle");
  const inspectorTitle = document.getElementById("inspectorTitle");
  const chatModalTitle = document.getElementById("chatModalTitle");
  const userInput = document.getElementById("userInput");
  const modalUserInput = document.getElementById("modalUserInput");

  const bankingScenariosBar = document.getElementById("bankingScenariosBar");
  const haqScenariosBar = document.getElementById("haqScenariosBar");
  const bankingFactsView = document.getElementById("bankingFactsView");
  const haqFactsView = document.getElementById("haqFactsView");
  const haqChipsBar = document.getElementById("haqChipsBar");
  const bankingInspectorView = document.getElementById("bankingInspectorView");
  const haqInspectorView = document.getElementById("haqInspectorView");
  const replayVoiceBtn = document.getElementById("replayVoiceBtn");

  document.querySelectorAll(".haq-only-item").forEach((el) => {
    el.style.display = mode === "haq" ? "flex" : "none";
  });

  if (mode === "banking") {
    if (bankingLogoSvg) bankingLogoSvg.style.display = "block";
    if (haqLogoEmoji) haqLogoEmoji.style.display = "none";
    if (appHeaderTitle) appHeaderTitle.textContent = "AI Banking Support";
    if (appHeaderSubtitle) appHeaderSubtitle.textContent = "Financial services";
    if (tabHaqSwitchBtn) tabHaqSwitchBtn.innerHTML = "<span>⚖️ Haq Saathi</span>";
    if (cardFactsTitle) cardFactsTitle.textContent = "VERIFIED FACTS";
    if (conversationTitle) conversationTitle.textContent = "Conversation panel";
    if (inspectorTitle) inspectorTitle.textContent = "GUARDRAILS & INSPECTOR";
    if (chatModalTitle) chatModalTitle.textContent = "AI Customer Service Assistant";
    if (userInput) userInput.placeholder = "Type your message...";
    if (modalUserInput) modalUserInput.placeholder = "Type your message...";

    const bankingCustomerBar = document.getElementById("bankingCustomerBar");
    if (bankingCustomerBar) bankingCustomerBar.style.display = "flex";
    if (haqScenariosBar) haqScenariosBar.style.display = "none";
    if (bankingFactsView) bankingFactsView.style.display = "flex";
    if (haqFactsView) haqFactsView.style.display = "none";
    if (haqChipsBar) haqChipsBar.style.display = "none";
    if (bankingInspectorView) bankingInspectorView.style.display = "block";
    if (haqInspectorView) haqInspectorView.style.display = "none";
    if (replayVoiceBtn) replayVoiceBtn.style.display = "none";

    loadCustomer(currentCustomerId);

  } else {
    // Haq Saathi Mode
    if (bankingLogoSvg) bankingLogoSvg.style.display = "none";
    if (haqLogoEmoji) haqLogoEmoji.style.display = "block";
    if (appHeaderTitle) appHeaderTitle.textContent = "Haq Saathi (హక్ సాథీ • हक़ साथी)";
    if (appHeaderSubtitle) appHeaderSubtitle.textContent = "Legal rights companion for informal workers";
    if (tabHaqSwitchBtn) tabHaqSwitchBtn.innerHTML = "<span>🏦 Switch to Banking</span>";
    if (cardFactsTitle) cardFactsTitle.textContent = "WORKER DETAILS";
    if (conversationTitle) conversationTitle.textContent = "Voice Rights Conversation";
    if (inspectorTitle) inspectorTitle.textContent = "LEGAL MACHINE & JURISDICTION";
    if (chatModalTitle) chatModalTitle.textContent = "Haq Saathi Legal Rights Assistant";
    if (userInput) userInput.placeholder = "మీ సమస్యను చెప్పండి లేదా టైప్ చేయండి... (Speak or type your problem)";
    if (modalUserInput) modalUserInput.placeholder = "మీ సమస్యను చెప్పండి లేదా టైప్ చేయండి...";

    const bankingCustomerBar = document.getElementById("bankingCustomerBar");
    if (bankingCustomerBar) bankingCustomerBar.style.display = "none";
    if (haqScenariosBar) haqScenariosBar.style.display = "flex";
    if (bankingFactsView) bankingFactsView.style.display = "none";
    if (haqFactsView) haqFactsView.style.display = "flex";
    if (haqChipsBar) haqChipsBar.style.display = "flex";
    if (bankingInspectorView) bankingInspectorView.style.display = "none";
    if (haqInspectorView) haqInspectorView.style.display = "block";
    if (replayVoiceBtn) replayVoiceBtn.style.display = "inline-block";

    loadHaqWorker(currentHaqWorkerId);
    resetHaqConversation();
  }

  // Refresh active tab view
  switchNavTab(activeTab);
}


// ============================================================================
// Customer Data Loader (Banking)
// ============================================================================
async function loadCustomer(cid) {
  try {
    const res = await fetch(`/api/customers/${cid}`);
    if (!res.ok) throw new Error("Customer load failed");
    const data = await res.json();
    currentCustomerData = data;
    renderCustomerFacts(data.profile);
    renderTicketsPane();
    renderInsightsPane();
  } catch (err) {
    console.error("Error loading customer:", err);
  }
}

function renderCustomerFacts(p) {
  if (!p) return;
  const custName = document.getElementById("custName");
  const custBranch = document.getElementById("custBranch");
  const custAccountType = document.getElementById("custAccountType");
  const custAccount = document.getElementById("custAccount");
  const custBalance = document.getElementById("custBalance");
  const custMobile = document.getElementById("custMobile");

  const primaryAcc = p.accounts?.[0];

  if (custName) custName.textContent = p.customer_name || "—";
  const authUserName = document.getElementById("authUserName");
  if (authUserName && p.customer_name) authUserName.textContent = p.customer_name;

  // Update authenticated session bar
  const sessionCustomerName = document.getElementById("sessionCustomerName");
  const sessionAccountNumber = document.getElementById("sessionAccountNumber");
  const sessionBranchName = document.getElementById("sessionBranchName");
  if (sessionCustomerName) sessionCustomerName.textContent = p.customer_name || "—";
  if (sessionAccountNumber) sessionAccountNumber.textContent = primaryAcc?.account_number || "—";
  if (sessionBranchName) sessionBranchName.textContent = p.contact?.home_branch || "Connaught Place, Delhi";

  if (custBranch) custBranch.textContent = p.contact?.home_branch || "Connaught Place, Delhi";
  if (custAccountType) custAccountType.textContent = primaryAcc?.account_type || "Advantage Savings";
  if (custAccount) custAccount.textContent = primaryAcc?.account_number || "AC-5002938491";
  if (custBalance) custBalance.textContent = primaryAcc ? `₹${primaryAcc.balance_inr.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : "₹0.00";
  if (custMobile) custMobile.textContent = p.contact?.registered_mobile || p.contact?.phone || "+91-98112-34567";
}

function renderTicketsPane() {
  const container = document.getElementById("ticketsListContainer");
  if (!container) return;
  container.innerHTML = "";

  if (currentMode === "banking") {
    const tickets = currentCustomerData?.profile?.support_tickets || [];
    if (tickets.length === 0) {
      container.innerHTML = `
        <div class="ticket-item-card">
          <div class="ticket-item-title">No Open Disputes</div>
          <p class="ticket-item-notes">Account in verified good standing. No pending tickets logged.</p>
        </div>
      `;
      return;
    }

    tickets.forEach((t) => {
      const card = document.createElement("div");
      card.className = "ticket-item-card";
      card.innerHTML = `
        <div class="ticket-item-header">
          <span class="mono">${t.ticket_id}</span>
          <span class="badge-pill ${t.status === 'OPEN' ? 'badge-orange' : 'badge-green'}">${t.status}</span>
        </div>
        <div class="ticket-item-title">${t.subject}</div>
        <p class="ticket-item-notes">${t.resolution_notes || 'Under automated processing'}</p>
      `;
      container.appendChild(card);
    });

  } else {
    // Haq Saathi Mode
    container.innerHTML = `
      <div class="ticket-item-card">
        <div class="ticket-item-header">
          <span class="mono">${currentHaqComplaintId || 'GRV-TEL-2026-901'}</span>
          <span class="badge-pill badge-green">READY</span>
        </div>
        <div class="ticket-item-title">Wage Recovery & Labour Grievance</div>
        <p class="ticket-item-notes">Routed to Telangana Labour Commissionerate under Payment of Wages Act.</p>
      </div>
    `;
  }
}

function renderInsightsPane() {
  const container = document.getElementById("insightsListContainer");
  if (!container) return;
  container.innerHTML = "";

  if (currentMode === "banking") {
    const insights = currentCustomerData?.memory_bank?.reflection_insights || [
      "Frequent digital banking user; prefer automated self-service.",
      "Eligible for pre-approved MSME interest subvention scheme.",
      "Internal Risk Level: TIER-1 Standard."
    ];

    insights.forEach((insight, idx) => {
      const card = document.createElement("div");
      card.className = "insight-item-card";
      card.innerHTML = `
        <div class="insight-item-header">
          <span>Hindsight Reflection #${idx + 1}</span>
          <span class="badge-pill badge-blue">Verified</span>
        </div>
        <p class="insight-item-notes">${insight}</p>
      `;
      container.appendChild(card);
    });

  } else {
    // Haq Saathi Mode
    const legalRights = [
      { title: "Timely Wage Payment", desc: "Wages must be cleared within 7 to 10 days of wage period (Payment of Wages Act, 1936)." },
      { title: "Statutory Minimum Wage", desc: "No worker can be paid below government declared floor rate (Code on Wages, 2019)." },
      { title: "BOCW Accident Relief", desc: "Immediate medical aid and welfare compensation for construction site injuries." }
    ];

    legalRights.forEach((r) => {
      const card = document.createElement("div");
      card.className = "insight-item-card";
      card.innerHTML = `
        <div class="insight-item-header">
          <span>${r.title}</span>
          <span class="badge-pill badge-green">Statutory</span>
        </div>
        <p class="insight-item-notes">${r.desc}</p>
      `;
      container.appendChild(card);
    });
  }
}


// ============================================================================
// Worker Loader (Haq Saathi)
// ============================================================================
function loadHaqWorker(workerId) {
  const w = HAQ_WORKERS[workerId] || HAQ_WORKERS["WRK-201"];
  const haqWorkerName = document.getElementById("haqWorkerName");
  const haqTrade = document.getElementById("haqTrade");
  const haqAmount = document.getElementById("haqAmount");
  const haqEmployer = document.getElementById("haqEmployer");
  const haqDistrict = document.getElementById("haqDistrict");
  const haqRightCiting = document.getElementById("haqRightCiting");

  if (haqWorkerName) haqWorkerName.textContent = w.name;
  if (haqTrade) haqTrade.textContent = w.trade;
  if (haqAmount) haqAmount.textContent = w.amount;
  if (haqEmployer) haqEmployer.textContent = w.employer;
  if (haqDistrict) haqDistrict.textContent = w.district;
  if (haqRightCiting) haqRightCiting.textContent = w.right;

  selectedLanguage = w.lang;
  const languageSelect = document.getElementById("languageSelect");
  if (languageSelect) languageSelect.value = w.lang;
}

function resetHaqConversation() {
  clearChatUI();
  addHaqWelcomeBubble();
  updateHaqInspectorState("GREETING", 0, "UNDERSTAND_PROBLEM");
}

function addHaqWelcomeBubble() {
  addSystemBubble(
    "<strong>హక్ సాథీ:</strong> మేము మీ వేతన లేదా లేబర్ సమస్యను మాత్రమే నమోదు చేస్తాము. ఆధార్ కార్డు, బ్యాంక్ వివరాలు ఎప్పటికీ అడగము. మీ సమస్యను మైక్ ద్వారా చెప్పండి లేదా సమస్య బటన్ నొక్కండి."
  );
}


// ============================================================================
// Scenarios Execution
// ============================================================================
function updateScenarioButtonHighlight(btnId) {
  document.querySelectorAll(".chip-scenario").forEach((b) => b.classList.remove("active"));
  if (btnId) {
    document.getElementById(btnId)?.classList.add("active");
  }
}

function triggerBankingScenario(cid, btnId, userQuery, lang = "en-IN") {
  updateScenarioButtonHighlight(btnId);
  currentCustomerId = cid;
  const customerSelect = document.getElementById("customerSelect");
  if (customerSelect) customerSelect.value = cid;
  loadCustomer(cid).then(() => {
    sendMessage(userQuery, "text", lang);
  });
}

async function runHaqDemoScenario(scenarioId, btnId, workerId) {
  updateScenarioButtonHighlight(btnId);
  currentHaqWorkerId = workerId;
  const haqWorkerSelect = document.getElementById("haqWorkerSelect");
  if (haqWorkerSelect) haqWorkerSelect.value = workerId;
  loadHaqWorker(workerId);

  try {
    const res = await fetch("/api/haq/scenarios");
    const scenarios = await res.json();
    const sc = scenarios.find((s) => s.id === scenarioId);
    if (!sc) return;

    resetHaqConversation();

    // Step 1: Initial problem
    await sendHaqMessage(sc.initial_problem);

    // Step 2 & 3: Follow-ups
    if (sc.steps && sc.steps.length > 0) {
      setTimeout(async () => {
        const step2 = sc.steps[1] ? sc.steps[1].user_text : sc.steps[0].user_text;
        await sendHaqMessage(step2);

        setTimeout(async () => {
          const step3 = sc.steps[sc.steps.length - 1].user_text;
          await sendHaqMessage(step3);
        }, 2200);
      }, 2000);
    }
  } catch (err) {
    console.error("Haq scenario error:", err);
  }
}

function triggerHaqQuickProblem(issue) {
  const phrasings = {
    unpaid_wages: {
      "te-IN": "గత మూడు నెలలుగా యజమాని జీతం ఇవ్వలేదు, మొత్తం 18000 రూపాయలు బాకీ ఉంది.",
      "hi-IN": "नियोक्ता ने पिछले कई महीनों से मेरा वेतन नहीं दिया है, पगार रोकी गई है।",
      "ur-IN": "مالک نے پچھلے چند مہینوں سے اجرت نہیں دی ہے، تنخواہ رکی ہوئی ہے۔",
      "en-IN": "My employer has withheld my salary for the past few months."
    },
    below_minimum_wage: {
      "te-IN": "నాకు ప్రభుత్వం నిర్ణయించిన కనీస వేతనం కంటే చాలా తక్కువ కూలి ఇస్తున్నారు.",
      "hi-IN": "मुझे सरकारी न्यूनतम मजदूरी से बहुत कम वेतन दिया जा रहा है।",
      "ur-IN": "مجھے حکومت کی مقررہ کم از کم اجرت سے بہت کم معاوضہ دیا جا رہا ہے۔",
      "en-IN": "I am being paid below the statutory minimum wage."
    },
    workplace_injury: {
      "te-IN": "పనిలో ప్రమాదం జరిగి గాయమైంది, యజమాని వైద్య ఖర్చులు లేదా పరిహారం ఇవ్వడం లేదు.",
      "hi-IN": "काम करते हुए गंभीर चोट लगी है, ठेकेदार इलाज का खर्च नहीं दे रहा।",
      "ur-IN": "کام کے دوران چوٹ لگی ہے، ٹھیکیدار علاج اور معاوضہ نہیں دے رہا ہے۔",
      "en-IN": "I had a workplace injury and the employer refused medical compensation."
    },
    no_pf_or_benefits: {
      "te-IN": "నేను అసంఘటిత కార్మికుడిని, సంక్షేమ బోర్డు లేదా పీఎఫ్ రక్షణ లభించడం లేదు.",
      "hi-IN": "मैं निर्माण या गिग वर्कर हूँ, मुझे पीएफ या कल्याण बोर्ड का लाभ नहीं मिल रहा।",
      "ur-IN": "میں کنسٹرکشن ورکر ہوں، مجھے ویلفیئر فنڈ کی سہولت نہیں مل رہی۔",
      "en-IN": "I am an informal worker and need BOCW welfare benefits."
    }
  };

  const lang = selectedLanguage !== "auto" ? selectedLanguage : "te-IN";
  const text = phrasings[issue]?.[lang] || phrasings[issue]?.["te-IN"] || "జీతం బాకీ సమస్య";
  sendMessage(text, "text");
}


// ============================================================================
// Message Routing & Execution
// ============================================================================
async function sendMessage(text, channel = "text", language = "auto") {
  if (currentMode === "haq") {
    await sendHaqMessage(text, channel);
  } else {
    await sendBankingMessage(text, channel, language);
  }
}

// Banking Assistant Messaging
async function sendBankingMessage(text, channel = "text", language = "auto") {
  addMessageBubble("user", text, channel);

  let effectiveLang;
  if (selectedLanguage !== "auto") {
    effectiveLang = selectedLanguage;
  } else if (language !== "auto" && language !== "en-IN") {
    effectiveLang = language;
  } else {
    effectiveLang = detectScriptLanguage(text);
  }

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

      if (isAutoTtsEnabled() && voiceRes.tts?.synthesized_text) {
        speakResponse(voiceRes.tts.synthesized_text, voiceRes.tts.language);
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

      if (isAutoTtsEnabled() && payload.response) {
        speakResponse(payload.response, payload.detected_language);
      }
    }

    lastSpokenText = payload.response;

    const isEscalated = payload.is_escalated;
    const respLang = payload.detected_language || effectiveLang;

    // Check if customer query talks about unpaid labour wages
    const wageSignals = ["salary", "wage", "contractor", "labour", "wages", "కూలి", "జీతం", "మజదూరి", "వేతనం"];
    const mentionsWage = wageSignals.some((s) => text.toLowerCase().includes(s));

    addMessageBubble("agent", payload.response, channel, isEscalated, respLang, mentionsWage);
    updateBankingInspector(payload);
    loadCustomer(currentCustomerId);

  } catch (err) {
    console.error("Banking send error:", err);
    addMessageBubble("agent", "An error occurred connecting to the banking orchestrator.");
  }
}

// Haq Saathi Messaging
async function sendHaqMessage(text, channel = "text") {
  addMessageBubble("user", text, channel);

  let lang = selectedLanguage !== "auto" ? selectedLanguage : "te-IN";

  try {
    const res = await fetch("/api/haq/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: haqSessionId,
        user_text: text,
        language: lang
      })
    });

    const data = await res.json();

    // Check danger signals
    if (data.danger_flag) {
      const dangerModal = document.getElementById("dangerModal");
      if (dangerModal) dangerModal.style.display = "flex";
      addMessageBubble("agent", data.reply_text, channel, true, lang);
      speakResponse(data.reply_text, lang);
      return;
    }

    lastSpokenText = data.reply_text;

    // Render response bubble
    addMessageBubble("agent", data.reply_text, channel, false, data.reply_language || lang);

    // Auto-speak response
    if (isAutoTtsEnabled() && data.reply_text) {
      speakResponse(data.reply_text, data.reply_language || lang);
    }

    // Render suggested option chips
    renderHaqSuggestedChips(data.suggested_options);

    // Update Legal Inspector
    updateHaqInspector(data);

  } catch (err) {
    console.error("Haq Saathi API error:", err);
    addMessageBubble("agent", "సర్వర్ కనెక్ట్ కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.");
  }
}


// ============================================================================
// Inspector Updates
// ============================================================================
function updateBankingInspector(payload) {
  const esc = payload.escalation || {};
  const isEsc = payload.is_escalated;

  const escBadge = document.getElementById("escBadge");
  const escRule = document.getElementById("escRule");
  const escDept = document.getElementById("escDept");
  const approvedPills = document.getElementById("approvedPills");
  const blockedPills = document.getElementById("blockedPills");
  const memoryTimeline = document.getElementById("memoryTimeline");

  if (escBadge) {
    if (isEsc) {
      escBadge.textContent = "ESCALATED";
      escBadge.className = "badge-pill badge-orange";
    } else {
      escBadge.textContent = "AUTONOMOUS";
      escBadge.className = "badge-pill badge-green";
    }
  }

  if (escRule) escRule.textContent = isEsc ? (esc.rule_id ? `${esc.rule_id}: ${esc.rule_name}` : "Triggered") : "None (Safe for AI)";
  if (escDept) escDept.textContent = isEsc ? (esc.department || "Human Support Desk") : "—";

  // Entity Whitelist Pills (green pill tag like loan_id in screenshot)
  if (approvedPills) {
    approvedPills.innerHTML = "";
    const allowed = payload.data_whitelist?.allowed_fields_surfaced || ["loan_id", "customer_name", "account_number"];
    allowed.forEach((f) => {
      const span = document.createElement("span");
      span.className = "pill-tag pill-green";
      span.textContent = f;
      approvedPills.appendChild(span);
    });
  }

  // Blocked Fields Pills
  if (blockedPills) {
    blockedPills.innerHTML = "";
    const blocked = payload.data_whitelist?.blocked_internal_fields || ["cibil_score", "internal_risk"];
    blocked.forEach((f) => {
      const span = document.createElement("span");
      span.className = "pill-tag pill-red";
      span.textContent = f;
      blockedPills.appendChild(span);
    });
  }

  // Memory timeline
  if (memoryTimeline) {
    memoryTimeline.innerHTML = `
      <div class="timeline-row">
        <span class="bullet-dot"></span>
        <span class="timeline-text">Recall(): Verified facts &amp; accounts</span>
      </div>
      <div class="timeline-row">
        <span class="bullet-dot green"></span>
        <span class="timeline-text">Reflect(): Active guardrail checks passed</span>
      </div>
    `;
  }
}

function updateHaqInspector(data) {
  const state = data.current_state || "UNDERSTAND_PROBLEM";
  const haqCurrentState = document.getElementById("haqCurrentState");
  const haqStateBadge = document.getElementById("haqStateBadge");
  const haqQuestionCount = document.getElementById("haqQuestionCount");
  const haqProgressFill = document.getElementById("haqProgressFill");
  const haqOfficeName = document.getElementById("haqOfficeName");
  const haqOfficeAddress = document.getElementById("haqOfficeAddress");
  const haqJurisdictionBadge = document.getElementById("haqJurisdictionBadge");
  const haqCallOfficeBtn = document.getElementById("haqCallOfficeBtn");
  const haqCallBtnLabel = document.getElementById("haqCallBtnLabel");
  const haqPdfStatusBadge = document.getElementById("haqPdfStatusBadge");

  if (haqCurrentState) haqCurrentState.textContent = state;
  if (haqStateBadge) haqStateBadge.textContent = state;

  const stateProgressMap = {
    "GREETING": 15,
    "UNDERSTAND_PROBLEM": 35,
    "COLLECT_FIELDS": 60,
    "EXPLAIN_RIGHTS": 80,
    "CONFIRM": 90,
    "GENERATE_COMPLAINT": 95,
    "ROUTE": 100,
    "DONE": 100
  };
  if (haqProgressFill) haqProgressFill.style.width = (stateProgressMap[state] || 35) + "%";

  if (haqQuestionCount) {
    haqQuestionCount.textContent = `${data.question_count || 1} / 4 (Strict Max)`;
  }

  // Rights
  if (data.rights_summary) {
    currentHaqRights = data.rights_summary;
  }

  // Routed Labour Office
  if (data.office_details) {
    if (haqOfficeName) haqOfficeName.textContent = data.office_details.office_name;
    if (haqOfficeAddress) haqOfficeAddress.textContent = data.office_details.address;
    if (haqJurisdictionBadge) haqJurisdictionBadge.textContent = data.office_details.district;
    if (haqCallOfficeBtn) haqCallOfficeBtn.href = `tel:${data.office_details.phone.replace(/[^0-9]/g, '')}`;
    if (haqCallBtnLabel) haqCallBtnLabel.textContent = `📞 Call Office (${data.office_details.phone})`;
  }

  // Complaint ID & PDF
  if (data.complaint_id) {
    currentHaqComplaintId = data.complaint_id;
    if (haqPdfStatusBadge) haqPdfStatusBadge.textContent = "READY";
  }

  // Checklist
  if (data.checklist && data.checklist.length > 0) {
    renderHaqChecklist(data.checklist);
  }
}

function updateHaqInspectorState(state, count, nextStep) {
  const haqCurrentState = document.getElementById("haqCurrentState");
  const haqStateBadge = document.getElementById("haqStateBadge");
  const haqQuestionCount = document.getElementById("haqQuestionCount");
  if (haqCurrentState) haqCurrentState.textContent = state;
  if (haqStateBadge) haqStateBadge.textContent = state;
  if (haqQuestionCount) haqQuestionCount.textContent = `${count} / 4 (Strict Max)`;
}

function renderHaqSuggestedChips(options) {
  const container = document.getElementById("suggestedChipsContainer");
  const modalContainer = document.getElementById("modalQuickOptions");

  if (!container && !modalContainer) return;

  if (container) container.innerHTML = "";
  if (modalContainer) modalContainer.innerHTML = "";

  if (!options || options.length === 0) {
    if (container) container.style.display = "none";
    if (modalContainer) modalContainer.style.display = "none";
    return;
  }

  if (container) container.style.display = "flex";
  if (modalContainer) modalContainer.style.display = "flex";

  options.forEach((opt) => {
    // Inline card chip
    if (container) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chip-scenario";
      btn.textContent = opt;
      btn.onclick = () => sendMessage(opt, "text");
      container.appendChild(btn);
    }

    // Modal chip
    if (modalContainer) {
      const mBtn = document.createElement("button");
      mBtn.type = "button";
      mBtn.className = "chip-scenario";
      mBtn.textContent = opt;
      mBtn.onclick = () => sendMessage(opt, "text");
      modalContainer.appendChild(mBtn);
    }
  });
}

function renderHaqChecklist(checklist) {
  const container = document.getElementById("haqChecklistTimeline");
  if (!container) return;
  container.innerHTML = "";

  checklist.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "timeline-row";
    row.innerHTML = `
      <span class="bullet-dot ${index > 1 ? 'green' : 'orange'}">${item.icon || (index + 1)}</span>
      <span class="timeline-text"><strong>${item.title}:</strong> ${item.desc}</span>
    `;
    container.appendChild(row);
  });
}

function showWhyModal() {
  const whyModal = document.getElementById("whyModal");
  const whyModalContent = document.getElementById("whyModalContent");
  if (!whyModal) return;

  if (currentHaqRights && whyModalContent) {
    whyModalContent.innerHTML = `
      <p><strong>చట్టం పేరు:</strong> ${currentHaqRights.title || 'Payment of Wages Act, 1936'}</p>
      <p><strong>అధికార యంత్రాంగం:</strong> ${currentHaqRights.authority || 'Telangana Labour Commissionerate'}</p>
      <p><strong>అధికారిక మూలం:</strong> ${currentHaqRights.source_name || 'Ministry of Labour & Employment'}</p>
      <p><strong>సులభ వివరణ:</strong> ${currentHaqRights.plain_explanation || 'వేతన కాలపరిమితి ముగిసిన వెంటనే పూర్తి జీతం చెల్లించాలి.'}</p>
      <p style="font-size:0.75rem; color:var(--text-dim); margin-top:8px;">ధృవీకరించబడిన మూలం: \`haq_saathi/knowledge/rights.json\`. ఏ కల్పిత చట్టాలు లేవు.</p>
    `;
  }
  whyModal.style.display = "flex";
}


// ============================================================================
// Shared Chat UI Rendering (Inline Panel + Pop-Up Modal Synchronized)
// ============================================================================
function addMessageBubble(sender, text, channel = "text", isEscalated = false, lang = "en-IN", showHaqLink = false) {
  const chatMessages = document.getElementById("chatMessages");
  const modalChatMessages = document.getElementById("modalChatMessages");

  // Remove empty placeholder message
  const emptyPlaceholder = document.getElementById("conversationEmptyText");
  if (emptyPlaceholder) emptyPlaceholder.parentElement?.remove();

  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // 1. Render in Inline Conversation Panel
  if (chatMessages) {
    const bubble = createBubbleElement(sender, text, channel, isEscalated, lang, showHaqLink, timeStr);
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // 2. Render in Pop-Up Modal
  if (modalChatMessages) {
    const modalBubble = createModalBubbleElement(sender, text, channel, isEscalated, lang, timeStr);
    modalChatMessages.appendChild(modalBubble);
    modalChatMessages.scrollTop = modalChatMessages.scrollHeight;
  }
}

function createBubbleElement(sender, text, channel, isEscalated, lang, showHaqLink, timeStr) {
  const bubble = document.createElement("div");
  bubble.className = `message-bubble ${sender}-bubble ${isEscalated ? 'escalated-bubble' : ''}`;

  const header = document.createElement("div");
  header.className = "bubble-header";

  const senderTag = document.createElement("span");
  senderTag.textContent = sender === "user" ? "You" : (currentMode === "haq" ? "Haq Saathi ⚖️" : "AI Assistant");
  header.appendChild(senderTag);

  const metaTag = document.createElement("span");
  metaTag.className = "bubble-time";
  metaTag.textContent = `${timeStr} • ${lang}`;
  header.appendChild(metaTag);

  bubble.appendChild(header);

  const content = document.createElement("p");
  content.textContent = text;
  bubble.appendChild(content);

  if (showHaqLink) {
    const linkBtn = document.createElement("button");
    linkBtn.type = "button";
    linkBtn.className = "service-switch-tab";
    linkBtn.style.marginTop = "8px";
    linkBtn.style.display = "inline-block";
    linkBtn.innerHTML = "⚖️ Switch to Haq Saathi to draft Wage-Theft Complaint PDF";
    linkBtn.onclick = () => setMode("haq");
    bubble.appendChild(linkBtn);
  }

  return bubble;
}

function createModalBubbleElement(sender, text, channel, isEscalated, lang, timeStr) {
  const bubble = document.createElement("div");
  bubble.className = `modal-bubble ${sender}`;

  const p = document.createElement("p");
  p.textContent = text;
  bubble.appendChild(p);

  return bubble;
}

function addSystemBubble(htmlText) {
  const chatMessages = document.getElementById("chatMessages");
  const modalChatMessages = document.getElementById("modalChatMessages");

  if (chatMessages) {
    const bubble = document.createElement("div");
    bubble.className = "message-bubble agent-bubble";
    bubble.style.borderLeft = "3px solid var(--accent-blue)";
    bubble.innerHTML = `<p>${htmlText}</p>`;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  if (modalChatMessages) {
    const mBubble = document.createElement("div");
    mBubble.className = "modal-bubble agent";
    mBubble.innerHTML = `<p>${htmlText}</p>`;
    modalChatMessages.appendChild(mBubble);
    modalChatMessages.scrollTop = modalChatMessages.scrollHeight;
  }
}

function clearChatUI() {
  const chatMessages = document.getElementById("chatMessages");
  const modalChatMessages = document.getElementById("modalChatMessages");
  if (chatMessages) chatMessages.innerHTML = "";
  if (modalChatMessages) modalChatMessages.innerHTML = "";
}


// ============================================================================
// Web Speech API: STT & TTS
// ============================================================================
function isAutoTtsEnabled() {
  const ttsToggle = document.getElementById("ttsToggle");
  return ttsToggle ? ttsToggle.checked : true;
}

function detectScriptLanguage(text) {
  if (!text) return "en-IN";
  if (/[\u0C00-\u0C7F]/.test(text)) return "te-IN"; // Telugu
  if (/[\u0600-\u06FF]/.test(text)) return "ur-IN"; // Urdu
  if (/[\u0B80-\u0BFF]/.test(text)) return "ta-IN"; // Tamil
  if (/[\u0900-\u097F]/.test(text)) return "hi-IN"; // Hindi
  return "en-IN";
}

function loadBrowserVoices() {
  if ('speechSynthesis' in window) {
    availableVoices = window.speechSynthesis.getVoices();
  }
}
if ('speechSynthesis' in window && window.speechSynthesis.onvoiceschanged !== undefined) {
  window.speechSynthesis.onvoiceschanged = loadBrowserVoices;
}

function getBestVoiceForLanguage(targetLang) {
  if (!availableVoices || availableVoices.length === 0) {
    availableVoices = window.speechSynthesis.getVoices();
  }
  const langLower = (targetLang || "en-IN").toLowerCase();
  const langPrefix = langLower.split("-")[0];

  let match = availableVoices.find((v) => v.lang.toLowerCase() === langLower || v.lang.toLowerCase().replace("_", "-") === langLower);
  if (match) return match;

  match = availableVoices.find((v) => v.lang.toLowerCase().startsWith(langPrefix));
  if (match) return match;

  return null;
}

function speakResponse(text, lang = "en-IN") {
  if (!('speechSynthesis' in window) || !text) return;
  window.speechSynthesis.cancel();

  const voiceActivityBar = document.getElementById("voiceActivityBar");
  const voiceStatusText = document.getElementById("voiceStatusText");

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = 0.95;

  const voice = getBestVoiceForLanguage(lang);
  if (voice) utterance.voice = voice;

  utterance.onstart = () => {
    voiceActivityBar?.classList.add("active");
    if (voiceStatusText) voiceStatusText.textContent = "Speaking response aloud...";
  };

  utterance.onend = utterance.onerror = () => {
    voiceActivityBar?.classList.remove("active");
    if (voiceStatusText) voiceStatusText.textContent = "Voice ready";
  };

  window.speechSynthesis.speak(utterance);
}

function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;

  const micBtn = document.getElementById("micBtn");
  const modalMicBtn = document.getElementById("modalMicBtn");
  const voiceActivityBar = document.getElementById("voiceActivityBar");
  const voiceStatusText = document.getElementById("voiceStatusText");

  recognition.onstart = () => {
    isListening = true;
    micBtn?.classList.add("listening");
    modalMicBtn?.classList.add("listening");
    voiceActivityBar?.classList.add("active");
    if (voiceStatusText) voiceStatusText.textContent = "Listening to speech...";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    if (voiceStatusText) voiceStatusText.textContent = `Transcribed: "${transcript}"`;
    sendMessage(transcript, "voice", recognition.lang);
  };

  recognition.onerror = () => stopListening();
  recognition.onend = () => stopListening();
}

function toggleSpeechInput() {
  if (!recognition) {
    alert("Web Speech API recognition is not supported in this browser. Please use Chrome/Edge or type your message.");
    return;
  }

  if (isListening) {
    recognition.stop();
    stopListening();
  } else {
    const lang = selectedLanguage !== "auto" ? selectedLanguage : (currentMode === "haq" ? "te-IN" : "en-IN");
    recognition.lang = lang;
    recognition.start();
  }
}

function stopListening() {
  isListening = false;
  document.getElementById("micBtn")?.classList.remove("listening");
  document.getElementById("modalMicBtn")?.classList.remove("listening");
  document.getElementById("voiceActivityBar")?.classList.remove("active");
  const voiceStatusText = document.getElementById("voiceStatusText");
  if (voiceStatusText) voiceStatusText.textContent = "Voice ready";
}

/**
 * Haq Saathi - Frontend Application Controller
 * Handles Web Speech STT/TTS, Multilingual Localization, Chat UI,
 * Workflow State, PDF Downloads, and 1-Click Judge Demo Scenarios.
 */

// Localized strings dictionary for instant UI updates
const I18N = {
  "te-IN": {
    brandTitle: "హక్ సాథీ",
    brandSub: "Haq Saathi",
    brandTagline: "కార్మికుల వాయిస్ లీగల్ సహచరుడు • Voice Rights Companion",
    demoBtnLabel: "డెమో సినారియోలు",
    consentText: "గోప్యతా హామీ: హక్ సాథీ మీ లేబర్ సమస్యను మాత్రమే నమోదు చేస్తుంది. మేము ఆధార్ కార్డు, బ్యాంక్ వివరాలు లేదా వ్యక్తిగత చిరునామా అడగము.",
    whyBtnLabel: "ఎందుకు ఈ సమాధానం? (Why this?)",
    step1: "సమస్య",
    step2: "వివరాలు",
    step3: "హక్కులు",
    step4: "ఫిర్యాదు",
    step5: "లేబర్ ఆఫీస్",
    langSelectTitle: "భాషను ఎంచుకోండి / Select Language:",
    quickHint: "లేదా కింద ఉన్న సమస్యను నేరుగా తాకండి:",
    cardTitle1: "జీతం రాలేదు",
    cardSub1: "నెలల తరబడి బాకీ లేదా ఆలస్యం",
    cardTitle2: "తక్కువ కూలి",
    cardSub2: "కనీస వేతనం కంటే తక్కువ చెల్లింపు",
    cardTitle3: "పనిలో గాయం",
    cardSub3: "ప్రమాద పరిహారం & వైద్య ఖర్చులు",
    cardTitle4: "పీఎఫ్ & ప్రయోజనాలు",
    cardSub4: "సంక్షేమ బోర్డు లేదా పీఎఫ్ రక్షణ",
    micCaptionIdle: "నొక్కండి మరియు మాట్లాడండి (Tap & Speak)",
    micCaptionListening: "వింటున్నాము... దయచేసి మాట్లాడండి (Listening...)",
    micCaptionSpeaking: "సమాధానం చదువుతున్నాము... (Speaking...)",
    replayText: "మళ్లీ వినండి (Replay)",
    chatTitle: "లైవ్ సంభాషణ (Live Transcript)",
    inputPlaceholder: "లేదా మీ సమస్యను ఇక్కడ టైప్ చేయండి...",
    welcome: "నమస్కారం! నేను హక్ సాథీ. మీ పని లేదా జీతానికి సంబంధించిన సమస్య ఏమిటి? చెప్పండి, నేను మీకు చట్టపరమైన సహాయం అందిస్తాను.",
    downloadBtnLabel: "ఫిర్యాదు పత్రం (తెలుగు PDF)",
    checklistHeading: "తదుపరి ఏమి చేయాలి? (Next Steps)",
    callOfficePrefix: "లేబర్ ఆఫీస్‌కు కాల్ చేయండి"
  },
  "hi-IN": {
    brandTitle: "हक़ साथी",
    brandSub: "Haq Saathi",
    brandTagline: "श्रमिकों का वॉयस कानूनी साथी • Voice Rights Companion",
    demoBtnLabel: "डेमो परिदृश्य",
    consentText: "गोपनीयता सुरक्षा: हक़ साथी केवल आपकी श्रम समस्या दर्ज करता है। हम आधार, बैंक खाता या व्यक्तिगत पता कभी नहीं मांगते।",
    whyBtnLabel: "यह उत्तर क्यों? (Why this?)",
    step1: "समस्या",
    step2: "विवरण",
    step3: "अधिकार",
    step4: "शिकायत",
    step5: "श्रम कार्यालय",
    langSelectTitle: "भाषा चुनें / Select Language:",
    quickHint: "या नीचे दी गई समस्या पर सीधे टैप करें:",
    cardTitle1: "वेतन नहीं मिला",
    cardSub1: "महीनों का बकाया या मजदूरी रोकी गई",
    cardTitle2: "कम मजदूरी",
    cardSub2: "तय न्यूनतम वेतन से कम भुगतान",
    cardTitle3: "काम पर चोट",
    cardSub3: "दुर्घटना मुआवजा और इलाज खर्च",
    cardTitle4: "पीएफ और लाभ",
    cardSub4: "कल्याण बोर्ड या पीएफ सुरक्षा",
    micCaptionIdle: "माइक दबाएं और बोलें (Tap & Speak)",
    micCaptionListening: "सुन रहे हैं... कृपया बोलिए (Listening...)",
    micCaptionSpeaking: "उत्तर पढ़ रहे हैं... (Speaking...)",
    replayText: "फिर से सुनें (Replay)",
    chatTitle: "बातचीत का विवरण (Live Transcript)",
    inputPlaceholder: "या अपनी समस्या यहाँ लिखें...",
    welcome: "नमस्ते! मैं हक़ साथी हूँ। आपके काम या मजदूरी से जुड़ी क्या समस्या है? बोलकर बताएं, मैं आपकी कानूनी मदद करूंगा।",
    downloadBtnLabel: "शिकायत पत्र (हिन्दी PDF)",
    checklistHeading: "आगे क्या करना है? (Next Steps)",
    callOfficePrefix: "श्रम कार्यालय में कॉल करें"
  },
  "ur-IN": {
    brandTitle: "حق ساتھی",
    brandSub: "Haq Saathi",
    brandTagline: "مزدوروں کا صوتی قانونی ساتھی • Voice Rights Companion",
    demoBtnLabel: "ڈیمو منظرنامے",
    consentText: "رازداری کی ضمانت: حق ساتھی صرف آپ کا لیبر مسئلہ درج کرتا ہے۔ ہم آدھار کارڈ، بینک اکاؤنٹ یا نجی پتہ نہیں مانگتے۔",
    whyBtnLabel: "یہ جواب کیوں؟ (Why this?)",
    step1: "مسئلہ",
    step2: "تفصیلات",
    step3: "حقوق",
    step4: "شکایت",
    step5: "لیبر آفس",
    langSelectTitle: "زبان منتخب کریں / Select Language:",
    quickHint: "یا نیچے دیے گئے مسئلے پر براہ راست کلک کریں:",
    cardTitle1: "اجرت نہیں ملی",
    cardSub1: "مہینوں کا بقایا یا رکی ہوئی اجرت",
    cardTitle2: "کم اجرت",
    cardSub2: "مقررہ کم از کم اجرت سے کم ادائیگی",
    cardTitle3: "کام پر چوٹ",
    cardSub3: "حادثاتی معاوضہ اور طبی اخراجات",
    cardTitle4: "پی ایف اور فوائد",
    cardSub4: "ویلئفیر بورڈ یا پی ایف کا تحفظ",
    micCaptionIdle: "مائیک دبائیں اور بولیں (Tap & Speak)",
    micCaptionListening: "سن رہے ہیں... براہ کرم بولیں (Listening...)",
    micCaptionSpeaking: "جواب پڑھا جا رہا ہے... (Speaking...)",
    replayText: "دوبارہ سنیں (Replay)",
    chatTitle: "براہ راست گفتگو (Live Transcript)",
    inputPlaceholder: "یا اپنا مسئلہ یہاں لکھیں...",
    welcome: "سلام علیکم! میں حق ساتھی ہوں۔ آپ کے کام یا اجرت سے متعلق کیا مسئلہ ہے؟ بول کر بتائیں، میں آپ کی قانونی مدد کروں گا۔",
    downloadBtnLabel: "شکایت کا خط (اردو PDF)",
    checklistHeading: "آگے کیا کرنا ہے؟ (Next Steps)",
    callOfficePrefix: "لیبر آفس کو کال کریں"
  },
  "en-IN": {
    brandTitle: "Haq Saathi",
    brandSub: "హక్ సాథీ / हक़ साथी",
    brandTagline: "Voice-First Legal Rights Companion for Informal Workers",
    demoBtnLabel: "Demo Scenarios",
    consentText: "Privacy guarantee: Haq Saathi collects only your work issue to draft a labour complaint. We never ask for Aadhaar or bank details.",
    whyBtnLabel: "Why this answer? (Source)",
    step1: "Problem",
    step2: "Details",
    step3: "Rights",
    step4: "Complaint",
    step5: "Labour Office",
    langSelectTitle: "Select Language:",
    quickHint: "Or tap a common issue directly below:",
    cardTitle1: "Salary Unpaid",
    cardSub1: "Withheld or delayed wages over months",
    cardTitle2: "Low Wages",
    cardSub2: "Paid below statutory minimum wage",
    cardTitle3: "Injury at Work",
    cardSub3: "Workplace accident compensation & bills",
    cardTitle4: "PF & Welfare",
    cardSub4: "BOCW registration & social security",
    micCaptionIdle: "Tap & Speak your problem",
    micCaptionListening: "Listening... Please speak now",
    micCaptionSpeaking: "Speaking response aloud...",
    replayText: "Replay Audio",
    chatTitle: "Live Transcript",
    inputPlaceholder: "Or type your problem here...",
    welcome: "Hello! I am Haq Saathi. What issue are you facing with your work or wages? Speak aloud, and I will assist you with your legal rights.",
    downloadBtnLabel: "Download Petition (PDF)",
    checklistHeading: "What Happens Next? (Next Steps)",
    callOfficePrefix: "Call Labour Office"
  }
};

class HaqSaathiApp {
  constructor() {
    this.sessionId = "hs_" + Math.random().toString(36).substring(2, 10);
    this.currentLang = "te-IN";
    this.soundEnabled = true;
    this.isListening = false;
    this.isSpeaking = false;
    this.lastSpokenText = "";
    this.currentComplaintId = null;
    this.currentRights = null;
    this.recognition = null;
    this.synthesis = window.speechSynthesis || null;

    this.initElements();
    this.initSpeechRecognition();
    this.bindEvents();
    this.setLanguage(this.currentLang);
  }

  initElements() {
    this.dom = {
      body: document.body,
      brandTitle: document.getElementById("brandTitle"),
      brandTagline: document.getElementById("brandTagline"),
      consentText: document.getElementById("consentText"),
      whyAnswerBtn: document.getElementById("whyAnswerBtn"),
      demoBtn: document.getElementById("demoBtn"),
      demoMenu: document.getElementById("demoMenu"),
      soundToggleBtn: document.getElementById("soundToggleBtn"),
      soundIcon: document.getElementById("soundIcon"),
      resetSessionBtn: document.getElementById("resetSessionBtn"),
      progressFill: document.getElementById("progressFill"),
      stepNodes: document.querySelectorAll(".step-node"),
      stepLabel1: document.getElementById("stepLabel1"),
      stepLabel2: document.getElementById("stepLabel2"),
      stepLabel3: document.getElementById("stepLabel3"),
      stepLabel4: document.getElementById("stepLabel4"),
      stepLabel5: document.getElementById("stepLabel5"),
      langChips: document.querySelectorAll(".lang-chip"),
      langSelectTitle: document.getElementById("langSelectTitle"),
      quickCardsHint: document.getElementById("quickCardsHint"),
      problemCards: document.querySelectorAll(".card-problem"),
      cardTitle1: document.getElementById("cardTitle1"),
      cardSub1: document.getElementById("cardSub1"),
      cardTitle2: document.getElementById("cardTitle2"),
      cardSub2: document.getElementById("cardSub2"),
      cardTitle3: document.getElementById("cardTitle3"),
      cardSub3: document.getElementById("cardSub3"),
      cardTitle4: document.getElementById("cardTitle4"),
      cardSub4: document.getElementById("cardSub4"),
      voiceCenterpiece: document.querySelector(".voice-centerpiece"),
      micBtn: document.getElementById("micBtn"),
      micCaption: document.getElementById("micCaption"),
      audioBars: document.getElementById("audioBars"),
      replayBtn: document.getElementById("replayBtn"),
      replayText: document.getElementById("replayText"),
      chatTitle: document.getElementById("chatTitle"),
      chatBox: document.getElementById("chatBox"),
      welcomeGreeting: document.getElementById("welcomeGreeting"),
      suggestedChipsContainer: document.getElementById("suggestedChipsContainer"),
      manualInput: document.getElementById("manualInput"),
      sendBtn: document.getElementById("sendBtn"),
      resultSection: document.getElementById("resultSection"),
      rightsCard: document.getElementById("rightsCard"),
      rightsLawTitle: document.getElementById("rightsLawTitle"),
      rightsAuthority: document.getElementById("rightsAuthority"),
      rightsExplanation: document.getElementById("rightsExplanation"),
      rightsDisclaimer: document.getElementById("rightsDisclaimer"),
      complaintCard: document.getElementById("complaintCard"),
      displayComplaintId: document.getElementById("displayComplaintId"),
      downloadLocalPdfBtn: document.getElementById("downloadLocalPdfBtn"),
      downloadBtnLabel: document.getElementById("downloadBtnLabel"),
      downloadEngPdfBtn: document.getElementById("downloadEngPdfBtn"),
      officeCard: document.getElementById("officeCard"),
      officeName: document.getElementById("officeName"),
      officeJurisdiction: document.getElementById("officeJurisdiction"),
      officeAddress: document.getElementById("officeAddress"),
      officeHours: document.getElementById("officeHours"),
      officeCallBtn: document.getElementById("officeCallBtn"),
      callOfficeLabel: document.getElementById("callOfficeLabel"),
      checklistHeading: document.getElementById("checklistHeading"),
      checklistGrid: document.getElementById("checklistGrid"),
      dangerModal: document.getElementById("dangerModal"),
      closeDangerBtn: document.getElementById("closeDangerBtn"),
      whyModal: document.getElementById("whyModal"),
      closeWhyBtn: document.getElementById("closeWhyBtn"),
      whyModalContent: document.getElementById("whyModalContent")
    };
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = this.currentLang;

      this.recognition.onstart = () => {
        this.isListening = true;
        this.dom.voiceCenterpiece.classList.add("listening");
        this.dom.micCaption.textContent = I18N[this.currentLang].micCaptionListening;
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript && transcript.trim()) {
          this.handleUserMessage(transcript);
        }
      };

      this.recognition.onerror = (event) => {
        console.warn("[STT Error]", event.error);
        this.stopListening();
        if (event.error === "not-allowed") {
          this.showNotice("మైక్రోఫోన్ అనుమతి నిరాకరించబడింది. దయచేసి కింద టైప్ చేయండి.", "Microphone access denied.");
        }
      };

      this.recognition.onend = () => {
        this.stopListening();
      };
    } else {
      console.warn("Web SpeechRecognition is not supported on this browser.");
    }
  }

  bindEvents() {
    // Mic Button
    this.dom.micBtn.addEventListener("click", () => {
      this.toggleSpeechRecognition();
    });

    // Language Chips
    this.dom.langChips.forEach(chip => {
      chip.addEventListener("click", () => {
        const lang = chip.getAttribute("data-lang");
        this.setLanguage(lang);
      });
    });

    // Quick Problem Cards (1-Tap)
    this.dom.problemCards.forEach(card => {
      card.addEventListener("click", () => {
        const issue = card.getAttribute("data-issue");
        this.handleQuickProblem(issue);
      });
    });

    // Manual Input Send
    this.dom.sendBtn.addEventListener("click", () => {
      this.sendManualInput();
    });
    this.dom.manualInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        this.sendManualInput();
      }
    });

    // Sound Toggle
    this.dom.soundToggleBtn.addEventListener("click", () => {
      this.soundEnabled = !this.soundEnabled;
      this.dom.soundIcon.textContent = this.soundEnabled ? "🔊" : "🔇";
      if (!this.soundEnabled && this.synthesis) {
        this.synthesis.cancel();
      }
    });

    // Replay Spoken Audio
    this.dom.replayBtn.addEventListener("click", () => {
      if (this.lastSpokenText) {
        this.speakText(this.lastSpokenText);
      }
    });

    // Reset Session
    this.dom.resetSessionBtn.addEventListener("click", () => {
      this.resetSession();
    });

    // Demo Scenarios Menu Toggle
    this.dom.demoBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      this.dom.demoMenu.classList.toggle("hidden");
    });
    document.addEventListener("click", () => {
      this.dom.demoMenu.classList.add("hidden");
    });

    // Demo Scenarios Item Click
    document.querySelectorAll(".demo-item").forEach(item => {
      item.addEventListener("click", (e) => {
        e.stopPropagation();
        const scId = item.getAttribute("data-scenario");
        this.runDemoScenario(scId);
        this.dom.demoMenu.classList.add("hidden");
      });
    });

    // "Why this answer?" Modal
    this.dom.whyAnswerBtn.addEventListener("click", () => {
      this.showWhyAnswerModal();
    });
    this.dom.closeWhyBtn.addEventListener("click", () => {
      this.dom.whyModal.classList.add("hidden");
    });

    // Danger Modal Close
    this.dom.closeDangerBtn.addEventListener("click", () => {
      this.dom.dangerModal.classList.add("hidden");
    });

    // PDF Download handlers
    this.dom.downloadLocalPdfBtn.addEventListener("click", () => {
      if (this.currentComplaintId) {
        window.open(`/api/complaint/${this.currentComplaintId}/pdf?lang=${this.currentLang}`, "_blank");
      }
    });
    this.dom.downloadEngPdfBtn.addEventListener("click", () => {
      if (this.currentComplaintId) {
        window.open(`/api/complaint/${this.currentComplaintId}/pdf?lang=en-IN`, "_blank");
      }
    });

    // Global helper for initial welcome play
    window.speakWelcome = () => {
      const text = I18N[this.currentLang].welcome;
      this.speakText(text);
    };
  }

  setLanguage(lang) {
    this.currentLang = lang;
    const str = I18N[lang] || I18N["te-IN"];

    // Update Body Script Class
    this.dom.body.className = "lang-" + lang.substring(0, 2);

    // Update Active Language Chip
    this.dom.langChips.forEach(chip => {
      chip.classList.toggle("active", chip.getAttribute("data-lang") === lang);
    });

    // Update Text Content across UI
    this.dom.brandTitle.innerHTML = `${str.brandTitle} <span class="brand-sub">${str.brandSub}</span>`;
    this.dom.brandTagline.textContent = str.brandTagline;
    this.dom.demoBtn.querySelector(".label").textContent = str.demoBtnLabel;
    this.dom.consentText.textContent = str.consentText;
    this.dom.whyAnswerBtn.textContent = str.whyBtnLabel;
    this.dom.stepLabel1.textContent = str.step1;
    this.dom.stepLabel2.textContent = str.step2;
    this.dom.stepLabel3.textContent = str.step3;
    this.dom.stepLabel4.textContent = str.step4;
    this.dom.stepLabel5.textContent = str.step5;
    this.dom.langSelectTitle.textContent = str.langSelectTitle;
    this.dom.quickCardsHint.textContent = str.quickHint;
    this.dom.cardTitle1.textContent = str.cardTitle1;
    this.dom.cardSub1.textContent = str.cardSub1;
    this.dom.cardTitle2.textContent = str.cardTitle2;
    this.dom.cardSub2.textContent = str.cardSub2;
    this.dom.cardTitle3.textContent = str.cardTitle3;
    this.dom.cardSub3.textContent = str.cardSub3;
    this.dom.cardTitle4.textContent = str.cardTitle4;
    this.dom.cardSub4.textContent = str.cardSub4;
    this.dom.micCaption.textContent = this.isListening ? str.micCaptionListening : str.micCaptionIdle;
    this.dom.replayText.textContent = str.replayText;
    this.dom.chatTitle.textContent = str.chatTitle;
    this.dom.manualInput.placeholder = str.inputPlaceholder;
    this.dom.welcomeGreeting.textContent = str.welcome;
    this.dom.downloadBtnLabel.textContent = str.downloadBtnLabel;
    this.dom.checklistHeading.textContent = str.checklistHeading;

    // Update Speech Recognition Language
    if (this.recognition) {
      this.recognition.lang = lang;
    }

    this.lastSpokenText = str.welcome;
  }

  toggleSpeechRecognition() {
    if (!this.recognition) {
      alert("వాయిస్ రికగ్నిషన్ ఈ బ్రౌజర్‌లో అందుబాటులో లేదు. దయచేసి కింద టైప్ చేయండి లేదా క్రోమ్ బ్రౌజర్ ఉపయోగించండి.");
      return;
    }

    if (this.isListening) {
      this.recognition.stop();
    } else {
      if (this.synthesis) {
        this.synthesis.cancel();
      }
      try {
        this.recognition.start();
      } catch (err) {
        console.warn("STT Start Error", err);
      }
    }
  }

  stopListening() {
    this.isListening = false;
    this.dom.voiceCenterpiece.classList.remove("listening");
    const str = I18N[this.currentLang] || I18N["te-IN"];
    this.dom.micCaption.textContent = str.micCaptionIdle;
  }

  speakText(text) {
    if (!this.soundEnabled || !this.synthesis || !text) return;

    this.synthesis.cancel(); // Cancel any ongoing speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = this.currentLang;
    utterance.rate = 0.95; // Slightly slower for crisp informal worker comprehension

    // Pick best matching voice
    const voices = this.synthesis.getVoices();
    const prefix = this.currentLang.substring(0, 2);
    const matchingVoice = voices.find(v => v.lang.startsWith(prefix));
    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.dom.voiceCenterpiece.classList.add("speaking");
      const str = I18N[this.currentLang] || I18N["te-IN"];
      this.dom.micCaption.textContent = str.micCaptionSpeaking;
      this.dom.replayBtn.classList.remove("hidden");
    };

    utterance.onend = utterance.onerror = () => {
      this.isSpeaking = false;
      this.dom.voiceCenterpiece.classList.remove("speaking");
      const str = I18N[this.currentLang] || I18N["te-IN"];
      this.dom.micCaption.textContent = str.micCaptionIdle;
    };

    this.synthesis.speak(utterance);
    this.lastSpokenText = text;
  }

  handleQuickProblem(issue) {
    const phrasings = {
      unpaid_wages: {
        "te-IN": "నమస్కారం, గత కొన్ని నెలలుగా నా యజమాని జీతం ఇవ్వలేదు, వేతనం నిలిపివేశారు.",
        "hi-IN": "नमस्ते, कई महीनों से नियोक्ता ने मेरा वेतन नहीं दिया है, मजदूरी रुकी हुई है।",
        "ur-IN": "سلام علیکم، پچھلے چند مہینوں سے مالک نے میری اجرت نہیں دی ہے، تنخواہ رکی ہوئی ہے۔",
        "en-IN": "Hello, my employer has not paid my wages for the past few months."
      },
      below_minimum_wage: {
        "te-IN": "నాకు ప్రభుత్వం నిర్ణయించిన కనీస వేతనం కంటే చాలా తక్కువ కూలి ఇస్తున్నారు.",
        "hi-IN": "मुझे सरकारी न्यूनतम मजदूरी से बहुत कम वेतन दिया जा रहा है।",
        "ur-IN": "مجھے حکومت کی مقررہ کم از کم اجرت سے بہت کم معاوضہ دیا جا رہا ہے۔",
        "en-IN": "I am being paid far below the statutory minimum wage."
      },
      workplace_injury: {
        "te-IN": "పనిలో ప్రమాదం జరిగి గాయమైంది, యజమాని వైద్య ఖర్చులు లేదా పరిహారం ఇవ్వడం లేదు.",
        "hi-IN": "कार्यस्थल पर काम करते हुए चोट लगी है, नियोक्ता इलाज का खर्च या मुआवजा नहीं दे रहा।",
        "ur-IN": "کام کے دوران چوٹ لگی ہے، ٹھیکیدار علاج کے اخراجات یا معاوضہ نہیں دے رہا ہے۔",
        "en-IN": "I had a workplace injury and the employer is refusing medical compensation."
      },
      no_pf_or_benefits: {
        "te-IN": "నేను నిర్మాణ లేదా గిగ్ వర్కర్‌గా పని చేస్తున్నాను, పీఎఫ్ లేదా సంక్షేమ రక్షణ లభించడం లేదు.",
        "hi-IN": "मैं निर्माण या गिग वर्कर हूँ, मुझे पीएफ या कल्याण बोर्ड का लाभ नहीं मिल रहा।",
        "ur-IN": "میں کنسٹرکشن یا پلیٹ فارم ورکر ہوں، مجھے پی ایف یا ویلفیئر فنڈ کی سہولت نہیں مل رہی۔",
        "en-IN": "I am an informal worker and not getting PF or welfare board registration."
      }
    };

    const text = phrasings[issue][this.currentLang] || phrasings[issue]["te-IN"];
    this.handleUserMessage(text);
  }

  sendManualInput() {
    const text = this.dom.manualInput.value.trim();
    if (text) {
      this.dom.manualInput.value = "";
      this.handleUserMessage(text);
    }
  }

  async handleUserMessage(userText) {
    // 1. Add User bubble to transcript
    this.appendMessage("user", userText);

    // 2. Call backend /api/chat
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: this.sessionId,
          user_text: userText,
          language: this.currentLang
        })
      });

      if (!response.ok) {
        throw new Error("API response error: " + response.status);
      }

      const data = await response.json();
      this.handleApiResponse(data);

    } catch (err) {
      console.error("[Chat Error]", err);
      const fallbackMsg = "సర్వర్ కనెక్ట్ కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి లేదా మైక్ నొక్కండి.";
      this.appendMessage("bot", fallbackMsg);
      this.speakText(fallbackMsg);
    }
  }

  handleApiResponse(data) {
    // Check danger signal override
    if (data.danger_flag) {
      this.dom.dangerModal.classList.remove("hidden");
      this.appendMessage("bot", data.reply_text);
      this.speakText(data.reply_text);
      return;
    }

    // 1. Add Bot message
    this.appendMessage("bot", data.reply_text);

    // 2. Speak reply aloud (under 40 words, friendly tone)
    this.speakText(data.reply_text);

    // 3. Update suggested chips
    this.renderSuggestedChips(data.suggested_options);

    // 4. Update workflow progress bar
    this.updateProgress(data.current_state);

    // 5. Store current rights
    if (data.rights_summary) {
      this.currentRights = data.rights_summary;
      this.renderRightsCard(data.rights_summary);
    }

    // 6. Handle complaint generation & office routing
    if (data.complaint_id) {
      this.currentComplaintId = data.complaint_id;
      this.dom.resultSection.classList.remove("hidden");
      this.dom.displayComplaintId.textContent = data.complaint_id;

      if (data.office_details) {
        this.renderOfficeCard(data.office_details);
      }
      if (data.checklist) {
        this.renderChecklist(data.checklist);
      }
    }
  }

  appendMessage(sender, text) {
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${sender}-message`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = sender === "user" ? "👤" : "⚖️";

    const content = document.createElement("div");
    content.className = "message-content";

    const p = document.createElement("p");
    p.textContent = text;
    content.appendChild(p);

    const footer = document.createElement("div");
    footer.className = "msg-footer";

    const time = document.createElement("span");
    time.className = "msg-time";
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    footer.appendChild(time);

    if (sender === "bot") {
      const playBtn = document.createElement("button");
      playBtn.className = "btn-mini-play";
      playBtn.textContent = "🔊 వినండి";
      playBtn.onclick = () => this.speakText(text);
      footer.appendChild(playBtn);
    }

    content.appendChild(footer);
    bubble.appendChild(avatar);
    bubble.appendChild(content);

    this.dom.chatBox.appendChild(bubble);
    this.dom.chatBox.scrollTop = this.dom.chatBox.scrollHeight;
  }

  renderSuggestedChips(options) {
    this.dom.suggestedChipsContainer.innerHTML = "";
    if (!options || options.length === 0) return;

    options.forEach(opt => {
      const btn = document.createElement("button");
      btn.className = "chip-option";
      btn.textContent = opt;
      btn.onclick = () => {
        this.handleUserMessage(opt);
      };
      this.dom.suggestedChipsContainer.appendChild(btn);
    });
  }

  updateProgress(state) {
    const stateStepMap = {
      "GREETING": 1,
      "UNDERSTAND_PROBLEM": 1,
      "COLLECT_FIELDS": 2,
      "EXPLAIN_RIGHTS": 3,
      "CONFIRM": 4,
      "GENERATE_COMPLAINT": 4,
      "ROUTE": 5,
      "DONE": 5
    };

    const stepNum = stateStepMap[state] || 1;
    const percentage = (stepNum / 5) * 100;
    this.dom.progressFill.style.width = percentage + "%";

    this.dom.stepNodes.forEach(node => {
      const nodeStep = parseInt(node.getAttribute("data-step"));
      node.classList.remove("active", "completed");
      if (nodeStep === stepNum) {
        node.classList.add("active");
      } else if (nodeStep < stepNum) {
        node.classList.add("completed");
      }
    });
  }

  renderRightsCard(rights) {
    this.dom.rightsLawTitle.textContent = rights.title || "చట్టబద్ధమైన హక్కు";
    this.dom.rightsAuthority.textContent = rights.authority || "అధికారిక రక్షణ";
    this.dom.rightsExplanation.textContent = rights.plain_explanation || "";
    this.dom.rightsDisclaimer.textContent = rights.disclaimer_note || "గమనిక: ఇది అధికారిక నిబంధన. నిర్ధారణ కోసం లేబర్ కార్యాలయాన్ని సంప్రదించండి.";
  }

  renderOfficeCard(office) {
    this.dom.officeName.textContent = office.office_name;
    this.dom.officeJurisdiction.textContent = `పరిధి / Jurisdiction: ${office.jurisdiction}`;
    this.dom.officeAddress.textContent = office.address;
    this.dom.officeHours.textContent = office.working_hours;
    this.dom.officeCallBtn.href = `tel:${office.phone.replace(/[^0-9]/g, '')}`;
    const str = I18N[this.currentLang] || I18N["te-IN"];
    this.dom.callOfficeLabel.textContent = `${str.callOfficePrefix} (${office.phone})`;
  }

  renderChecklist(checklist) {
    this.dom.checklistGrid.innerHTML = "";
    checklist.forEach(item => {
      const card = document.createElement("div");
      card.className = "checklist-item";

      const badge = document.createElement("div");
      badge.className = "checklist-step-badge";
      badge.textContent = item.icon || item.step;

      const content = document.createElement("div");
      content.className = "checklist-content";

      const title = document.createElement("strong");
      title.textContent = item.title;

      const desc = document.createElement("p");
      desc.textContent = item.desc;

      content.appendChild(title);
      content.appendChild(desc);
      card.appendChild(badge);
      card.appendChild(content);

      this.dom.checklistGrid.appendChild(card);
    });
  }

  showWhyAnswerModal() {
    if (!this.currentRights) {
      this.dom.whyModalContent.innerHTML = `
        <p><strong>అధికారిక ఆధారం:</strong> భారత కార్మిక సంక్షేమ మరియు వేతన చట్టాలు (Payment of Wages Act, Minimum Wages Act, BOCW Act 1996).</p>
        <p><strong>ధృవీకరణ నియమం:</strong> మా జ్ఞాన భాండాగారం (\`knowledge/rights.json\`) అధికారిక ప్రభుత్వ గెజిట్ మార్గదర్శకాల ఆధారంగా రూపొందించబడింది.</p>
        <p class="source-tag">గమనిక: ఏ చట్టబద్ధమైన సెక్షన్ నంబర్లు లేదా రూపాయి సంఖ్యలు కల్పితం కావు.</p>
      `;
    } else {
      this.dom.whyModalContent.innerHTML = `
        <p><strong>చట్టం పేరు (Topic):</strong> ${this.currentRights.title}</p>
        <p><strong>అధికార యంత్రాంగం (Authority):</strong> ${this.currentRights.authority}</p>
        <p><strong>మూలం (Official Source):</strong> ${this.currentRights.source_name}</p>
        <p><strong>సులభ వివరణ:</strong> ${this.currentRights.plain_explanation}</p>
        <p><strong>ధృవీకరించబడిన తేదీ:</strong> ${this.currentRights.last_verified_date || "2026-03-01"}</p>
        <p class="source-tag">ప్రత్యేక గమనిక: ${this.currentRights.disclaimer_note || "అధికారిక ఉపయోగం ముందు లేబర్ కార్యాలయంలో నిర్ధారించుకోండి."}</p>
      `;
    }
    this.dom.whyModal.classList.remove("hidden");
  }

  async runDemoScenario(scId) {
    try {
      const res = await fetch("/api/scenarios");
      const scenarios = await res.json();
      const sc = scenarios.find(s => s.id === scId);
      if (!sc) return;

      // 1. Reset Session
      this.resetSession();

      // 2. Set Language
      this.setLanguage(sc.language);

      // 3. Run Step 1
      this.appendMessage("user", sc.initial_problem);

      const turn1 = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: this.sessionId,
          user_text: sc.initial_problem,
          language: sc.language
        })
      });
      const data1 = await turn1.json();
      this.handleApiResponse(data1);

      // Automated follow-up step execution for seamless hackathon live demonstration
      if (sc.steps && sc.steps.length > 0) {
        setTimeout(async () => {
          const step2Text = sc.steps[1] ? sc.steps[1].user_text : sc.steps[0].user_text;
          this.appendMessage("user", step2Text);

          const turn2 = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              session_id: this.sessionId,
              user_text: step2Text,
              language: sc.language
            })
          });
          const data2 = await turn2.json();
          this.handleApiResponse(data2);

          // Final step: Confirm complaint generation
          setTimeout(async () => {
            const finalStepText = sc.steps[sc.steps.length - 1].user_text;
            this.appendMessage("user", finalStepText);

            const turn3 = await fetch("/api/chat", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                session_id: this.sessionId,
                user_text: finalStepText,
                language: sc.language
              })
            });
            const data3 = await turn3.json();
            this.handleApiResponse(data3);
          }, 2400);

        }, 2200);
      }

    } catch (e) {
      console.error("[Demo Error]", e);
    }
  }

  resetSession() {
    this.sessionId = "hs_" + Math.random().toString(36).substring(2, 10);
    this.currentComplaintId = null;
    this.currentRights = null;
    this.dom.chatBox.innerHTML = "";
    this.dom.suggestedChipsContainer.innerHTML = "";
    this.dom.resultSection.classList.add("hidden");
    this.dom.replayBtn.classList.add("hidden");
    if (this.synthesis) this.synthesis.cancel();

    // Re-add initial bot welcome message
    const str = I18N[this.currentLang] || I18N["te-IN"];
    const bubble = document.createElement("div");
    bubble.className = "message-bubble bot-message";
    bubble.innerHTML = `
      <div class="avatar">⚖️</div>
      <div class="message-content">
        <p>${str.welcome}</p>
        <div class="msg-footer">
          <span class="msg-time">ఇప్పుడే</span>
          <button class="btn-mini-play" onclick="window.speakWelcome()">🔊 వినండి</button>
        </div>
      </div>
    `;
    this.dom.chatBox.appendChild(bubble);
    this.updateProgress("GREETING");
  }

  showNotice(msg) {
    alert(msg);
  }
}

// Bootstrap on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  window.haqApp = new HaqSaathiApp();
});

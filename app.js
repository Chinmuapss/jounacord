import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { SUPABASE_URL, SUPABASE_ANON_KEY } from "./config.js";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const authCard = document.getElementById("auth-card");
const appCard = document.getElementById("app-card");
const authForm = document.getElementById("auth-form");
const statusText = document.getElementById("status");
const logoutBtn = document.getElementById("logout");
const welcome = document.getElementById("welcome");

const recordBtn = document.getElementById("record");
const saveBtn = document.getElementById("save");
const transcriptEl = document.getElementById("transcript");
const translationEl = document.getElementById("translation");
const targetLangEl = document.getElementById("target-lang");
const historyEl = document.getElementById("history");

let currentUser = null;
let latestTranscript = "";
let latestTranslation = "";
let recognizing = false;

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

if (recognition) {
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onresult = async (event) => {
    latestTranscript = event.results[0][0].transcript.trim();
    transcriptEl.textContent = latestTranscript || "—";
    await translateLatest();
  };

  recognition.onend = () => {
    recognizing = false;
    recordBtn.textContent = "Start Recording";
  };

  recognition.onerror = (event) => {
    setStatus(`Speech recognition error: ${event.error}`);
  };
}

function setStatus(msg) {
  statusText.textContent = msg;
}

async function translateLatest() {
  if (!latestTranscript) return;
  setStatus("Translating...");
  const target = targetLangEl.value;
  const q = encodeURIComponent(latestTranscript);
  const url = `https://api.mymemory.translated.net/get?q=${q}&langpair=en|${target}`;
  const res = await fetch(url);
  const data = await res.json();
  latestTranslation = data?.responseData?.translatedText?.trim() || "";
  translationEl.textContent = latestTranslation || "(No translation returned)";
  saveBtn.disabled = !latestTranslation;
  setStatus("Translation ready. Save it to your account.");
}

function resetOutputs() {
  latestTranscript = "";
  latestTranslation = "";
  transcriptEl.textContent = "—";
  translationEl.textContent = "—";
  saveBtn.disabled = true;
}

async function loadHistory() {
  const { data, error } = await supabase
    .from("voice_entries")
    .select("id, transcript, translation, target_language, created_at")
    .order("created_at", { ascending: false });

  if (error) {
    setStatus(`Failed loading history: ${error.message}`);
    return;
  }

  historyEl.innerHTML = "";
  if (!data.length) {
    historyEl.innerHTML = "<li>No entries yet.</li>";
    return;
  }

  for (const item of data) {
    const li = document.createElement("li");
    const date = new Date(item.created_at).toLocaleString();
    li.innerHTML = `
      <strong>${item.target_language.toUpperCase()}</strong> · ${date}<br>
      <em>${item.transcript}</em><br>
      ${item.translation}
    `;
    historyEl.appendChild(li);
  }
}

async function saveEntry() {
  if (!currentUser || !latestTranscript || !latestTranslation) return;
  const payload = {
    user_id: currentUser.id,
    transcript: latestTranscript,
    translation: latestTranslation,
    target_language: targetLangEl.value,
  };

  const { error } = await supabase.from("voice_entries").insert(payload);
  if (error) {
    setStatus(`Save failed: ${error.message}`);
    return;
  }
  setStatus("Saved to your account.");
  resetOutputs();
  await loadHistory();
}

async function handleAuth(mode, email, password) {
  if (mode === "signup") {
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) throw error;
    setStatus("Sign-up successful. Check email if confirmation is enabled, then login.");
    return;
  }

  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  setStatus("Logged in.");
}

function showApp(user) {
  currentUser = user;
  authCard.classList.add("hidden");
  appCard.classList.remove("hidden");
  welcome.textContent = `Your Workspace (${user.email})`;
  loadHistory();
}

function showAuth() {
  currentUser = null;
  appCard.classList.add("hidden");
  authCard.classList.remove("hidden");
  historyEl.innerHTML = "";
  resetOutputs();
}

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const btn = event.submitter;
  const mode = btn?.dataset?.mode || "login";
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    await handleAuth(mode, email, password);
  } catch (err) {
    setStatus(err.message);
  }
});

logoutBtn.addEventListener("click", async () => {
  await supabase.auth.signOut();
  setStatus("Logged out.");
});

recordBtn.addEventListener("click", () => {
  if (!recognition) {
    setStatus("Speech recognition is not supported in this browser.");
    return;
  }

  if (recognizing) {
    recognition.stop();
    recognizing = false;
    recordBtn.textContent = "Start Recording";
    return;
  }

  resetOutputs();
  recognizing = true;
  recordBtn.textContent = "Stop Recording";
  setStatus("Listening... Speak now.");
  recognition.start();
});

saveBtn.addEventListener("click", saveEntry);
targetLangEl.addEventListener("change", () => {
  if (latestTranscript) {
    translateLatest().catch((error) => setStatus(error.message));
  }
});

supabase.auth.onAuthStateChange((_event, session) => {
  if (session?.user) {
    showApp(session.user);
  } else {
    showAuth();
  }
});

const { data } = await supabase.auth.getSession();
if (data?.session?.user) {
  showApp(data.session.user);
} else {
  showAuth();
}

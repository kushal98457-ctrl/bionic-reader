/**
 * Bionic Reader — Frontend Logic
 * Talks to the FastAPI backend at /convert, /convert/file, /convert/export.
 * All original API contracts preserved exactly.
 * New: theme switcher, reading controls, word count, improved UX.
 */

"use strict";

const API_BASE = ""; // same origin

// ─── Theme ────────────────────────────────────────────────────

const THEME_KEY = "bionic-theme";
const VALID_THEMES = ["light", "sepia", "dark"];

function applyTheme(theme) {
  if (!VALID_THEMES.includes(theme)) theme = "light";
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(THEME_KEY, theme);

  // Update active state on theme buttons
  document.querySelectorAll(".theme-btn").forEach((btn) => {
    const isActive = btn.dataset.themeSet === theme;
    btn.classList.toggle("active", isActive);
    btn.setAttribute("aria-pressed", isActive ? "true" : "false");
  });
}

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  const preferred = window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
  applyTheme(saved || preferred);
}

document.querySelectorAll(".theme-btn").forEach((btn) => {
  btn.addEventListener("click", () => applyTheme(btn.dataset.themeSet));
});

initTheme();

// ─── Help Modal ───────────────────────────────────────────────

const helpBtn   = document.getElementById("help-btn");
const helpModal = document.getElementById("help-modal");
const helpClose = document.getElementById("help-close");

function openHelp() {
  helpModal.hidden = false;
  helpModal.focus?.();
  helpClose.focus();
  document.addEventListener("keydown", onModalKey);
}

function closeHelp() {
  helpModal.hidden = true;
  document.removeEventListener("keydown", onModalKey);
  helpBtn.focus();
}

function onModalKey(e) {
  if (e.key === "Escape") closeHelp();
}

helpBtn.addEventListener("click", openHelp);
helpClose.addEventListener("click", closeHelp);
helpModal.addEventListener("click", (e) => {
  if (e.target === helpModal) closeHelp();
});

// ─── Tabs ─────────────────────────────────────────────────────

const tabBtns  = document.querySelectorAll(".tab-btn");
const tabPanels = document.querySelectorAll(".tab-panel");
let activeInputMode = "paste";

tabBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const target = btn.dataset.tab;

    tabBtns.forEach((t) => {
      t.classList.remove("active");
      t.setAttribute("aria-selected", "false");
    });
    tabPanels.forEach((p) => {
      p.classList.remove("active");
      p.hidden = true;
    });

    btn.classList.add("active");
    btn.setAttribute("aria-selected", "true");

    const panel = document.getElementById(`panel-${target}`);
    panel.classList.add("active");
    panel.hidden = false;

    activeInputMode = target;
  });
});

// ─── Word Count ───────────────────────────────────────────────

const textInput = document.getElementById("text-input");
const wordCountEl = document.getElementById("word-count");

function updateWordCount() {
  const text = textInput.value.trim();
  const count = text ? text.split(/\s+/).length : 0;
  wordCountEl.textContent = count === 1 ? "1 word" : `${count.toLocaleString()} words`;
}

textInput.addEventListener("input", updateWordCount);
updateWordCount(); // initial

// Convert on Ctrl+Enter or Cmd+Enter when textarea focused
textInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    convert();
  }
});

// ─── Dropzone ─────────────────────────────────────────────────

const dropzone         = document.getElementById("dropzone");
const fileInput        = document.getElementById("file-input");
const dropzoneIdle     = document.getElementById("dropzone-idle");
const dropzoneSelected = document.getElementById("dropzone-selected");
const dropzoneFilename = document.getElementById("dropzone-filename");
const dropzoneMeta     = document.getElementById("dropzone-meta");
const fileRemoveBtn    = document.getElementById("file-remove");
let selectedFile = null;

function setSelectedFile(file) {
  selectedFile = file;

  const ext = file.name.split(".").pop().toUpperCase();
  const sizeMB = (file.size / 1024 / 1024).toFixed(2);

  dropzoneFilename.textContent = file.name;
  dropzoneMeta.textContent = `${ext} · ${sizeMB} MB`;

  dropzoneIdle.hidden = true;
  dropzoneSelected.hidden = false;
}

function clearSelectedFile() {
  selectedFile = null;
  fileInput.value = "";
  dropzoneIdle.hidden = false;
  dropzoneSelected.hidden = true;
  dropzoneFilename.textContent = "";
  dropzoneMeta.textContent = "";
}

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) setSelectedFile(fileInput.files[0]);
});

fileRemoveBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  clearSelectedFile();
});

["dragover", "dragenter"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  })
);

["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
  })
);

dropzone.addEventListener("drop", (e) => {
  if (e.dataTransfer.files.length) setSelectedFile(e.dataTransfer.files[0]);
});

// ─── Strength Slider ──────────────────────────────────────────

const slider        = document.getElementById("strength-slider");
const strengthName  = document.getElementById("strength-name");
const strengthValue = document.getElementById("strength-value");
const strengthPrev  = document.getElementById("strength-preview");

function nameForRatio(pct) {
  if (pct <= 32) return "LOW";
  if (pct <= 45) return "MEDIUM";
  if (pct <= 55) return "HIGH";
  return "MAX";
}

// Client-side mirror for the instant preview — backend does the real conversion.
function previewBionicWord(word, ratio) {
  const len = word.length;
  if (len < 3) return `<strong>${word.slice(0, 1)}</strong>${word.slice(1)}`;
  let bold = Math.ceil(len * ratio);
  bold = Math.min(bold, 6);
  bold = Math.max(bold, 1);
  if (bold >= len) bold = len - 1;
  return `<strong>${word.slice(0, bold)}</strong>${word.slice(bold)}`;
}

function updateSliderFill(pct) {
  const min = Number(slider.min);
  const max = Number(slider.max);
  const fraction = ((pct - min) / (max - min)) * 100;
  slider.style.setProperty("--slider-pct", `${fraction.toFixed(2)}%`);
  // Also update CSS on :root for the track gradient
  document.documentElement.style.setProperty("--slider-pct", `${fraction.toFixed(2)}%`);
}

function renderPreview() {
  const pct = Number(slider.value);
  const ratio = pct / 100;

  strengthName.textContent = nameForRatio(pct);
  strengthValue.textContent = `${pct}%`;

  slider.setAttribute("aria-valuenow", pct);
  slider.setAttribute("aria-valuetext", `${nameForRatio(pct)}, ${pct}%`);

  updateSliderFill(pct);

  const sample = "Reading faster becomes automatic once your eyes learn the pattern.";
  const html = sample
    .split(" ")
    .map((w) => previewBionicWord(w, ratio))
    .join(" ");
  strengthPrev.innerHTML = html;
}

slider.addEventListener("input", renderPreview);
renderPreview(); // initial

// ─── Reading Controls (front-end only) ────────────────────────

const output = document.getElementById("output");

const FONT_SIZES    = [15, 17, 19, 21, 24];
const LINE_SPACINGS = [1.55, 1.75, 1.95, 2.15];
const MAX_WIDTHS    = [520, 680, 840];
const WIDTH_IDS     = ["width-narrow", "width-normal", "width-wide"];

let fontIdx    = 1; // 17px
let spacingIdx = 1; // 1.75
let widthIdx   = 1; // 680px

function applyReadingSettings() {
  document.documentElement.style.setProperty("--output-font-size",   `${FONT_SIZES[fontIdx]}px`);
  document.documentElement.style.setProperty("--output-line-height", `${LINE_SPACINGS[spacingIdx]}`);
  document.documentElement.style.setProperty("--output-max-width",   `${MAX_WIDTHS[widthIdx]}px`);
}

function setWidthActive(idx) {
  WIDTH_IDS.forEach((id, i) => {
    const btn = document.getElementById(id);
    btn.classList.toggle("active", i === idx);
    btn.setAttribute("aria-pressed", i === idx ? "true" : "false");
  });
}

document.getElementById("font-decrease").addEventListener("click", () => {
  if (fontIdx > 0) { fontIdx--; applyReadingSettings(); }
});
document.getElementById("font-increase").addEventListener("click", () => {
  if (fontIdx < FONT_SIZES.length - 1) { fontIdx++; applyReadingSettings(); }
});

document.getElementById("spacing-decrease").addEventListener("click", () => {
  if (spacingIdx > 0) { spacingIdx--; applyReadingSettings(); }
});
document.getElementById("spacing-increase").addEventListener("click", () => {
  if (spacingIdx < LINE_SPACINGS.length - 1) { spacingIdx++; applyReadingSettings(); }
});

document.getElementById("width-narrow").addEventListener("click", () => {
  widthIdx = 0; applyReadingSettings(); setWidthActive(0);
});
document.getElementById("width-normal").addEventListener("click", () => {
  widthIdx = 1; applyReadingSettings(); setWidthActive(1);
});
document.getElementById("width-wide").addEventListener("click", () => {
  widthIdx = 2; applyReadingSettings(); setWidthActive(2);
});

applyReadingSettings();
setWidthActive(widthIdx);

// ─── Status ───────────────────────────────────────────────────

const statusEl = document.getElementById("status");

function setStatus(message, type = "info") {
  // type: "info" | "error" | "success"
  statusEl.textContent = message;
  statusEl.classList.remove("error", "success");
  if (type === "error")   statusEl.classList.add("error");
  if (type === "success") statusEl.classList.add("success");
}

function clearStatus() {
  statusEl.textContent = "";
  statusEl.classList.remove("error", "success");
}

// ─── Convert ──────────────────────────────────────────────────

const convertBtn = document.getElementById("convert-btn");
const outputEmpty = document.getElementById("output-empty");

async function convert() {
  const strength = Number(slider.value) / 100;

  convertBtn.disabled = true;
  convertBtn.classList.add("loading");
  setStatus("Converting…");

  try {
    let html;

    if (activeInputMode === "upload") {
      if (!selectedFile) {
        setStatus("Choose a file first.", "error");
        return;
      }
      const form = new FormData();
      form.append("file", selectedFile);
      form.append("strength", strength);

      const res = await fetch(`${API_BASE}/convert/file`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Server error ${res.status}`);
      }
      html = (await res.json()).html;
    } else {
      const text = textInput.value;
      if (!text.trim()) {
        setStatus("Enter some text first.", "error");
        return;
      }
      const res = await fetch(`${API_BASE}/convert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, strength }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Server error ${res.status}`);
      }
      html = (await res.json()).html;
    }

    // Inject output
    if (outputEmpty) outputEmpty.remove();
    output.innerHTML = html || "<p class=\"output-placeholder\">Nothing to show — try a longer text.</p>";

    // Fade-in
    output.classList.remove("appeared");
    // Force reflow
    void output.offsetWidth;
    output.classList.add("appeared");

    setStatus("Converted successfully.", "success");

    // Auto-clear success message after 3s
    setTimeout(() => {
      if (statusEl.classList.contains("success")) clearStatus();
    }, 3000);

  } catch (err) {
    const friendly = friendlyError(err.message);
    setStatus(friendly, "error");
  } finally {
    convertBtn.disabled = false;
    convertBtn.classList.remove("loading");
  }
}

convertBtn.addEventListener("click", convert);

function friendlyError(msg) {
  if (!msg) return "Something went wrong. Please try again.";
  if (msg.toLowerCase().includes("network") || msg.toLowerCase().includes("fetch"))
    return "Network error — is the server running?";
  if (msg.toLowerCase().includes("413"))
    return "File is too large.";
  if (msg.toLowerCase().includes("unsupported file"))
    return msg; // pass through the backend's friendly message
  return msg;
}

// ─── Copy ─────────────────────────────────────────────────────

const copyBtn = document.getElementById("copy-btn");
const copyLabel = copyBtn.querySelector(".copy-label");

copyBtn.addEventListener("click", async () => {
  const text = output.innerText || output.textContent;
  if (!text || text === "Your bionic reading output will appear here.") {
    setStatus("Nothing to copy — convert first.", "error");
    return;
  }

  try {
    // Try rich copy (HTML) for paste-into-Word fidelity
    if (navigator.clipboard && window.ClipboardItem) {
      const htmlBlob = new Blob([output.innerHTML], { type: "text/html" });
      const textBlob = new Blob([text], { type: "text/plain" });
      await navigator.clipboard.write([
        new ClipboardItem({ "text/html": htmlBlob, "text/plain": textBlob }),
      ]);
    } else {
      await navigator.clipboard.writeText(text);
    }
    copyLabel.textContent = "Copied ✓";
    copyBtn.classList.add("copied");
    copyBtn.setAttribute("aria-label", "Copied to clipboard");
    setTimeout(() => {
      copyLabel.textContent = "Copy";
      copyBtn.classList.remove("copied");
      copyBtn.setAttribute("aria-label", "Copy bionic output to clipboard");
    }, 2200);
  } catch {
    setStatus("Copy failed — please select and copy manually.", "error");
  }
});

// ─── Export ───────────────────────────────────────────────────

document.querySelectorAll(".export-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const format   = btn.dataset.format;
    const strength = Number(slider.value) / 100;

    btn.disabled = true;
    btn.classList.add("loading");
    setStatus(`Exporting .${format}…`);

    try {
      const form = new FormData();
      form.append("format", format);
      form.append("strength", strength);

      if (activeInputMode === "upload") {
        if (!selectedFile) {
          setStatus("Choose a file first.", "error");
          return;
        }
        form.append("file", selectedFile);
      } else {
        const text = textInput.value;
        if (!text.trim()) {
          setStatus("Enter some text first.", "error");
          return;
        }
        form.append("text", text);
      }

      const res = await fetch(`${API_BASE}/convert/export`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Export failed");
      }

      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `bionic_output.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      setStatus(`Exported as .${format.toUpperCase()}.`, "success");
      setTimeout(() => {
        if (statusEl.classList.contains("success")) clearStatus();
      }, 3000);

    } catch (err) {
      setStatus(err.message || "Export failed — please try again.", "error");
    } finally {
      btn.disabled = false;
      btn.classList.remove("loading");
    }
  });
});

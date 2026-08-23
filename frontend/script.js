// Bionic Reader — frontend logic
// Talks to the FastAPI backend at /convert, /convert/file, /convert/export.

const API_BASE = ""; // same origin

// ---------- Tabs ----------
const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".tab-panel");
let activeInputMode = "paste";

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    panels.forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    const name = tab.dataset.tab;
    document.querySelector(`.tab-panel[data-panel="${name}"]`).classList.add("active");
    activeInputMode = name;
  });
});

// ---------- Dropzone ----------
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const dropzoneFilename = document.getElementById("dropzone-filename");
let selectedFile = null;

dropzone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) setSelectedFile(fileInput.files[0]);
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

function setSelectedFile(file) {
  selectedFile = file;
  dropzoneFilename.textContent = file.name;
}

// ---------- Strength slider ----------
const slider = document.getElementById("strength-slider");
const strengthName = document.getElementById("strength-name");
const strengthValue = document.getElementById("strength-value");
const strengthPreview = document.getElementById("strength-preview");

function nameForRatio(pct) {
  if (pct <= 32) return "LOW";
  if (pct <= 45) return "MEDIUM";
  if (pct <= 55) return "HIGH";
  return "MAX";
}

// Lightweight client-side mirror of the server's rule, just for the
// instant live preview — the real conversion always goes through the
// backend so behavior (URLs, numbers, hyphens, punctuation) matches exactly.
function previewBionicWord(word, ratio) {
  const len = word.length;
  if (len < 3) return `<strong>${word.slice(0, 1)}</strong>${word.slice(1)}`;
  let bold = Math.ceil(len * ratio);
  bold = Math.min(bold, 6);
  bold = Math.max(bold, 1);
  if (bold >= len) bold = len - 1;
  return `<strong>${word.slice(0, bold)}</strong>${word.slice(bold)}`;
}

function renderPreview() {
  const pct = Number(slider.value);
  const ratio = pct / 100;
  strengthName.textContent = nameForRatio(pct);
  strengthValue.textContent = `${pct}%`;
  const sample = "Reading faster becomes automatic once your eyes learn the pattern.";
  const html = sample
    .split(" ")
    .map((w) => previewBionicWord(w, ratio))
    .join(" ");
  strengthPreview.innerHTML = html;
}

slider.addEventListener("input", renderPreview);
renderPreview();

// ---------- Convert ----------
const convertBtn = document.getElementById("convert-btn");
const outputEl = document.getElementById("output");
const statusEl = document.getElementById("status");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

async function convert() {
  const strength = Number(slider.value) / 100;
  convertBtn.disabled = true;
  setStatus("Converting…");

  try {
    let html;
    if (activeInputMode === "upload") {
      if (!selectedFile) {
        setStatus("Choose a file first.", true);
        convertBtn.disabled = false;
        return;
      }
      const form = new FormData();
      form.append("file", selectedFile);
      form.append("strength", strength);
      const res = await fetch(`${API_BASE}/convert/file`, { method: "POST", body: form });
      if (!res.ok) throw new Error((await res.json()).detail || "Conversion failed");
      html = (await res.json()).html;
    } else {
      const text = document.getElementById("text-input").value;
      const res = await fetch(`${API_BASE}/convert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, strength }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Conversion failed");
      html = (await res.json()).html;
    }
    outputEl.innerHTML = html || '<p class="output-placeholder">Nothing to show.</p>';
    setStatus("Done.");
  } catch (err) {
    setStatus(err.message || "Something went wrong.", true);
  } finally {
    convertBtn.disabled = false;
  }
}

convertBtn.addEventListener("click", convert);

// ---------- Export ----------
document.querySelectorAll(".export-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const format = btn.dataset.format;
    const strength = Number(slider.value) / 100;
    setStatus(`Exporting .${format}…`);

    try {
      const form = new FormData();
      form.append("format", format);
      form.append("strength", strength);

      if (activeInputMode === "upload") {
        if (!selectedFile) {
          setStatus("Choose a file first.", true);
          return;
        }
        form.append("file", selectedFile);
      } else {
        form.append("text", document.getElementById("text-input").value);
      }

      const res = await fetch(`${API_BASE}/convert/export`, { method: "POST", body: form });
      if (!res.ok) throw new Error("Export failed");

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `bionic_output.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setStatus(`Exported .${format}.`);
    } catch (err) {
      setStatus(err.message || "Export failed.", true);
    }
  });
});

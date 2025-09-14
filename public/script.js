(function () {
  const recapForm = document.getElementById("recap-form");
  const sessionInput = document.getElementById("session-id");
  const recapOutput = document.getElementById("recap-output");
  const statusRegion = document.getElementById("status");
  const copyBtn = document.getElementById("copy-btn");
  const fileInput = document.getElementById("file-upload");

  let controller;

  async function fetchWithTimeout(resource, options = {}) {
    const { timeout = 10000 } = options;
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), timeout);
    const response = await fetch(resource, {
      ...options,
      signal: ctrl.signal,
    });
    clearTimeout(id);
    return response;
  }

  function setStatus(message, isError = false) {
    statusRegion.textContent = message;
    statusRegion.style.color = isError ? "red" : "black";
    statusRegion.setAttribute("aria-busy", "false");
  }

  function renderRecap(data) {
    recapOutput.innerHTML = "";

    function createSection(title, content) {
      const section = document.createElement("section");
      const h3 = document.createElement("h3");
      h3.textContent = title;
      section.appendChild(h3);

      if (Array.isArray(content)) {
        if (content.length === 0) {
          const p = document.createElement("p");
          p.textContent = "None";
          section.appendChild(p);
        } else {
          const ul = document.createElement("ul");
          content.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;
            ul.appendChild(li);
          });
          section.appendChild(ul);
        }
      } else if (typeof content === "string") {
        const p = document.createElement("p");
        p.textContent = content || "None";
        section.appendChild(p);
      }
      recapOutput.appendChild(section);
    }

    createSection("Session ID", data.session_id);
    createSection("Summary", data.summary);
    createSection("Aha Moments", data.aha_moments);
    createSection("MVP Changes", data.mvp_changes);
    createSection("Scope Creep", data.scope_creep);
    createSection("README Notes", data.readme_notes);
    createSection("Post-MVP Ideas", data.post_mvp_ideas);
    createSection("Quality Flags", data.quality_flags);
  }

  recapForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (controller) controller.abort();
    controller = new AbortController();
    recapOutput.innerHTML = "";
    statusRegion.setAttribute("aria-busy", "true");
    setStatus("Fetching recap...");

    try {
      const response = await fetchWithTimeout(
        `/recap?session_id=${encodeURIComponent(sessionInput.value)}`,
        { timeout: 15000 }
      );
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
      const data = await response.json();
      renderRecap(data);
      setStatus("Recap loaded.");
    } catch (error) {
      if (error.name === "AbortError") {
        setStatus("Request aborted.", true);
      } else {
        setStatus("Error fetching recap: " + error.message, true);
      }
    }
  });

  copyBtn.addEventListener("click", () => {
    const text = recapOutput.innerText;
    navigator.clipboard.writeText(text).then(
      () => setStatus("Copied recap to clipboard."),
      (err) => setStatus("Failed to copy: " + err, true)
    );
  });

  // File upload support (from File 1)
  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const jsonData = JSON.parse(e.target.result);
        renderRecap(jsonData);
        setStatus("Recap loaded from file.");
      } catch (err) {
        setStatus("Invalid JSON file.", true);
      }
    };
    reader.readAsText(file);
  });

  // Keyboard shortcuts (from File 2)
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      recapForm.requestSubmit();
    }
    if ((event.ctrlKey || event.metaKey) && event.key === "c") {
      copyBtn.click();
    }
  });
})();
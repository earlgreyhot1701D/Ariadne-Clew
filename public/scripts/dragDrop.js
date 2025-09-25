export function setupDragDrop(dropZoneEl, fileInputEl, handleFile) {
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight() {
    dropZoneEl.classList.add('highlight');
  }

  function unhighlight() {
    dropZoneEl.classList.remove('highlight');
  }

  async function handleDrop(e) {
    const files = e.dataTransfer.files;
    if (files && files.length > 0 && files[0].type === 'application/json') {
      handleFile(files[0]);
    } else {
      alert('Please drop a JSON file.');
    }
  }

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((eventName) => {
    dropZoneEl.addEventListener(eventName, preventDefaults, false);
  });

  ['dragenter', 'dragover'].forEach((e) =>
    dropZoneEl.addEventListener(e, highlight)
  );
  ['dragleave', 'drop'].forEach((e) =>
    dropZoneEl.addEventListener(e, unhighlight)
  );
  dropZoneEl.addEventListener('drop', handleDrop);

  fileInputEl.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/json') {
      handleFile(file);
    } else {
      alert('File must be JSON');
    }
  });
}

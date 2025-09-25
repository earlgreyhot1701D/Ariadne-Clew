export function getElement(id) {
  const element = document.getElementById(id);
  if (!element) {
    throw new Error(`Element with id '${id}' not found`);
  }
  return element;
}

export function setElementContent(id, content) {
  const element = getElement(id);
  element.textContent = content;
}

export function setElementHTML(id, html) {
  const element = getElement(id);
  element.innerHTML = html;
}

export function showElement(id) {
  const element = getElement(id);
  element.style.display = 'block';
}

export function hideElement(id) {
  const element = getElement(id);
  element.style.display = 'none';
}

export function enableElement(id) {
  const element = getElement(id);
  element.disabled = false;
}

export function disableElement(id) {
  const element = getElement(id);
  element.disabled = true;
}

export function clearElement(id) {
  const element = getElement(id);
  element.innerHTML = '';
}

export function addClickListener(id, callback) {
  const element = getElement(id);
  element.addEventListener('click', callback);
}

export function addSubmitListener(id, callback) {
  const element = getElement(id);
  element.addEventListener('submit', callback);
}

export function getValue(id) {
  const element = getElement(id);
  return element.value;
}

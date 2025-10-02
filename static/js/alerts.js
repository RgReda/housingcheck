/* eslint-env browser */
const alertsEndpoint = '/api/alerts';

async function fetchJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

async function createAlert(symbol, condition, threshold) {
  const payload = { symbol, condition, threshold };
  await fetchJSON(alertsEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  window.alert('Alerte créée avec succès !');
}

function init() {
  const form = document.querySelector('#alert-form');
  if (!form) return;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const symbol = document.querySelector('#alert-symbol').value.trim();
    const condition = document.querySelector('#alert-condition').value;
    const threshold = parseFloat(document.querySelector('#alert-threshold').value);
    if (!symbol || Number.isNaN(threshold)) {
      return;
    }
    try {
      await createAlert(symbol, condition, threshold);
      form.reset();
    } catch (error) {
      console.error('Impossible de créer l\'alerte', error);
      window.alert('Erreur lors de la création de l\'alerte.');
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

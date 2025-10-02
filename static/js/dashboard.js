/* eslint-env browser */
const marketEndpoint = '/api/market';
const newsEndpoint = '/api/news';
const alertsEndpoint = '/api/alerts';
const triggeredEndpoint = '/api/alerts/triggered';

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

function formatNumber(value) {
  return value?.toLocaleString('fr-FR', { maximumFractionDigits: 2 }) ?? '—';
}

function updateMarketTables(data) {
  const indicesBody = document.querySelector('#indices-table tbody');
  const stocksBody = document.querySelector('#stocks-table tbody');
  const opcvmBody = document.querySelector('#opcvm-table tbody');
  const updatedSpan = document.querySelector('#market-updated');

  if (updatedSpan && data.updated_at) {
    const date = new Date(data.updated_at);
    updatedSpan.textContent = date.toLocaleTimeString('fr-FR', { hour12: false });
  }

  if (indicesBody) {
    indicesBody.innerHTML = data.indices.map((item) => `
      <tr data-symbol="${item.symbol}">
        <td><a href="/action/${item.symbol}">${item.name}</a></td>
        <td class="text-end">${formatNumber(item.last)}</td>
        <td class="text-end">${formatNumber(item.change)}</td>
        <td class="text-end">${formatNumber(item.percent_change * 100)}%</td>
        <td class="text-end">${formatNumber(item.volume)}</td>
      </tr>`).join('');
  }

  if (stocksBody) {
    stocksBody.innerHTML = data.stocks.map((item) => `
      <tr data-symbol="${item.symbol}">
        <td><a href="/action/${item.symbol}">${item.name}</a> <span class="badge bg-secondary">${item.symbol}</span></td>
        <td class="text-end">${formatNumber(item.last)}</td>
        <td class="text-end">${formatNumber(item.change)}</td>
        <td class="text-end">${formatNumber(item.percent_change * 100)}%</td>
        <td class="text-end">${formatNumber(item.volume)}</td>
      </tr>`).join('');
  }

  if (opcvmBody) {
    opcvmBody.innerHTML = data.opcvm.map((fund) => `
      <tr>
        <td>${fund.code}</td>
        <td>${fund.name}</td>
        <td>${fund.category}</td>
        <td>${formatNumber(fund.vl)}</td>
        <td>${fund.frequency}</td>
      </tr>`).join('');
  }
}

function updateNewsList(items) {
  const newsList = document.querySelector('#news-list');
  if (!newsList) return;
  if (!items.length) {
    newsList.innerHTML = '<div class="list-group-item">Aucune actualité disponible.</div>';
    return;
  }
  newsList.innerHTML = items.map((item) => {
    const published = item.published ? new Date(item.published).toLocaleString('fr-FR', { hour12: false }) : '';
    return `
      <a class="list-group-item list-group-item-action" href="${item.link}" target="_blank" rel="noopener">
        <div class="d-flex w-100 justify-content-between">
          <h6 class="mb-1">${item.title}</h6>
          <small class="text-muted">${item.source}</small>
        </div>
        ${published ? `<small class="text-muted">${published}</small>` : ''}
      </a>`;
  }).join('');
}

function renderAlerts(alerts) {
  const alertList = document.querySelector('#alert-list');
  if (!alertList) return;
  if (!alerts.length) {
    alertList.innerHTML = '<p class="text-muted">Aucune alerte définie pour le moment.</p>';
    return;
  }
  alertList.innerHTML = alerts.map((alert) => `
    <div class="alert alert-light border d-flex justify-content-between align-items-center" data-alert-id="${alert.id}">
      <div>
        <strong>${alert.symbol}</strong> ${alert.condition === 'above' ? '≥' : '≤'} ${alert.threshold}
        ${alert.triggered_at ? '<span class="badge bg-warning text-dark">Déclenchée</span>' : ''}
      </div>
      <button class="btn btn-sm btn-outline-danger" data-delete-alert>Supprimer</button>
    </div>`).join('');
}

function renderTriggeredAlerts(alerts) {
  const container = document.querySelector('#triggered-alerts');
  if (!container) return;
  if (!alerts.length) {
    container.innerHTML = '';
    return;
  }
  container.innerHTML = `
    <h6>Derniers déclenchements</h6>
    <ul class="list-group">
      ${alerts.map((alert) => `<li class="list-group-item">${alert.symbol} ${alert.condition === 'above' ? '≥' : '≤'} ${alert.threshold} (${alert.triggered_at ? new Date(alert.triggered_at).toLocaleTimeString('fr-FR', { hour12: false }) : ''})</li>`).join('')}
    </ul>`;
}

async function refreshAll() {
  try {
    const [marketData, newsItems, alerts, triggered] = await Promise.all([
      fetchJSON(marketEndpoint),
      fetchJSON(newsEndpoint),
      fetchJSON(alertsEndpoint),
      fetchJSON(triggeredEndpoint)
    ]);
    updateMarketTables(marketData);
    updateNewsList(newsItems);
    renderAlerts(alerts);
    renderTriggeredAlerts(triggered);
  } catch (error) {
    console.error('Erreur lors de la mise à jour du tableau de bord', error);
  }
}

async function createAlert(symbol, condition, threshold) {
  const payload = { symbol, condition, threshold };
  await fetchJSON(alertsEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  await refreshAlerts();
}

async function refreshAlerts() {
  try {
    const [alerts, triggered] = await Promise.all([
      fetchJSON(alertsEndpoint),
      fetchJSON(triggeredEndpoint)
    ]);
    renderAlerts(alerts);
    renderTriggeredAlerts(triggered);
  } catch (error) {
    console.error('Impossible de rafraîchir les alertes', error);
  }
}

function setupAlertForm() {
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
      console.error('Création alerte impossible', error);
    }
  });
}

function setupAlertDeletion() {
  const container = document.querySelector('#alert-list');
  if (!container) return;
  container.addEventListener('click', async (event) => {
    if (!(event.target instanceof HTMLElement)) return;
    if (!event.target.matches('[data-delete-alert]')) return;
    const wrapper = event.target.closest('[data-alert-id]');
    if (!wrapper) return;
    const id = wrapper.getAttribute('data-alert-id');
    if (!id) return;
    try {
      await fetchJSON(`${alertsEndpoint}/${id}`, { method: 'DELETE' });
      await refreshAlerts();
    } catch (error) {
      console.error('Suppression alerte impossible', error);
    }
  });
}

function setupClearTriggered() {
  const btn = document.querySelector('#clear-triggered');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    try {
      await fetchJSON(triggeredEndpoint, { method: 'POST' });
      await refreshAlerts();
    } catch (error) {
      console.error('Effacement des déclenchements impossible', error);
    }
  });
}

function init() {
  setupAlertForm();
  setupAlertDeletion();
  setupClearTriggered();
  refreshAll();
  window.setInterval(refreshAll, 60000);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

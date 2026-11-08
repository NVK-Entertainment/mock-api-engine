// Логика страницы /projects: список проектов и глобального scope, их CRUD.
(() => {
  'use strict';

  const { $, $$, el, api, ApiError, toast, flash, reload, openActionModal, textField } = window.App;
  const APP = JSON.parse($('#app-data').textContent);

  const projectById = (id) => APP.projects.find((p) => p.id === id);
  const endpointById = (id) => APP.endpoints.find((e) => e.id === id);
  const projectName = (id) => (id === null ? 'Глобальные' : projectById(id)?.name ?? `Проект ${id}`);

  /* ---------- состояние раскрытых секций между перезагрузками ---------- */

  // Какая секция сейчас раскрыта: 'projects' или 'global'
  try {
    const scope = sessionStorage.getItem('projects-page-scope');
    if (scope === 'global') {
      $('#scope-projects').classList.remove('show');
      $('#scope-projects-btn').classList.add('collapsed');
      $('#scope-projects-btn').setAttribute('aria-expanded', 'false');
      $('#scope-global').classList.add('show');
      $('#scope-global-btn').classList.remove('collapsed');
      $('#scope-global-btn').setAttribute('aria-expanded', 'true');
    }
  } catch { /* ignore */ }
  $('#scope-projects').addEventListener('shown.bs.collapse', () => { try { sessionStorage.setItem('projects-page-scope', 'projects'); } catch { /* ignore */ } });
  $('#scope-global').addEventListener('shown.bs.collapse', () => { try { sessionStorage.setItem('projects-page-scope', 'global'); } catch { /* ignore */ } });

  // Свёрнутые карточки проектов
  let collapsedCards = [];
  try { collapsedCards = JSON.parse(localStorage.getItem('projects-page-collapsed') || '[]'); } catch { /* ignore */ }
  const saveCollapsedCards = () => {
    try { localStorage.setItem('projects-page-collapsed', JSON.stringify(collapsedCards)); } catch { /* ignore */ }
  };
  $$('.project-card').forEach((card) => {
    const body = $('.collapse', card);
    const key = body.id;
    const toggle = $('.toggle-card', card);
    if (collapsedCards.includes(key)) {
      body.classList.remove('show');
      toggle.classList.add('collapsed');
      toggle.setAttribute('aria-expanded', 'false');
    }
    body.addEventListener('hidden.bs.collapse', () => { collapsedCards = [...new Set([...collapsedCards, key])]; saveCollapsedCards(); });
    body.addEventListener('shown.bs.collapse', () => { collapsedCards = collapsedCards.filter((k) => k !== key); saveCollapsedCards(); });
  });

  // Выпадающие меню внутри карточек не обрезаются по краю контейнера
  $$('[data-bs-toggle="dropdown"]').forEach((btn) =>
    new bootstrap.Dropdown(btn, { popperConfig: (cfg) => ({ ...cfg, strategy: 'fixed' }) }));

  /* ---------- простые действия (проекты, подтверждения) ---------- */

  const simpleActions = {
    'new-project': () => openActionModal({
      title: 'Новый проект', confirm: 'Создать',
      build: () => {
        const input = textField('Название', '', 'Не длиннее 32 символов, название уникально.');
        return {
          valid: () => input.value.trim().length > 0,
          run: async () => { await api('POST', '/api/v1/projects', { name: input.value.trim() }); flash('Проект создан'); reload(); },
        };
      },
    }),

    'rename-project': (id) => {
      const project = projectById(id);
      openActionModal({
        title: 'Переименовать проект', confirm: 'Сохранить',
        build: () => {
          const input = textField('Название', project.name, 'Не длиннее 32 символов, название уникально.');
          return {
            valid: () => input.value.trim().length > 0,
            run: async () => { await api('PATCH', `/api/v1/projects/${id}`, { name: input.value.trim() }); flash('Проект переименован'); reload(); },
          };
        },
      });
    },

    'delete-project': (id) => {
      const project = projectById(id);
      const count = APP.endpoints.filter((e) => e.project_id === id).length;
      openActionModal({
        title: `Удалить проект «${project.name}»?`, confirm: 'Удалить', danger: true,
        build: (body) => {
          body.append(el('p', { className: 'mb-0' }, count
            ? `Вместе с ним удалятся эндпоинты проекта (${count}). Это нельзя отменить.`
            : 'В проекте нет эндпоинтов.'));
          return {
            valid: () => true,
            run: async () => { await api('DELETE', `/api/v1/projects/${id}`); flash('Проект удалён'); reload(); },
          };
        },
      });
    },

    'delete-endpoint': (id) => {
      const ep = endpointById(id);
      openActionModal({
        title: 'Удалить эндпоинт?', confirm: 'Удалить', danger: true,
        build: (body) => {
          const p = el('p', { className: 'mb-0' });
          p.append(el('code', {}, `${ep.method} ${ep.path}`), ' будет удалён.');
          body.append(p);
          return {
            valid: () => true,
            run: async () => { await api('DELETE', `/api/v1/management/endpoints/${id}`); flash('Эндпоинт удалён'); reload(); },
          };
        },
      });
    },
  };

  // Переместить / клонировать / сделать глобальным: мгновенное действие по клику, без модалки
  async function instantAction(promise, successText) {
    try {
      await promise;
      flash(successText);
      reload();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Не удалось выполнить действие', 'error');
    }
  }

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const action = btn.dataset.action;
    const id = btn.dataset.id ? Number(btn.dataset.id) : undefined;

    if (action === 'move-endpoint') {
      instantAction(api('POST', `/api/v1/endpoints/${id}/move-to/projects/${btn.dataset.target}`), `Перемещён в «${projectName(Number(btn.dataset.target))}»`);
      return;
    }
    if (action === 'clone-endpoint') {
      instantAction(api('POST', `/api/v1/endpoints/${id}/clone-to/projects/${btn.dataset.target}`), `Клонирован в «${projectName(Number(btn.dataset.target))}»`);
      return;
    }
    if (action === 'make-global') {
      instantAction(api('PATCH', `/api/v1/management/endpoints/${id}`, { project_id: null }), 'Эндпоинт стал глобальным');
      return;
    }
    if (action === 'add-endpoint') {
      openEndpointModal(null, btn.dataset.projectId ? Number(btn.dataset.projectId) : null);
      return;
    }
    if (action === 'edit-endpoint') {
      openEndpointModal(endpointById(id));
      return;
    }
    const run = simpleActions[action];
    if (run) run(id);
  });

  /* ---------- модальное окно создания/редактирования эндпоинта ---------- */

  const STATUS_TEXT = {
    200: 'OK', 201: 'Created', 202: 'Accepted', 204: 'No Content', 301: 'Moved Permanently', 302: 'Found', 304: 'Not Modified',
    400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed', 409: 'Conflict',
    418: "I'm a teapot", 422: 'Unprocessable Entity', 429: 'Too Many Requests', 500: 'Internal Server Error', 502: 'Bad Gateway',
    503: 'Service Unavailable', 504: 'Gateway Timeout',
  };

  const epModalEl = $('#endpointModal');
  const epModal = bootstrap.Modal.getOrCreateInstance(epModalEl);
  const epForm = $('#endpointForm');
  const epMethodBtn = $('#ep-method-btn');
  const epPath = $('#ep-path');
  const epStatus = $('#ep-status');
  const epActive = $('#ep-active');
  const epBody = $('#ep-body');
  const epHeadersBody = $('#ep-headers-body');
  const epSaveBtn = $('#ep-save-btn');
  const showEpError = (id, text) => { const n = $(id); n.textContent = text || ''; n.hidden = !text; };

  let epEndpoint = null;   // редактируемый эндпоинт или null (создание)
  let epProjectId = null;  // проект для нового эндпоинта
  let epAttempted = false;

  function headerRow(key = '', value = '') {
    const tr = el('tr');
    const keyInput = el('input', { className: 'form-control form-control-sm font-monospace border-0 rounded-0 h-key', placeholder: 'Ключ', value, spellcheck: false });
    const valInput = el('input', { className: 'form-control form-control-sm font-monospace border-0 rounded-0 h-value', placeholder: 'Значение', value: value === undefined ? '' : value, spellcheck: false });
    keyInput.value = key; valInput.value = value;
    const del = el('button', { type: 'button', className: 'btn btn-sm btn-icon row-del' });
    del.innerHTML = '<i class="bi bi-x-lg"></i>';
    tr.append(el('td', {}, '')); tr.append(el('td', {}, ''));
    tr.children[0].append(keyInput);
    tr.children[1].append(valInput);
    const delTd = el('td', { className: 'kv-del' }, '');
    delTd.append(del);
    tr.append(delTd);
    return tr;
  }

  function ensureEpTrailingBlank() {
    const last = $$('tr', epHeadersBody).pop();
    if (last && ($('.h-key', last).value || $('.h-value', last).value)) epHeadersBody.append(headerRow());
  }
  epHeadersBody.addEventListener('input', () => { ensureEpTrailingBlank(); epTouch(); });
  epHeadersBody.addEventListener('click', (e) => {
    const del = e.target.closest('.row-del');
    if (!del) return;
    const tr = del.closest('tr');
    if (tr !== epHeadersBody.lastElementChild) { tr.remove(); epTouch(); }
  });

  function openEndpointModal(endpoint, projectId) {
    epEndpoint = endpoint;
    epProjectId = endpoint ? endpoint.project_id : projectId;
    epAttempted = false;

    $('#endpointModalTitle').textContent = endpoint ? 'Изменить эндпоинт' : 'Новый эндпоинт';
    $('#ep-scope-name').textContent = projectName(epProjectId);
    epSaveBtn.textContent = endpoint ? 'Сохранить' : 'Создать';
    $('#ep-server-error').hidden = true;

    epMethodBtn.dataset.method = endpoint ? endpoint.method : 'GET';
    epPath.value = endpoint ? endpoint.path : '';
    epStatus.value = endpoint ? String(endpoint.status_code) : '200';
    epActive.checked = endpoint ? endpoint.is_active : true;
    $(`#ep-scenario-${endpoint ? endpoint.scenario : 'SUCCESS'}`).checked = true;
    epBody.value = endpoint && endpoint.response_body != null ? JSON.stringify(endpoint.response_body, null, 2) : '';

    epHeadersBody.replaceChildren();
    const headers = endpoint ? endpoint.response_headers : {};
    Object.entries(headers).forEach(([k, v]) => epHeadersBody.append(headerRow(k, v)));
    epHeadersBody.append(headerRow());

    epRefresh();
    epModal.show();
  }

  $$('.ep-method-item').forEach((item) => item.addEventListener('click', () => {
    epMethodBtn.dataset.method = item.dataset.method;
    epTouch();
  }));
  [epPath, epBody, epActive].forEach((n) => n.addEventListener('input', epTouch));
  epActive.addEventListener('change', epTouch);
  epStatus.addEventListener('input', () => { epStatus.value = epStatus.value.replace(/\D/g, ''); epTouch(); });
  $$('input[name="ep-scenario"]').forEach((r) => r.addEventListener('change', epTouch));

  $('#ep-format-body').addEventListener('click', () => {
    try {
      if (epBody.value.trim()) epBody.value = JSON.stringify(JSON.parse(epBody.value), null, 2);
      epRefresh();
    } catch { /* ошибка уже показана */ }
  });

  function epCollect() {
    const rows = $$('tr', epHeadersBody).map((tr) => [$('.h-key', tr).value, $('.h-value', tr).value]);
    return {
      method: epMethodBtn.dataset.method,
      path: epPath.value,
      status: epStatus.value,
      scenario: $('input[name="ep-scenario"]:checked').value,
      active: epActive.checked,
      headers: rows,
      body: epBody.value,
    };
  }

  function epValidate(d) {
    const errors = {};
    const path = d.path.trim();
    if (!path) errors.path = 'Укажите путь, например /users/1';
    else if (path.length > 512) errors.path = 'Путь не длиннее 512 символов';

    const status = Number(d.status);
    if (!/^\d{3}$/.test(d.status.trim()) || status < 100 || status > 599) errors.status = 'Код от 100 до 599';

    const headers = {};
    const seen = new Set();
    for (const [rawKey, value] of d.headers) {
      const key = rawKey.trim();
      if (!key && !value) continue;
      if (!key) { errors.headers = 'У заголовка не указан ключ'; break; }
      if (seen.has(key.toLowerCase())) { errors.headers = `Заголовок «${key}» указан дважды`; break; }
      seen.add(key.toLowerCase());
      headers[key] = value;
    }

    let parsed = null;
    if (d.body.trim()) {
      try { parsed = JSON.parse(d.body); } catch (e) { errors.body = e.message; }
    }
    if (Object.keys(errors).length) return { payload: null, errors };
    return {
      errors,
      payload: { method: d.method, path, status_code: status, response_headers: headers, response_body: parsed, scenario: d.scenario, is_active: d.active },
    };
  }

  function epRefresh() {
    const d = epCollect();
    const { errors } = epValidate(d);

    epMethodBtn.className = `btn dropdown-toggle method-btn m-${d.method}`;
    epMethodBtn.textContent = d.method;

    const statusText = $('#ep-status-text');
    statusText.textContent = (epAttempted && errors.status) || STATUS_TEXT[Number(d.status)] || '';
    statusText.className = `small ${epAttempted && errors.status ? 'text-danger' : 'text-body-secondary'}`;
    epStatus.classList.toggle('is-invalid', epAttempted && !!errors.status);

    $('#ep-active-text').textContent = d.active ? 'Включён' : 'Выключен, отвечает 404';

    const state = $('#ep-body-state');
    const bad = !!errors.body;
    state.textContent = !d.body.trim() ? 'Тело пустое, придёт null' : bad ? `Ошибка JSON: ${errors.body}` : 'Корректный JSON';
    state.className = `small mt-2 mb-0 ${bad ? 'bad' : 'ok'}`;
    epBody.classList.toggle('is-invalid', bad);

    showEpError('#ep-err-path', epAttempted && errors.path);
    epPath.classList.toggle('is-invalid', epAttempted && !!errors.path);
    showEpError('#ep-err-headers', epAttempted && errors.headers);
  }

  function epTouch() {
    $('#ep-server-error').hidden = true;
    epRefresh();
  }

  epForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    epAttempted = true;
    const { payload } = epValidate(epCollect());
    epRefresh();
    if (!payload) return;
    epSaveBtn.disabled = true;
    epSaveBtn.textContent = epEndpoint ? 'Сохраняем…' : 'Создаём…';
    try {
      if (epEndpoint) {
        await api('PATCH', `/api/v1/management/endpoints/${epEndpoint.id}`, payload);
        flash('Сохранено');
      } else {
        await api('POST', '/api/v1/management/endpoints', { ...payload, project_id: epProjectId });
        flash('Эндпоинт создан');
      }
      reload();
    } catch (err) {
      $('#ep-server-error').textContent = err.message;
      $('#ep-server-error').hidden = false;
      epSaveBtn.disabled = false;
      epSaveBtn.textContent = epEndpoint ? 'Сохранить' : 'Создать';
    }
  });
})();

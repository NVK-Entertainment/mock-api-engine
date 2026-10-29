(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const APP = JSON.parse($('#app-data').textContent);
  let leaving = false; // true, когда уходим со страницы сами (после сохранения)

  /* ---------- утилиты ---------- */

  function toast(text, kind = 'success') {
    const el = document.createElement('div');
    el.className = `alert alert-${kind === 'error' ? 'danger' : 'dark'} shadow-sm py-2 px-3 mb-2`;
    el.textContent = text;
    $('#toasts').append(el);
    setTimeout(() => el.remove(), kind === 'error' ? 6000 : 2500);
  }

  // Сообщение, которое нужно показать после перезагрузки страницы
  function flash(text) {
    try { sessionStorage.setItem('flash', text); } catch { /* хранилище недоступно */ }
  }
  function reload() { leaving = true; location.reload(); }
  function go(url) { leaving = true; location.assign(url); }

  function formatDetail(detail) {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map((d) => {
        const loc = (d.loc || []).filter((p) => p !== 'body').join('.');
        return loc ? `${loc}: ${d.msg}` : d.msg;
      }).join('; ');
    }
    return null;
  }

  async function api(method, url, body) {
    let res;
    try {
      res = await fetch(url, {
        method,
        headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
    } catch {
      throw new Error('Нет связи с сервером. Проверьте, что бэкенд запущен.');
    }
    if (!res.ok) {
      let message = `Ошибка ${res.status}`;
      try { message = formatDetail((await res.json()).detail) || message; } catch { /* не JSON */ }
      throw new Error(message);
    }
    return res.status === 204 ? null : res.json();
  }

  try {
    const msg = sessionStorage.getItem('flash');
    if (msg) { sessionStorage.removeItem('flash'); toast(msg); }
  } catch { /* ignore */ }

  /* ---------- сайдбар ---------- */

  // Выпадающие меню внутри прокручиваемого списка: position: fixed, чтобы не обрезались.
  $$('.sidebar [data-bs-toggle="dropdown"]').forEach((el) =>
    new bootstrap.Dropdown(el, { popperConfig: (cfg) => ({ ...cfg, strategy: 'fixed' }) }));

  // Свёрнутые группы запоминаем между перезагрузками.
  let collapsed = [];
  try { collapsed = JSON.parse(localStorage.getItem('collapsed-groups') || '[]'); } catch { /* ignore */ }
  const saveCollapsed = () => {
    try { localStorage.setItem('collapsed-groups', JSON.stringify(collapsed)); } catch { /* ignore */ }
  };
  $$('.group').forEach((group) => {
    const key = group.dataset.group;
    const list = $('.endpoints', group);
    const toggle = $('.group-toggle', group);
    if (collapsed.includes(key)) {
      list.classList.remove('show');
      toggle.classList.add('collapsed');
      toggle.setAttribute('aria-expanded', 'false');
    }
    list.addEventListener('hidden.bs.collapse', () => { collapsed = [...new Set([...collapsed, key])]; saveCollapsed(); });
    list.addEventListener('shown.bs.collapse', () => { collapsed = collapsed.filter((k) => k !== key); saveCollapsed(); });
  });

  /* ---------- модальное окно действий ---------- */

  const modalEl = $('#actionModal');
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  const form = $('#actionForm');
  const body = $('#actionBody');
  const confirmBtn = $('#actionConfirm');
  let current = null;

  /**
   * title, confirm — тексты; danger — красная кнопка;
   * build(body) наполняет тело окна и возвращает { valid(), run() }.
   */
  function openModal({ title, confirm, danger, build }) {
    $('#actionModalTitle').textContent = title;
    confirmBtn.textContent = confirm;
    confirmBtn.className = `btn ${danger ? 'btn-danger' : 'btn-primary'}`;
    body.replaceChildren();
    current = build(body);
    const sync = () => { confirmBtn.disabled = !current.valid(); };
    body.oninput = body.onchange = sync;
    sync();
    modal.show();
  }

  modalEl.addEventListener('shown.bs.modal', () => {
    const first = $('input, select', body);
    if (first) first.focus();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!current || confirmBtn.disabled) return;
    confirmBtn.disabled = true;
    try {
      await current.run();
    } catch (err) {
      toast(err.message, 'error');
      confirmBtn.disabled = !current.valid();
    }
  });

  const el = (tag, props = {}, text) => {
    const node = Object.assign(document.createElement(tag), props);
    if (text !== undefined) node.textContent = text;
    return node;
  };

  function textField(label, value, hint) {
    const input = el('input', { className: 'form-control', id: 'modal-field', value: value || '', maxLength: 32 });
    body.append(el('label', { className: 'form-label small fw-semibold text-body-secondary', htmlFor: 'modal-field' }, label), input);
    if (hint) body.append(el('div', { className: 'form-text' }, hint));
    return input;
  }

  const projectById = (id) => APP.projects.find((p) => p.id === id);
  const endpointById = (id) => APP.endpoints.find((e) => e.id === id);
  const editor = $('#editor');
  const openEndpointId = editor && editor.dataset.endpointId ? Number(editor.dataset.endpointId) : null;

  const actions = {
    'new-project': () => openModal({
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
      openModal({
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
      openModal({
        title: `Удалить проект «${project.name}»?`, confirm: 'Удалить', danger: true,
        build: () => {
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
      openModal({
        title: 'Удалить эндпоинт?', confirm: 'Удалить', danger: true,
        build: () => {
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

  // Переместить / клонировать: выбор другого проекта
  ['move', 'clone'].forEach((kind) => {
    actions[`${kind}-endpoint`] = (id) => {
      const ep = endpointById(id);
      const isMove = kind === 'move';
      const options = APP.projects.filter((p) => p.id !== ep.project_id);
      openModal({
        title: isMove ? 'Переместить эндпоинт' : 'Клонировать эндпоинт',
        confirm: isMove ? 'Переместить' : 'Клонировать',
        build: () => {
          body.append(el('p', {}, ''));
          body.lastChild.append(el('code', {}, `${ep.method} ${ep.path}`));
          if (!options.length) {
            body.append(el('div', { className: 'form-text' }, 'Нет других проектов. Сначала создайте проект.'));
            return { valid: () => false, run: async () => {} };
          }
          const select = el('select', { className: 'form-select', id: 'modal-field' });
          select.append(el('option', { value: '' }, 'Выберите проект'));
          options.forEach((p) => select.append(el('option', { value: String(p.id) }, p.name)));
          body.append(el('label', { className: 'form-label small fw-semibold text-body-secondary', htmlFor: 'modal-field' }, 'Проект'), select);
          return {
            valid: () => select.value !== '',
            run: async () => {
              const target = Number(select.value);
              const result = await api('POST', `/api/v1/endpoints/${id}/${kind}-to/projects/${target}`);
              const name = projectById(target).name;
              flash(isMove ? `Перемещён в «${name}»` : `Клонирован в «${name}»`);
              // При переносе открытого эндпоинта может получиться другая запись (реактивация дубликата)
              if (isMove && openEndpointId === id) go(`/ui/endpoints/${result.id}`); else reload();
            },
          };
        },
      });
    };
  });

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const run = actions[btn.dataset.action];
    if (run) run(btn.dataset.id ? Number(btn.dataset.id) : undefined);
  });

  /* ---------- редактор эндпоинта ---------- */

  if (!editor) return;

  const STATUS_TEXT = {
    200: 'OK', 201: 'Created', 202: 'Accepted', 204: 'No Content', 301: 'Moved Permanently', 302: 'Found', 304: 'Not Modified',
    400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed', 409: 'Conflict',
    418: "I'm a teapot", 422: 'Unprocessable Entity', 429: 'Too Many Requests', 500: 'Internal Server Error', 502: 'Bad Gateway',
    503: 'Service Unavailable', 504: 'Gateway Timeout',
  };

  const endpointId = editor.dataset.endpointId ? Number(editor.dataset.endpointId) : null;
  const projectId = editor.dataset.projectId ? Number(editor.dataset.projectId) : null;
  const isNew = endpointId === null;

  const methodBtn = $('#method-btn');
  const pathInput = $('#path');
  const statusInput = $('#status');
  const activeInput = $('#active');
  const bodyInput = $('#body');
  const saveBtn = $('#save-btn');
  const headersBody = $('#headers-body');
  const showError = (id, text) => { const n = $(id); n.textContent = text || ''; n.hidden = !text; };

  let attempted = false;
  let saving = false;

  const scenario = () => $('input[name="scenario"]:checked').value;
  const rows = () => $$('tr', headersBody).map((tr) => [$('.h-key', tr).value, $('.h-value', tr).value]);

  function collect() {
    return {
      method: methodBtn.dataset.method,
      path: pathInput.value,
      status: statusInput.value,
      scenario: scenario(),
      active: activeInput.checked,
      headers: rows(),
      body: bodyInput.value,
    };
  }

  const fingerprint = (d) => JSON.stringify([
    d.method, d.path.trim(), d.status.trim(), d.scenario, d.active,
    d.headers.filter(([k, v]) => k || v), d.body.trim(),
  ]);
  const baseline = fingerprint(collect());
  const isDirty = () => fingerprint(collect()) !== baseline;

  function validate(d) {
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
      payload: {
        method: d.method, path, status_code: status, response_headers: headers,
        response_body: parsed, scenario: d.scenario, is_active: d.active,
      },
    };
  }

  function normalizePath(p) {
    p = p.trim();
    if (!p.startsWith('/')) p = '/' + p;
    if (p.length > 1 && p.endsWith('/')) p = p.replace(/\/+$/, '') || '/';
    return p;
  }

  function refresh() {
    const d = collect();
    const { errors } = validate(d);

    // Адрес мока и подсказка про сценарий
    const scope = projectId;
    const url = `${location.origin}/api/v1/mock${scope !== null ? `/projects/${scope}` : ''}${normalizePath(d.path)}`;
    const mock = $('#mock-url');
    mock.title = url;
    mock.replaceChildren(el('b', { className: `m-${d.method}` }, d.method), ` ${url}`);
    $('#scenario-hint').hidden = d.scenario === 'SUCCESS';
    $('#scenario-hint-value').textContent = d.scenario;

    // Метод
    methodBtn.className = `btn dropdown-toggle method-btn m-${d.method}`;
    methodBtn.textContent = d.method;

    // Статус
    const statusText = $('#status-text');
    statusText.textContent = (attempted && errors.status) || STATUS_TEXT[Number(d.status)] || '';
    statusText.className = `small ${attempted && errors.status ? 'text-danger' : 'text-body-secondary'}`;
    statusInput.classList.toggle('is-invalid', attempted && !!errors.status);

    // Тумблер
    $('#active-text').textContent = d.active ? 'Включён' : 'Выключен, отвечает 404';

    // Состояние JSON
    const state = $('#body-state');
    const bad = !!errors.body;
    state.textContent = !d.body.trim() ? 'Тело пустое, придёт null' : bad ? `Ошибка JSON: ${errors.body}` : 'Корректный JSON';
    state.className = `small mt-2 mb-0 ${bad ? 'bad' : 'ok'}`;
    bodyInput.classList.toggle('is-invalid', bad);
    $('#format-body').disabled = bad || !d.body.trim();

    // Ошибки пути и заголовков показываем после первой попытки сохранить
    showError('#err-path', attempted && errors.path);
    pathInput.classList.toggle('is-invalid', attempted && !!errors.path);
    showError('#err-headers', attempted && errors.headers);

    saveBtn.disabled = saving || (!isNew && !isDirty());
  }

  function touch() {
    $('#server-error').hidden = true;
    refresh();
  }

  // Таблица заголовков: внизу всегда остаётся пустая строка, как в Postman
  function ensureTrailingBlank() {
    const last = $$('tr', headersBody).pop();
    if (last && ($('.h-key', last).value || $('.h-value', last).value)) {
      const copy = last.cloneNode(true);
      $$('input', copy).forEach((i) => { i.value = ''; });
      headersBody.append(copy);
    }
  }
  headersBody.addEventListener('input', () => { ensureTrailingBlank(); touch(); });
  headersBody.addEventListener('click', (e) => {
    const del = e.target.closest('.row-del');
    if (!del) return;
    const tr = del.closest('tr');
    if (tr !== headersBody.lastElementChild) { tr.remove(); touch(); }
  });

  $$('.method-item').forEach((item) => item.addEventListener('click', () => {
    methodBtn.dataset.method = item.dataset.method;
    touch();
  }));
  [pathInput, bodyInput, activeInput].forEach((n) => n.addEventListener('input', touch));
  activeInput.addEventListener('change', touch);
  statusInput.addEventListener('input', () => { statusInput.value = statusInput.value.replace(/\D/g, ''); touch(); });
  $$('input[name="scenario"]').forEach((r) => r.addEventListener('change', touch));

  $('#format-body').addEventListener('click', () => {
    try {
      if (bodyInput.value.trim()) bodyInput.value = JSON.stringify(JSON.parse(bodyInput.value), null, 2);
      touch();
    } catch { /* ошибка уже показана */ }
  });

  $('#copy-url').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText($('#mock-url').title);
      toast('Адрес скопирован');
    } catch {
      toast('Не удалось скопировать адрес', 'error');
    }
  });

  async function save() {
    attempted = true;
    const { payload } = validate(collect());
    refresh();
    if (!payload || saving) return;
    saving = true;
    saveBtn.disabled = true;
    saveBtn.textContent = 'Сохраняем…';
    try {
      if (isNew) {
        const saved = await api('POST', '/api/v1/management/endpoints', { ...payload, project_id: projectId });
        flash('Эндпоинт создан');
        go(`/ui/endpoints/${saved.id}`);
      } else {
        await api('PATCH', `/api/v1/management/endpoints/${endpointId}`, payload);
        flash('Сохранено');
        reload(); // сервер отдаст страницу с нормализованным путём и отформатированным телом
      }
    } catch (err) {
      const box = $('#server-error');
      box.textContent = err.message;
      box.hidden = false;
      saving = false;
      saveBtn.textContent = isNew ? 'Создать' : 'Сохранить';
      refresh();
    }
  }

  $('#request-form').addEventListener('submit', (e) => { e.preventDefault(); save(); });

  // Ctrl/Cmd+S — сохранить
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      e.preventDefault();
      if (isNew || isDirty()) save();
    }
  });

  // Уход со страницы с несохранёнными правками (ссылки, перезагрузка, закрытие вкладки)
  window.addEventListener('beforeunload', (e) => {
    if (!leaving && isDirty()) { e.preventDefault(); e.returnValue = ''; }
  });

  refresh();
})();

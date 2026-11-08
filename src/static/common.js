// Общие для всех страниц вещи: fetch-обёртка, тосты, сообщение после перезагрузки
// и общее модальное окно подтверждений/простых форм (#actionModal из base.html).
window.App = (() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  const el = (tag, props = {}, text) => {
    const node = Object.assign(document.createElement(tag), props);
    if (text !== undefined) node.textContent = text;
    return node;
  };

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
  function reload() { window.__leaving = true; location.reload(); }
  function go(url) { window.__leaving = true; location.assign(url); }

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

  class ApiError extends Error {
    constructor(status, message) {
      super(message);
      this.status = status;
    }
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
      throw new ApiError(0, 'Нет связи с сервером. Проверьте, что бэкенд запущен.');
    }
    if (!res.ok) {
      let message = `Ошибка ${res.status}`;
      try { message = formatDetail((await res.json()).detail) || message; } catch { /* тело не JSON */ }
      throw new ApiError(res.status, message);
    }
    return res.status === 204 ? null : res.json();
  }

  try {
    const msg = sessionStorage.getItem('flash');
    if (msg) { sessionStorage.removeItem('flash'); toast(msg); }
  } catch { /* ignore */ }

  // ---------- общее модальное окно (#actionModal) ----------

  const modalEl = $('#actionModal');
  const modal = modalEl ? bootstrap.Modal.getOrCreateInstance(modalEl) : null;
  const form = $('#actionForm');
  const body = $('#actionBody');
  const confirmBtn = $('#actionConfirm');
  let current = null;

  /**
   * title, confirm — тексты; danger — красная кнопка;
   * build(body) наполняет тело окна и возвращает { valid(), run() }.
   */
  function openActionModal({ title, confirm, danger, build }) {
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

  if (modalEl) {
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
  }

  function textField(label, value, hint) {
    const input = el('input', { className: 'form-control', id: 'modal-field', value: value || '', maxLength: 32 });
    body.append(el('label', { className: 'form-label small fw-semibold text-body-secondary', htmlFor: 'modal-field' }, label), input);
    if (hint) body.append(el('div', { className: 'form-text' }, hint));
    return input;
  }

  return { $, $$, el, toast, flash, reload, go, api, ApiError, openActionModal, textField };
})();

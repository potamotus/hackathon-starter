/**
 * GPTHub custom loader: memory toast + instructions tab.
 * Loaded by Open WebUI via app.html <script src="/static/loader.js">
 */
(function () {
  const API_BASE = window.location.protocol + '//' + window.location.hostname + ':8000';
  const SCOPE = 'default-scope';

  /* ── Styles ── */
  var style = document.createElement('style');
  style.textContent =
    '.memory-toast{position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(10px);opacity:0;' +
    'background:rgba(30,30,30,.92);backdrop-filter:blur(8px);border:1px solid rgba(91,141,239,.3);' +
    'border-radius:8px;padding:8px 16px;font-size:12px;color:#b0b0b0;z-index:9999;pointer-events:none;' +
    'transition:opacity .3s,transform .3s;display:flex;align-items:center;gap:6px;' +
    'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}' +
    '.memory-toast.visible{opacity:1;transform:translateX(-50%) translateY(0)}' +
    '.memory-toast-dot{width:6px;height:6px;border-radius:50%;background:#5b8def;flex-shrink:0}' +
    'td .rounded-full{white-space:nowrap}' +
    /* Tabs */
    '.ct-tabs{display:flex;gap:0;border-bottom:1px solid rgba(255,255,255,.1);margin-bottom:16px}' +
    '.ct-tab{padding:10px 20px;border:none;background:transparent;color:#9ca3af;font-size:14px;' +
    'font-weight:500;cursor:pointer;border-bottom:2px solid transparent;position:relative;bottom:-1px;transition:all .15s}' +
    '.ct-tab:hover{color:#e5e7eb}' +
    '.ct-tab-active{color:#5b8def;border-bottom-color:#5b8def}' +
    /* Instruction rows */
    '.ct-instr-row{display:flex;align-items:center;gap:12px;padding:12px 16px;' +
    'border-bottom:1px solid rgba(255,255,255,.06);cursor:pointer;transition:background .12s}' +
    '.ct-instr-row:hover{background:rgba(255,255,255,.04)}' +
    '.ct-instr-info{flex:1;min-width:0}' +
    '.ct-instr-name{font-size:14px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.ct-instr-desc{font-size:12px;color:#9ca3af;margin-top:2px;display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;overflow:hidden}' +
    '.ct-instr-meta{display:flex;align-items:center;gap:8px;flex-shrink:0}' +
    '.ct-badge{font-size:10px;font-weight:600;padding:2px 6px;border-radius:4px;text-transform:uppercase;letter-spacing:.5px}' +
    '.ct-badge-auto{background:rgba(229,167,59,.15);color:#e5a73b}' +
    '.ct-badge-user{background:rgba(91,141,239,.15);color:#5b8def}' +
    '.ct-empty{text-align:center;padding:40px 20px;color:#6b7280;font-size:13px}' +
    '.ct-add-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:6px;' +
    'border:1px dashed rgba(255,255,255,.15);background:transparent;color:#9ca3af;font-size:13px;' +
    'cursor:pointer;transition:all .15s;margin-bottom:12px}' +
    '.ct-add-btn:hover{border-color:#5b8def;color:#5b8def}' +
    /* Modal */
    '.ct-modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(4px);' +
    'z-index:10000;align-items:center;justify-content:center}' +
    '.ct-modal-overlay.ct-visible{display:flex}' +
    '.ct-modal{background:#1e1e1e;border:1px solid #333;border-radius:14px;width:90%;max-width:560px;' +
    'max-height:85vh;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.5)}' +
    '.ct-modal-header{display:flex;align-items:center;justify-content:space-between;padding:20px 24px 16px;border-bottom:1px solid #333}' +
    '.ct-modal-header h3{font-size:16px;font-weight:600;margin:0}' +
    '.ct-modal-close{width:28px;height:28px;border-radius:6px;border:1px solid #333;background:transparent;' +
    'color:#9ca3af;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:16px}' +
    '.ct-modal-close:hover{background:#333;color:#e5e7eb}' +
    '.ct-modal-body{padding:20px 24px;overflow-y:auto;flex:1}' +
    '.ct-modal-body label{display:block;font-size:11px;font-weight:500;color:#9ca3af;margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px}' +
    '.ct-modal-body input,.ct-modal-body textarea{width:100%;padding:10px 12px;border-radius:6px;border:1px solid #333;' +
    'background:#1a1a1a;color:#e5e5e5;font-size:14px;font-family:inherit;outline:none;transition:border-color .15s}' +
    '.ct-modal-body input:focus,.ct-modal-body textarea:focus{border-color:#5b8def}' +
    '.ct-modal-body textarea{min-height:120px;resize:vertical;line-height:1.5}' +
    '.ct-field{margin-bottom:14px}' +
    '.ct-modal-footer{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;border-top:1px solid #333}' +
    '.ct-btn{padding:8px 16px;border-radius:6px;border:none;font-size:13px;font-weight:500;cursor:pointer;transition:all .12s}' +
    '.ct-btn-primary{background:#5b8def;color:#fff}' +
    '.ct-btn-primary:hover{background:#4a7de0}' +
    '.ct-btn-danger{background:transparent;color:#e55;border:1px solid #e55}' +
    '.ct-btn-danger:hover{background:#e55;color:#fff}' +
    '.ct-btn-ghost{background:transparent;color:#9ca3af}' +
    '.ct-btn-ghost:hover{color:#e5e7eb}';
  document.head.appendChild(style);

  /* ── Helpers ── */
  function escHtml(s) {
    var d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
  }

  /* ── Toast ── */
  var toast = document.createElement('div');
  toast.className = 'memory-toast';
  toast.innerHTML = '<span class="memory-toast-dot"></span><span class="memory-toast-text"></span>';

  var hideTimeout = null;

  function showToast(text) {
    toast.querySelector('.memory-toast-text').textContent = text;
    toast.classList.add('visible');
    if (hideTimeout) clearTimeout(hideTimeout);
    hideTimeout = setTimeout(function () { toast.classList.remove('visible'); }, 4000);
  }

  function connectSSE() {
    var es = new EventSource(API_BASE + '/api/v1/memory-events?scope_id=' + encodeURIComponent(SCOPE));
    es.onmessage = function (e) {
      try {
        var data = JSON.parse(e.data);
        if (data.type === 'connected') return;
        showToast('Память обновлена');
        if (_activeTab === 'instructions') loadInstructions();
      } catch (err) {}
    };
    es.onerror = function () {
      es.close();
      setTimeout(connectSSE, 10000);
    };
  }

  /* ── Agent Settings injection (Settings > Connections page) ── */
  function injectAgentSettings() {
    if (document.getElementById('ct-agent-settings')) return;
    // Find "Direct Connections" text node and insert before its parent section
    var allEls = document.querySelectorAll('div');
    var directConnDiv = null;
    for (var i = 0; i < allEls.length; i++) {
      var el = allEls[i];
      if (el.children.length === 0 && el.textContent.trim() === 'Direct Connections') {
        directConnDiv = el.closest('.my-2');
        break;
      }
    }
    if (!directConnDiv) return;

    // Load current value
    fetch(API_BASE + '/api/v1/agent/config')
      .then(function(r) { return r.json(); })
      .then(function(d) {
        var input = document.getElementById('ct-agent-tokens-input');
        if (input) input.value = d.max_agent_tokens || 128000;
      })
      .catch(function() {});

    var section = document.createElement('div');
    section.id = 'ct-agent-settings';
    section.className = 'my-2';
    section.innerHTML =
      '<div class="flex justify-between items-center text-sm">' +
        '<div class="font-medium">Agent Settings</div>' +
        '<span id="ct-agent-save-status" class="text-xs font-medium" style="display:none"></span>' +
      '</div>' +
      '<div class="mt-1 text-xs text-gray-400 dark:text-gray-500">' +
        'Token budget per agent request. The agent loop stops when cumulative tokens exceed this limit.' +
      '</div>' +
      '<div class="mt-2.5">' +
        '<div class="text-xs font-medium mb-1">Max Agent Tokens</div>' +
        '<div class="flex gap-2">' +
          '<input id="ct-agent-tokens-input" ' +
            'class="w-full rounded-lg py-1.5 px-4 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden" ' +
            'type="number" min="1000" max="1000000" step="1000" value="128000">' +
          '<button id="ct-agent-save-btn" ' +
            'class="px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 transition" ' +
            'type="button">Save</button>' +
        '</div>' +
      '</div>';

    // Insert: <hr> + section before Direct Connections
    var hr = document.createElement('hr');
    hr.className = 'border-gray-100/30 dark:border-gray-850/30 my-2';
    var parent = directConnDiv.parentNode;
    parent.insertBefore(hr, directConnDiv);
    parent.insertBefore(section, directConnDiv);

    document.getElementById('ct-agent-save-btn').addEventListener('click', function() {
      var val = parseInt(document.getElementById('ct-agent-tokens-input').value) || 128000;
      var status = document.getElementById('ct-agent-save-status');
      fetch(API_BASE + '/api/v1/agent/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_agent_tokens: val })
      })
        .then(function(r) { return r.json(); })
        .then(function(d) {
          document.getElementById('ct-agent-tokens-input').value = d.max_agent_tokens;
          status.textContent = 'Saved';
          status.style.display = '';
          status.style.color = '#22c55e';
          setTimeout(function() { status.style.display = 'none'; }, 2000);
        })
        .catch(function(e) {
          status.textContent = 'Error';
          status.style.display = '';
          status.style.color = '#ef4444';
          setTimeout(function() { status.style.display = 'none'; }, 3000);
        });
    });
  }

  var _agentSettingsInterval = null;
  function watchForSettingsPage() {
    if (_agentSettingsInterval) return;
    _agentSettingsInterval = setInterval(function() {
      if (!document.getElementById('ct-agent-settings')) {
        injectAgentSettings();
      }
    }, 200);
  }

  /* ── i18n patch: translate Memory admin page to Russian ── */
  var MEM_I18N = {
    'Manage Memories': 'Управление памятью',
    'Memories accessible by LLMs will be shown here.': 'Воспоминания, доступные ассистенту, будут отображаться здесь.',
    'Add Memory': 'Добавить',
    'Clear memory': 'Очистить память',
    'Loading...': 'Загрузка...'
  };
  var TYPE_RU = { user: 'Пользователь', project: 'Проект', reference: 'Ссылки' };
  var HDR_RU = { 'Name': 'Название', 'Type': 'Тип', 'Last Modified': 'Изменено', 'All': 'Все' };

  /* ── Instructions tab state ── */
  var _instructions = [];
  var _editingFilename = null;
  var _editingSource = null;
  var _activeTab = 'memory';

  /* ── Instructions CRUD ── */
  function loadInstructions() {
    fetch(API_BASE + '/api/v1/instructions?scope_id=' + encodeURIComponent(SCOPE))
      .then(function(r) { return r.json(); })
      .then(function(d) {
        _instructions = d.instructions || [];
        renderInstructions();
      })
      .catch(function(e) { console.error('Failed to load instructions', e); });
  }

  function renderInstructions() {
    var list = document.getElementById('ct-instr-list');
    if (!list) return;
    if (!_instructions.length) {
      list.innerHTML = '<div class="ct-empty">Пока нет инструкций</div>';
      return;
    }
    var SOURCE_LABELS = { auto: 'Авто', user: 'Ручная' };
    list.innerHTML = _instructions.map(function(item) {
      var badgeClass = item.source === 'auto' ? 'ct-badge-auto' : 'ct-badge-user';
      return '<div class="ct-instr-row" data-filename="' + escHtml(item.filename) + '">' +
        '<div class="ct-instr-info">' +
          '<div class="ct-instr-name">' + escHtml(item.name) + '</div>' +
          '<div class="ct-instr-desc">' + escHtml(item.description) + '</div>' +
        '</div>' +
        '<div class="ct-instr-meta">' +
          '<span class="ct-badge ' + badgeClass + '">' + (SOURCE_LABELS[item.source] || item.source) + '</span>' +
        '</div>' +
      '</div>';
    }).join('');
    // Wire click handlers
    var rows = list.querySelectorAll('.ct-instr-row');
    for (var i = 0; i < rows.length; i++) {
      rows[i].addEventListener('click', (function(fn) {
        return function() { openInstruction(fn); };
      })(rows[i].getAttribute('data-filename')));
    }
  }

  function openInstruction(filename) {
    var instr = null;
    for (var i = 0; i < _instructions.length; i++) {
      if (_instructions[i].filename === filename) { instr = _instructions[i]; break; }
    }
    if (!instr) return;
    _editingFilename = filename;
    _editingSource = instr.source;
    var isAuto = instr.source === 'auto';
    document.getElementById('ct-instr-modal-title').textContent = instr.name || 'Инструкция';
    document.getElementById('ct-instr-desc').value = instr.description || '';
    document.getElementById('ct-instr-body').value = instr.body || '';
    document.getElementById('ct-instr-desc').disabled = isAuto;
    document.getElementById('ct-instr-body').disabled = isAuto;
    document.getElementById('ct-instr-save-btn').style.display = isAuto ? 'none' : '';
    document.getElementById('ct-instr-delete-btn').style.display = '';
    document.getElementById('ct-instr-modal').classList.add('ct-visible');
  }

  function openNewInstruction() {
    _editingFilename = null;
    _editingSource = 'user';
    document.getElementById('ct-instr-modal-title').textContent = 'Новая инструкция';
    document.getElementById('ct-instr-desc').value = '';
    document.getElementById('ct-instr-body').value = '';
    document.getElementById('ct-instr-desc').disabled = false;
    document.getElementById('ct-instr-body').disabled = false;
    document.getElementById('ct-instr-save-btn').style.display = '';
    document.getElementById('ct-instr-delete-btn').style.display = 'none';
    document.getElementById('ct-instr-modal').classList.add('ct-visible');
  }

  function closeInstrModal() {
    document.getElementById('ct-instr-modal').classList.remove('ct-visible');
    _editingFilename = null;
    _editingSource = null;
  }

  function saveInstruction() {
    var desc = document.getElementById('ct-instr-desc').value.trim();
    var body = document.getElementById('ct-instr-body').value.trim();
    if (!body) { showToast('Заполните текст инструкции'); return; }
    var filename = _editingFilename || ('instr-' + Date.now() + '.md');
    var source = _editingSource || 'user';
    fetch(API_BASE + '/api/v1/instructions/' + encodeURIComponent(filename) + '?scope_id=' + encodeURIComponent(SCOPE), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: desc || body.slice(0, 200), body: body, source: source })
    })
      .then(function(r) {
        if (!r.ok) throw new Error('Save failed');
        return r.json();
      })
      .then(function() {
        closeInstrModal();
        showToast(_editingFilename ? 'Инструкция обновлена' : 'Инструкция добавлена');
        loadInstructions();
      })
      .catch(function() { showToast('Ошибка сохранения'); });
  }

  function deleteInstruction() {
    if (!_editingFilename || !confirm('Удалить эту инструкцию?')) return;
    fetch(API_BASE + '/api/v1/instructions/' + encodeURIComponent(_editingFilename) + '?scope_id=' + encodeURIComponent(SCOPE), {
      method: 'DELETE'
    })
      .then(function(r) {
        if (!r.ok) throw new Error('Delete failed');
        return r.json();
      })
      .then(function() {
        closeInstrModal();
        showToast('Инструкция удалена');
        loadInstructions();
      })
      .catch(function() { showToast('Ошибка удаления'); });
  }

  /* ── Inject Instructions Tab into Memory admin page ── */
  function injectInstructionsTab() {
    if (document.getElementById('ct-instructions-tab')) return;
    // Detect Memory page by finding the header div
    var allDivs = document.querySelectorAll('div');
    var headerDiv = null;
    for (var i = 0; i < allDivs.length; i++) {
      var el = allDivs[i];
      if (el.children.length === 0 && (el.textContent.trim() === 'Управление памятью' || el.textContent.trim() === 'Manage Memories')) {
        headerDiv = el;
        break;
      }
    }
    if (!headerDiv) return;

    // Find the scrollable container
    var container = headerDiv.closest('.scrollbar-hidden') || headerDiv.closest('[class*="overflow-y"]');
    if (!container) container = headerDiv.parentElement && headerDiv.parentElement.parentElement;
    if (!container) return;

    // Mark existing memory content as panel
    var memoryPanel = container.firstElementChild;
    if (!memoryPanel) return;
    memoryPanel.id = 'ct-panel-memory';

    // Create tab bar
    var tabBar = document.createElement('div');
    tabBar.id = 'ct-instructions-tab';
    tabBar.className = 'ct-tabs';
    tabBar.style.paddingLeft = '16px';
    tabBar.style.paddingRight = '16px';
    tabBar.innerHTML =
      '<button class="ct-tab ct-tab-active" data-ct-tab="memory">Память</button>' +
      '<button class="ct-tab" data-ct-tab="instructions">Инструкции</button>';
    container.insertBefore(tabBar, memoryPanel);

    // Create instructions panel (hidden)
    var instrPanel = document.createElement('div');
    instrPanel.id = 'ct-panel-instructions';
    instrPanel.style.display = 'none';
    instrPanel.style.padding = '16px';
    instrPanel.innerHTML =
      '<button class="ct-add-btn" id="ct-instr-add-btn">+ Добавить инструкцию</button>' +
      '<div id="ct-instr-list"></div>';
    container.appendChild(instrPanel);

    // Wire add button
    document.getElementById('ct-instr-add-btn').addEventListener('click', openNewInstruction);

    // Parent wrapper contains the bottom buttons (sibling of scrollable container)
    var wrapper = container.parentElement || container;

    // Tab click handler
    tabBar.addEventListener('click', function(e) {
      var btn = e.target.closest('.ct-tab');
      if (!btn) return;
      var tab = btn.getAttribute('data-ct-tab');
      _activeTab = tab;
      // Toggle active class
      var tabs = tabBar.querySelectorAll('.ct-tab');
      for (var j = 0; j < tabs.length; j++) {
        tabs[j].classList.toggle('ct-tab-active', tabs[j] === btn);
      }
      // Toggle panels
      memoryPanel.style.display = tab === 'memory' ? '' : 'none';
      instrPanel.style.display = tab === 'instructions' ? '' : 'none';
      // Hide Memory.svelte's bottom buttons when on Instructions tab
      var bottomBtns = wrapper.querySelectorAll('button');
      for (var k = 0; k < bottomBtns.length; k++) {
        var txt = bottomBtns[k].textContent.trim();
        if (txt === 'Добавить' || txt === 'Очистить память' || txt === 'Add Memory' || txt === 'Clear memory') {
          bottomBtns[k].style.display = tab === 'instructions' ? 'none' : '';
        }
      }
      if (tab === 'instructions') loadInstructions();
    });

    // Hide "Обратная связь" chip if present
    var chips = wrapper.querySelectorAll('button');
    for (var c = 0; c < chips.length; c++) {
      if (chips[c].textContent.trim() === 'Обратная связь') {
        chips[c].style.display = 'none';
      }
    }

    // Restore active tab state
    if (_activeTab === 'instructions') {
      tabBar.querySelector('[data-ct-tab="instructions"]').click();
    }
  }

  function patchMemoryTexts() {
    injectInstructionsTab();
  }

  var _patchObserver = new MutationObserver(function () { patchMemoryTexts(); });

  function init() {
    document.body.appendChild(toast);
    connectSSE();
    watchForSettingsPage();

    // Create instruction modal (once, on body)
    var modal = document.createElement('div');
    modal.id = 'ct-instr-modal';
    modal.className = 'ct-modal-overlay';
    modal.innerHTML =
      '<div class="ct-modal">' +
        '<div class="ct-modal-header">' +
          '<h3 id="ct-instr-modal-title">Инструкция</h3>' +
          '<button class="ct-modal-close" id="ct-instr-close-btn">&times;</button>' +
        '</div>' +
        '<div class="ct-modal-body">' +
          '<div class="ct-field">' +
            '<label>Описание</label>' +
            '<input type="text" id="ct-instr-desc" placeholder="Краткое описание правила">' +
          '</div>' +
          '<div class="ct-field">' +
            '<label>Правило</label>' +
            '<textarea id="ct-instr-body" placeholder="Текст инструкции"></textarea>' +
          '</div>' +
        '</div>' +
        '<div class="ct-modal-footer">' +
          '<button class="ct-btn ct-btn-danger" id="ct-instr-delete-btn" style="display:none">Удалить</button>' +
          '<div style="display:flex;gap:8px;margin-left:auto">' +
            '<button class="ct-btn ct-btn-ghost" id="ct-instr-cancel-btn">Отмена</button>' +
            '<button class="ct-btn ct-btn-primary" id="ct-instr-save-btn">Сохранить</button>' +
          '</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(modal);

    // Wire modal events
    document.getElementById('ct-instr-close-btn').addEventListener('click', closeInstrModal);
    document.getElementById('ct-instr-cancel-btn').addEventListener('click', closeInstrModal);
    document.getElementById('ct-instr-save-btn').addEventListener('click', saveInstruction);
    document.getElementById('ct-instr-delete-btn').addEventListener('click', deleteInstruction);
    modal.addEventListener('click', function(e) {
      if (e.target === modal) closeInstrModal();
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && modal.classList.contains('ct-visible')) closeInstrModal();
    });

    _patchObserver.observe(document.body, { childList: true, subtree: true });
    patchMemoryTexts();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

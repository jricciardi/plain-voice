(function () {
  'use strict';

  var isNode = typeof module !== 'undefined' && module.exports;

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c];
    });
  }

  function inlineMarkdown(text) {
    var s = escapeHtml(text);
    var code = [];
    s = s.replace(/`([^`]+)`/g, function (_, inner) {
      code.push('<code>' + inner + '</code>');
      return '\u0000C' + (code.length - 1) + '\u0000';
    });
    s = s.replace(/\[([^\]\n]+)\]\(([^)\n]+)\)/g, '<span class="fake-link">$1</span>');
    s = s.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
    s = s.replace(/(^|[^_])_([^_\n]+)_/g, '$1<em>$2</em>');
    s = s.replace(/\u0000C(\d+)\u0000/g, function (_, i) { return code[Number(i)]; });
    return s;
  }

  function isTableStart(lines, i) {
    return i + 1 < lines.length && /^\s*\|.+\|\s*$/.test(lines[i]) && /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(lines[i + 1]);
  }

  function splitTableRow(line) {
    var row = line.trim();
    if (row.charAt(0) === '|') row = row.slice(1);
    if (row.charAt(row.length - 1) === '|') row = row.slice(0, -1);
    return row.split('|').map(function (c) { return c.trim(); });
  }

  function renderTable(lines, start) {
    var html = '<table><thead><tr>';
    splitTableRow(lines[start]).forEach(function (cell) { html += '<th>' + inlineMarkdown(cell) + '</th>'; });
    html += '</tr></thead><tbody>';
    var i = start + 2;
    while (i < lines.length && /^\s*\|.+\|\s*$/.test(lines[i])) {
      html += '<tr>';
      splitTableRow(lines[i]).forEach(function (cell) { html += '<td>' + inlineMarkdown(cell) + '</td>'; });
      html += '</tr>';
      i++;
    }
    html += '</tbody></table>';
    return {html: html, next: i};
  }

  function listLevel(line) {
    var m = /^(\s*)([-*+] |\d+[.)] )/.exec(line);
    return m ? (m[1].length >= 2 ? 1 : 0) : -1;
  }

  function renderList(lines, start) {
    var ordered = /^\s*\d+[.)] /.test(lines[start]);
    var root = ordered ? 'ol' : 'ul';
    var html = '<' + root + '>';
    var i = start;
    var inNested = false;
    while (i < lines.length && listLevel(lines[i]) >= 0) {
      var level = listLevel(lines[i]);
      var text = lines[i].replace(/^\s*([-*+] |\d+[.)] )/, '');
      if (level === 0) {
        if (inNested) { html += '</ul></li>'; inNested = false; }
        html += '<li>' + inlineMarkdown(text);
      } else {
        if (!inNested) { html += '<ul>'; inNested = true; }
        html += '<li>' + inlineMarkdown(text) + '</li>';
      }
      if (level === 0) {
        var nextLevel = i + 1 < lines.length ? listLevel(lines[i + 1]) : -1;
        if (nextLevel !== 1) html += '</li>';
      }
      i++;
    }
    if (inNested) html += '</ul></li>';
    html += '</' + root + '>';
    return {html: html, next: i};
  }

  function renderMarkdown(src) {
    var lines = String(src == null ? '' : src).replace(/\r\n?/g, '\n').split('\n');
    var out = [];
    var i = 0;
    while (i < lines.length) {
      var line = lines[i];
      if (/^\s*$/.test(line)) { i++; continue; }
      if (/^```/.test(line.trim())) {
        var code = [];
        i++;
        while (i < lines.length && !/^```/.test(lines[i].trim())) { code.push(lines[i]); i++; }
        if (i < lines.length) i++;
        out.push('<pre><code>' + escapeHtml(code.join('\n')) + '</code></pre>');
        continue;
      }
      if (isTableStart(lines, i)) {
        var table = renderTable(lines, i);
        out.push(table.html);
        i = table.next;
        continue;
      }
      var hm = /^(#{1,6})\s+(.+)$/.exec(line);
      if (hm) {
        var level = hm[1].length;
        out.push('<h' + level + '>' + inlineMarkdown(hm[2]) + '</h' + level + '>');
        i++;
        continue;
      }
      if (/^\s*(---|\*\*\*|___)\s*$/.test(line)) { out.push('<hr>'); i++; continue; }
      if (/^\s*>\s?/.test(line)) {
        var quote = [];
        while (i < lines.length && /^\s*>\s?/.test(lines[i])) { quote.push(lines[i].replace(/^\s*>\s?/, '')); i++; }
        out.push('<blockquote>' + renderMarkdown(quote.join('\n')) + '</blockquote>');
        continue;
      }
      if (listLevel(line) >= 0) {
        var list = renderList(lines, i);
        out.push(list.html);
        i = list.next;
        continue;
      }
      var para = [line];
      i++;
      while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^```/.test(lines[i].trim()) && !isTableStart(lines, i) && !/^(#{1,6})\s+/.test(lines[i]) && !/^\s*(---|\*\*\*|___)\s*$/.test(lines[i]) && !/^\s*>\s?/.test(lines[i]) && listLevel(lines[i]) < 0) {
        para.push(lines[i]);
        i++;
      }
      out.push('<p>' + para.map(inlineMarkdown).join('<br>') + '</p>');
    }
    return out.join('\n');
  }

  if (isNode) {
    module.exports = { renderMarkdown: renderMarkdown, escapeHtml: escapeHtml };
    return;
  }

  var app = document.getElementById('app');
  var tagPop = document.getElementById('tag-pop');
  var state = {
    tasksDoc: null,
    flat: [],
    responsesDoc: {meta: {}, responses: {}},
    index: -1,
    started: false,
    raw: false,
    messageOpen: false,
    noteOpen: false,
    saveState: 'Saved',
    saveWarn: false,
    taskStartedAt: Date.now(),
    sectionIntrosSeen: {},
    inIntro: false,
    lastSelection: null,
    finishedSaved: false
  };

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function responseFor(id) { return state.responsesDoc.responses[id] || {}; }
  function currentItem() { return state.flat[state.index]; }
  function answeredCount() { return state.flat.filter(taskIsAnswered).length; }
  function setSave(label, warn) { state.saveState = label; state.saveWarn = !!warn; var el = $('.save-status'); if (el) { el.textContent = label; el.className = 'save-status ' + (warn ? 'warn' : (label === 'Saved' ? 'ok' : '')); } }
  function taskResponseKey() { var it = currentItem(); return it && it.task && it.task.id; }
  function isTypingTarget(el) { return el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable); }
  function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }

  function flatten(doc) {
    var out = [];
    (doc.sections || []).forEach(function (section) {
      (section.tasks || []).forEach(function (task, idx) {
        out.push({section: section, task: task, sectionTaskIndex: idx, sectionTaskCount: (section.tasks || []).length});
      });
    });
    return out;
  }

  function countsHtml() {
    return (state.tasksDoc.sections || []).map(function (s) {
      var n = (s.tasks || []).length;
      var label = s.kind === 'pair' ? 'pairs' : 'matches';
      return '<div><strong>' + escapeHtml(s.title || s.id) + '</strong>: ' + n + ' ' + label + '</div>';
    }).join('');
  }

  function estimateSeconds() {
    var sec = 0;
    (state.tasksDoc.sections || []).forEach(function (s) { sec += (s.tasks || []).length * (s.kind === 'match' ? 4 : 20); });
    return sec;
  }

  function fmtEstimate(sec) {
    var min = Math.max(1, Math.round(sec / 60));
    return min + ' minute' + (min === 1 ? '' : 's');
  }

  function taskIsAnswered(item) {
    var r = responseFor(item.task.id);
    if (item.section.kind === 'pair') return !!(r.prefer && r.ai_like);
    return !!r.verdict;
  }

  function findResumeIndex() {
    for (var i = 0; i < state.flat.length; i++) if (!taskIsAnswered(state.flat[i])) return i;
    return state.flat.length;
  }

  function renderStart() {
    var name = localStorage.getItem('reviewer_name') || (state.responsesDoc.meta && state.responsesDoc.meta.rater_name) || 'jay';
    app.innerHTML = '<main class="start card">' +
      '<h1>' + escapeHtml(state.tasksDoc.title || 'Blind review') + '</h1>' +
      '<p>Compare pairs of replies to the same message, then check flagged phrases.</p>' +
      '<p>Go with your gut. Everything saves as you go, so you can stop anytime.</p>' +
      '<div class="counts">' + countsHtml() + '</div>' +
      '<p class="muted">Estimated time: ' + fmtEstimate(estimateSeconds()) + '.</p>' +
      '<div class="name-row"><label for="name">Your name</label><input id="name" value="' + escapeHtml(name) + '" autocomplete="name"><button id="start" class="primary">Start <kbd>Enter</kbd></button></div>' +
      '<p class="muted">Resumes at the first unanswered item.</p>' +
      '</main>';
    $('#name').focus();
    $('#name').select();
    $('#start').addEventListener('click', startReview);
    $('#name').addEventListener('keydown', function (e) { if (e.key === 'Enter') startReview(); });
  }

  function startReview() {
    var name = $('#name').value.trim() || 'jay';
    localStorage.setItem('reviewer_name', name);
    saveMeta({rater_name: name, started_at: new Date().toISOString()});
    state.started = true;
    state.index = findResumeIndex();
    renderCurrent(true);
  }

  function topbarHtml() {
    var it = currentItem();
    var secDone = it ? it.sectionTaskIndex + 1 : 0;
    var secPct = it ? (secDone - 1) / Math.max(1, it.sectionTaskCount) * 100 : 100;
    var overallPct = state.flat.length ? (answeredCount() / state.flat.length) * 100 : 0;
    return '<div class="topbar"><div class="toprow">' +
      '<div class="section-title">' + escapeHtml(it ? it.section.title : 'All done') + '</div>' +
      '<div class="counter">' + (it ? (secDone + ' of ' + it.sectionTaskCount) : '') + ' · ' + answeredCount() + ' of ' + state.flat.length + ' overall</div>' +
      '<div class="save-status ' + (state.saveWarn ? 'warn' : 'ok') + '">' + escapeHtml(state.saveState) + '</div>' +
      '</div><div class="progress-row"><div class="progress" title="Section progress"><span style="width:' + clamp(secPct, 0, 100) + '%"></span></div>' +
      '<div class="progress" title="Overall progress"><span style="width:' + clamp(overallPct, 0, 100) + '%"></span></div></div></div>';
  }

  function renderCurrent(checkIntro) {
    state.inIntro = false;
    hideTagPop();
    if (state.index >= state.flat.length) { renderFinish(); return; }
    state.taskStartedAt = Date.now();
    var it = currentItem();
    if (checkIntro && it.sectionTaskIndex === 0 && !state.sectionIntrosSeen[it.section.id]) { renderIntro(it.section); return; }
    state.sectionIntrosSeen[it.section.id] = true;
    if (it.section.kind === 'pair') renderPair(it); else renderMatch(it);
  }

  function renderIntro(section) {
    state.inIntro = true;
    app.innerHTML = topbarHtml() + '<main class="intro-card"><h1>' + escapeHtml(section.title || '') + '</h1><p>' + escapeHtml(section.instructions || '') + '</p><button id="continue" class="primary">Continue <kbd>Enter</kbd></button></main>';
    $('#continue').focus();
    $('#continue').addEventListener('click', function () { state.inIntro = false; state.sectionIntrosSeen[section.id] = true; renderCurrent(false); });
  }

  function messageHtml(prompt) {
    var long = String(prompt || '').split('\n').length > 10 || String(prompt || '').length > 850;
    var collapsed = long && !state.messageOpen;
    return '<section class="message-panel card"><div class="panel-label">Message</div><div class="message-body markdown ' + (collapsed ? 'collapsed' : '') + '">' + renderMarkdown(prompt || '') + '</div>' + (long ? '<button class="small-btn" id="toggle-message">' + (collapsed ? 'Show all' : 'Collapse') + ' <kbd>M</kbd></button>' : '') + '</section>';
  }

  function replyCard(side, text, resp) {
    var tags = (resp.tags || []).filter(function (t) { return t.side === side; });
    var body = state.raw ? '<div class="raw-text">' + escapeHtml(text || '') + '</div>' : '<div class="reply-body markdown" data-side="' + side + '">' + renderMarkdown(text || '') + '</div>';
    return '<article class="reply-card" data-card-side="' + side + '"><div class="reply-head"><div class="reply-label">' + (side === 'left' ? 'Left' : 'Right') + '</div></div>' + body + '<div class="tags">' + tags.map(function (t, idx) { return '<span class="chip"><span>' + escapeHtml(t.text) + '</span><button data-remove-tag="' + side + ':' + idx + '" aria-label="Remove tag">×</button></span>'; }).join('') + '</div></article>';
  }

  function renderPair(it) {
    var t = it.task, resp = responseFor(t.id);
    app.innerHTML = topbarHtml() + '<main>' + messageHtml(t.prompt) + '<section class="reply-grid">' + replyCard('left', t.left, resp) + replyCard('right', t.right, resp) + '</section></main>' + answerBarHtml(resp);
    var msg = $('#toggle-message');
    if (msg) msg.addEventListener('click', function () { state.messageOpen = !state.messageOpen; renderPair(it); });
    bindAnswerButtons();
    bindTagRemoval();
    document.addEventListener('selectionchange', onSelectionChange);
  }

  function answerBarHtml(resp) {
    function b(group, value, label, key) {
      return '<button class="answer-btn ' + (resp[group] === value ? 'selected' : '') + '" data-group="' + group + '" data-value="' + value + '">' + label + ' <kbd>' + key + '</kbd></button>';
    }
    var noteField = state.noteOpen || resp.note || resp.flag ? '<div class="note-wrap"><input class="note-input" id="note" placeholder="Optional note" value="' + escapeHtml(resp.note || '') + '"><button class="small-btn" id="save-note">Save note</button></div>' : '';
    return '<div class="answerbar"><div class="answer-inner">' +
      '<div class="answer-row"><div class="answer-label">Which would you rather receive?</div>' + b('prefer', 'left', 'Left', '1') + b('prefer', 'tie', 'Tie', '2') + b('prefer', 'right', 'Right', '3') + '</div>' +
      '<div class="answer-row"><div class="answer-label">Which sounds more like stock AI?</div>' + b('ai_like', 'left', 'Left', 'Q') + b('ai_like', 'same', 'Same', 'W') + b('ai_like', 'right', 'Right', 'E') + '</div>' +
      '<div class="tools-row"><button class="small-btn ' + (resp.flag ? 'active' : '') + '" id="flag">Flag <kbd>F</kbd></button><button class="small-btn" id="note-btn">Note <kbd>N</kbd></button><button class="small-btn ' + (state.raw ? 'active' : '') + '" id="raw">Raw <kbd>R</kbd></button><button class="small-btn" id="help">Shortcuts <kbd>?</kbd></button><button class="small-btn" id="prev">← Previous</button><button class="small-btn" id="next">Next ↵</button>' + noteField + '</div>' +
      '</div></div>';
  }

  function bindAnswerButtons() {
    $all('.answer-btn').forEach(function (btn) { btn.addEventListener('click', function () { setPairAnswer(btn.dataset.group, btn.dataset.value); }); });
    $('#flag').addEventListener('click', toggleFlag);
    $('#note-btn').addEventListener('click', openNote);
    $('#raw').addEventListener('click', function () { state.raw = !state.raw; renderCurrent(false); });
    $('#help').addEventListener('click', showHelp);
    $('#prev').addEventListener('click', previousTask);
    $('#next').addEventListener('click', nextTask);
    var note = $('#note');
    if (note) {
      $('#save-note').addEventListener('click', saveNote);
      note.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); saveNote(); } if (e.key === 'Escape') { e.stopPropagation(); state.noteOpen = false; renderCurrent(false); } });
      if (state.noteOpen) note.focus();
    }
  }

  function normalizedPairResponse(base) {
    return {
      prefer: base.prefer || '',
      ai_like: base.ai_like || '',
      flag: !!base.flag,
      note: base.note || '',
      tags: Array.isArray(base.tags) ? base.tags : [],
      ms_on_task: (base.ms_on_task || 0) + Math.max(0, Date.now() - state.taskStartedAt)
    };
  }

  function setPairAnswer(group, value) {
    var id = taskResponseKey();
    var r = normalizedPairResponse(responseFor(id));
    r[group] = value;
    state.responsesDoc.responses[id] = r;
    saveResponse(id, r);
    renderCurrent(false);
    if (r.prefer && r.ai_like) {
      app.classList.add('flash');
      setTimeout(function () { app.classList.remove('flash'); nextTask(); }, 300);
    }
  }

  function toggleFlag() {
    var id = taskResponseKey();
    var r = normalizedPairResponse(responseFor(id));
    r.flag = !r.flag;
    state.noteOpen = r.flag;
    state.responsesDoc.responses[id] = r;
    saveResponse(id, r);
    renderCurrent(false);
  }

  function openNote() { state.noteOpen = true; renderCurrent(false); }

  function saveNote() {
    var id = taskResponseKey();
    var r = normalizedPairResponse(responseFor(id));
    var note = $('#note');
    r.note = note ? note.value : r.note;
    state.noteOpen = false;
    state.responsesDoc.responses[id] = r;
    saveResponse(id, r);
    renderCurrent(false);
  }

  function bindTagRemoval() {
    $all('[data-remove-tag]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var parts = btn.dataset.removeTag.split(':');
        var side = parts[0], idx = Number(parts[1]);
        var id = taskResponseKey();
        var r = normalizedPairResponse(responseFor(id));
        var seen = -1;
        r.tags = r.tags.filter(function (tag) {
          if (tag.side === side) { seen++; if (seen === idx) return false; }
          return true;
        });
        state.responsesDoc.responses[id] = r;
        saveResponse(id, r);
        renderCurrent(false);
      });
    });
  }

  function onSelectionChange() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || state.raw) { hideTagPop(); return; }
    var text = sel.toString().trim();
    if (!text) { hideTagPop(); return; }
    var node = sel.anchorNode;
    var el = node && (node.nodeType === 1 ? node : node.parentElement);
    var card = el && el.closest && el.closest('.reply-body[data-side]');
    if (!card) { hideTagPop(); return; }
    var rect = sel.getRangeAt(0).getBoundingClientRect();
    state.lastSelection = {side: card.dataset.side, text: text.slice(0, 500)};
    tagPop.style.left = Math.min(window.innerWidth - 170, Math.max(12, rect.left)) + 'px';
    tagPop.style.top = Math.max(12, rect.top - 44) + 'px';
    tagPop.classList.remove('hidden');
  }

  function hideTagPop() { tagPop.classList.add('hidden'); state.lastSelection = null; }

  function addTagFromSelection() {
    if (!state.lastSelection) return;
    var id = taskResponseKey();
    var r = normalizedPairResponse(responseFor(id));
    r.tags.push({side: state.lastSelection.side, text: state.lastSelection.text});
    state.responsesDoc.responses[id] = r;
    saveResponse(id, r);
    window.getSelection().removeAllRanges();
    hideTagPop();
    renderCurrent(false);
  }
  tagPop.addEventListener('click', addTagFromSelection);
  tagPop.addEventListener('keydown', function (e) { if (e.key.toLowerCase() === 't' || e.key === 'Enter') addTagFromSelection(); });

  function renderMatch(it) {
    var t = it.task;
    var v = responseFor(t.id).verdict;
    function mb(value, label, key) { return '<button class="answer-btn ' + (v === value ? 'selected' : '') + '" data-verdict="' + value + '">' + label + ' <kbd>' + key + '</kbd></button>'; }
    app.innerHTML = topbarHtml() + '<main class="match-card card"><div class="tell-name">' + escapeHtml(t.tell || '') + '</div><div class="muted">' + escapeHtml(t.tell_help || '') + '</div><div class="snippet">' + escapeHtml(t.before || '') + '<mark>' + escapeHtml(t.match || '') + '</mark>' + escapeHtml(t.after || '') + '</div><div class="match-buttons">' + mb('yes', 'Yes, real example', 'Y') + mb('no', 'No, false alarm', 'N') + mb('unsure', 'Unsure', 'U') + '</div><p><button class="small-btn" id="prev">← Previous</button> <button class="small-btn" id="help">Shortcuts <kbd>?</kbd></button></p></main>';
    $all('[data-verdict]').forEach(function (btn) { btn.addEventListener('click', function () { setMatchVerdict(btn.dataset.verdict); }); });
    $('#prev').addEventListener('click', previousTask);
    $('#help').addEventListener('click', showHelp);
  }

  function setMatchVerdict(verdict) {
    var id = taskResponseKey();
    var prior = responseFor(id);
    var r = { verdict: verdict, ms_on_task: (prior.ms_on_task || 0) + Math.max(0, Date.now() - state.taskStartedAt) };
    state.responsesDoc.responses[id] = r;
    saveResponse(id, r);
    app.classList.add('flash');
    setTimeout(function () { app.classList.remove('flash'); nextTask(); }, 120);
  }

  function nextTask() { state.index = Math.min(state.flat.length, state.index + 1); state.messageOpen = false; state.noteOpen = false; renderCurrent(true); }
  function previousTask() { state.index = Math.max(0, state.index - 1); state.messageOpen = false; state.noteOpen = false; renderCurrent(false); }

  function renderFinish() {
    if (!state.finishedSaved) { state.finishedSaved = true; saveMeta({finished_at: new Date().toISOString()}); }
    var per = (state.tasksDoc.sections || []).map(function (s) {
      var ids = (s.tasks || []).map(function (t) { return t.id; });
      var n = ids.filter(function (id) { return !!state.responsesDoc.responses[id]; }).length;
      return '<div><strong>' + escapeHtml(s.title || s.id) + '</strong>: ' + n + ' of ' + ids.length + '</div>';
    }).join('');
    app.innerHTML = topbarHtml() + '<main class="finish card"><h1>All done</h1><div class="counts">' + per + '</div><button id="download" class="primary">Download a copy</button><p class="muted">Your work has been saved. You can close this tab.</p><p><button class="small-btn" id="prev">← Previous</button></p></main>';
    $('#download').addEventListener('click', downloadResponses);
    $('#prev').addEventListener('click', previousTask);
  }

  function downloadResponses() {
    var blob = new Blob([JSON.stringify(state.responsesDoc, null, 2) + '\n'], {type: 'application/json'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'responses.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 100);
  }

  function showHelp() {
    var div = document.createElement('div');
    div.className = 'overlay';
    div.innerHTML = '<div class="overlay-card"><h2>Keyboard shortcuts</h2><ul class="shortcuts"><li><kbd>1</kbd>/<kbd>2</kbd>/<kbd>3</kbd> prefer Left/Tie/Right</li><li><kbd>Q</kbd>/<kbd>W</kbd>/<kbd>E</kbd> stock AI Left/Same/Right</li><li><kbd>Y</kbd>/<kbd>N</kbd>/<kbd>U</kbd> match verdict</li><li><kbd>→</kbd> or <kbd>Enter</kbd> next</li><li><kbd>←</kbd> previous</li><li><kbd>F</kbd> flag pair</li><li><kbd>N</kbd> note</li><li><kbd>T</kbd> tag selected text</li><li><kbd>R</kbd> raw replies</li><li><kbd>M</kbd> show/collapse message</li><li><kbd>Esc</kbd> close</li></ul><button class="primary">Close</button></div>';
    document.body.appendChild(div);
    $('button', div).focus();
    function close(e) { if (!e || e.key === 'Escape' || e.target === div || e.target.tagName === 'BUTTON') { div.remove(); document.removeEventListener('keydown', close); } }
    div.addEventListener('click', close);
    document.addEventListener('keydown', close);
  }

  function queueItem(method, url, body) {
    var q = JSON.parse(localStorage.getItem('review_retry_queue') || '[]');
    q.push({method: method, url: url, body: body, queued_at: new Date().toISOString()});
    localStorage.setItem('review_retry_queue', JSON.stringify(q));
  }

  function saveResponse(id, response) {
    setSave('Saving…', false);
    return fetch('/api/responses/' + encodeURIComponent(id), {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(response)}).then(function (r) {
      if (!r.ok) throw new Error('save failed');
      return r.json();
    }).then(function () { setSave('Saved', false); }).catch(function () { queueItem('POST', '/api/responses/' + encodeURIComponent(id), response); setSave('Offline — retrying', true); });
  }

  function saveMeta(meta) {
    Object.assign(state.responsesDoc.meta, meta);
    return fetch('/api/meta', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(meta)}).then(function (r) {
      if (!r.ok) throw new Error('meta save failed');
      setSave('Saved', false);
    }).catch(function () { queueItem('POST', '/api/meta', meta); setSave('Offline — retrying', true); });
  }

  function retryQueue() {
    var q = JSON.parse(localStorage.getItem('review_retry_queue') || '[]');
    if (!q.length) return;
    var remaining = [];
    var chain = Promise.resolve();
    q.forEach(function (item) {
      chain = chain.then(function () {
        return fetch(item.url, {method: item.method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(item.body)}).then(function (r) { if (!r.ok) throw new Error('retry failed'); }).catch(function () { remaining.push(item); });
      });
    });
    chain.then(function () { localStorage.setItem('review_retry_queue', JSON.stringify(remaining)); setSave(remaining.length ? 'Offline — retrying' : 'Saved', !!remaining.length); });
  }

  function globalKeys(e) {
    if (isTypingTarget(e.target)) return;
    var key = e.key;
    var it = currentItem();
    if ($('.overlay')) return;
    if (!state.started) return;
    if (key === '?') { e.preventDefault(); showHelp(); return; }
    if (state.inIntro) {
      if (key === 'Enter' || key === 'ArrowRight') {
        e.preventDefault();
        var introItem = currentItem();
        if (introItem) state.sectionIntrosSeen[introItem.section.id] = true;
        state.inIntro = false;
        renderCurrent(false);
      }
      if (key === 'ArrowLeft') previousTask();
      return;
    }
    if (state.index >= state.flat.length) { if (key === 'ArrowLeft') previousTask(); return; }
    if (key === 'ArrowRight' || key === 'Enter') { e.preventDefault(); nextTask(); return; }
    if (key === 'ArrowLeft') { e.preventDefault(); previousTask(); return; }
    if (!it) return;
    if (it.section.kind === 'pair') {
      var lower = key.toLowerCase();
      if (key === '1') setPairAnswer('prefer', 'left');
      else if (key === '2') setPairAnswer('prefer', 'tie');
      else if (key === '3') setPairAnswer('prefer', 'right');
      else if (lower === 'q') setPairAnswer('ai_like', 'left');
      else if (lower === 'w') setPairAnswer('ai_like', 'same');
      else if (lower === 'e') setPairAnswer('ai_like', 'right');
      else if (lower === 'f') toggleFlag();
      else if (lower === 'n') openNote();
      else if (lower === 'r') { state.raw = !state.raw; renderCurrent(false); }
      else if (lower === 'm') { state.messageOpen = !state.messageOpen; renderCurrent(false); }
      else if (lower === 't') addTagFromSelection();
    } else {
      var k = key.toLowerCase();
      if (k === 'y') setMatchVerdict('yes');
      else if (k === 'n') setMatchVerdict('no');
      else if (k === 'u') setMatchVerdict('unsure');
    }
  }

  function init() {
    Promise.all([
      fetch('/api/tasks').then(function (r) { if (!r.ok) throw new Error('tasks failed'); return r.json(); }),
      fetch('/api/responses').then(function (r) { if (!r.ok) throw new Error('responses failed'); return r.json(); })
    ]).then(function (pair) {
      state.tasksDoc = pair[0];
      state.responsesDoc = pair[1] || {meta: {}, responses: {}};
      state.responsesDoc.meta = state.responsesDoc.meta || {};
      state.responsesDoc.responses = state.responsesDoc.responses || {};
      state.flat = flatten(state.tasksDoc);
      renderStart();
      document.addEventListener('keydown', globalKeys);
      setInterval(retryQueue, 3500);
      retryQueue();
    }).catch(function (err) {
      app.innerHTML = '<main class="start card"><h1>Could not load review</h1><p class="muted">' + escapeHtml(err.message) + '</p></main>';
    });
  }

  init();
}());

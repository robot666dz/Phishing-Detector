

//  Конфигурация 
const CONFIG = {
  API_BASE: 'http://localhost:5000/api',
  DEMO_MODE: false  // true = работает без бэкенда (демо)
};

//  Примеры сообщений 
const MSG_EXAMPLES = {
  1: {
    sender: 'Сбербанк',
    message: `Уважаемый клиент! Ваш аккаунт СберБанк Онлайн заблокирован в связи с подозрительной активностью. Для разблокировки СРОЧНО перейдите по ссылке и введите ваши данные: http://sber-online.tk/verify?action=unblock&token=abc123. Код подтверждения действителен только 2 часа. Служба безопасности Сбербанк.`
  },
  2: {
    sender: 'Russian Loto',
    message: `Поздравляем! Вы выиграли 500 000 рублей в государственной лотерее! Ваш номер: 7741-RUS. Для получения выплаты немедленно перейдите: http://win-rus-loto.xyz/claim и введите данные банковской карты. Акция ограничена — только 24 часа!`
  },
  3: {
    sender: 'noreply@vtb-bank.cc',
    message: `Дорогой клиент ВТБ Банка. Нам необходимо подтвердить вашу личность в связи с новыми требованиями ЦБ РФ. Перейдите по ссылке и введите логин, пароль и CVV вашей карты: https://vtb-online.site/confirm_identity Срок — до конца сегодняшнего дня, иначе счет будет заблокирован.`
  }
};

//  DOM элементы 
const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

//  Инициализация 
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initForms();
  initCharCounter();
  animateHeroStats();
});

 
// ТАБЫ

function initTabs() {
  const tabBtns = $$('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.target;
      tabBtns.forEach(b => b.classList.remove('active'));
      $$('.panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      $(`panel-${target}`).classList.add('active');
      hideResults();
    });
  });

  const resultTabs = $$('.rtab');
  resultTabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.rtab;
      resultTabs.forEach(b => b.classList.remove('active'));
      $$('.rpanel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      $(`rpanel-${target}`).classList.add('active');
    });
  });
}

 
// ФОРМЫ
 
function initForms() {
  $('url-form').addEventListener('submit', e => {
    e.preventDefault();
    const url = $('url-input').value.trim();
    if (!url) return showError('Введите URL для проверки');
    analyzeURL(url);
  });

  $('msg-form').addEventListener('submit', e => {
    e.preventDefault();
    const msg = $('message-input').value.trim();
    if (!msg) return showError('Введите текст сообщения');
    const sender = $('sender-input').value.trim();
    analyzeMessage(msg, sender);
  });

  $('full-form').addEventListener('submit', e => {
    e.preventDefault();
    const url = $('full-url-input').value.trim();
    const msg = $('full-msg-input').value.trim();
    const sender = $('full-sender-input').value.trim();
    if (!url && !msg) return showError('Введите URL или текст сообщения');
    analyzeFull(url, msg, sender);
  });
}

function initCharCounter() {
  $('message-input').addEventListener('input', function() {
    $('char-count').textContent = this.value.length;
  });
}


// API ЗАПРОСЫ

async function analyzeURL(url) {
  showLoading('URL');
  try {
    if (CONFIG.DEMO_MODE) {
      await delay(3200);
      const result = generateDemoURLResult(url);
      hideLoading();
      displayResults(result, 'url');
    } else {
      const res = await fetch(`${CONFIG.API_BASE}/analyze/url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const result = await res.json();
      hideLoading();
      if (result.error) return showError(result.error);
      displayResults(result, 'url');
    }
  } catch (err) {
    hideLoading();
    // Если нет бэкенда — автоматически переключаемся в демо-режим
    const result = generateDemoURLResult(url);
    displayResults(result, 'url');
  }
}

async function analyzeMessage(message, sender) {
  showLoading('сообщение');
  try {
    if (CONFIG.DEMO_MODE) {
      await delay(2800);
      const result = generateDemoMessageResult(message, sender);
      hideLoading();
      displayResults(result, 'message');
    } else {
      const res = await fetch(`${CONFIG.API_BASE}/analyze/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, sender })
      });
      const result = await res.json();
      hideLoading();
      if (result.error) return showError(result.error);
      displayResults(result, 'message');
    }
  } catch (err) {
    hideLoading();
    const result = generateDemoMessageResult(message, sender);
    displayResults(result, 'message');
  }
}

async function analyzeFull(url, message, sender) {
  showLoading('полный анализ');
  try {
    if (CONFIG.DEMO_MODE) {
      await delay(4000);
      const result = generateDemoFullResult(url, message, sender);
      hideLoading();
      displayResults(result, 'full');
    } else {
      const res = await fetch(`${CONFIG.API_BASE}/analyze/full`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, message, sender })
      });
      const result = await res.json();
      hideLoading();
      if (result.error) return showError(result.error);
      displayResults(result, 'full');
    }
  } catch (err) {
    hideLoading();
    const result = generateDemoFullResult(url, message, sender);
    displayResults(result, 'full');
  }
}


// ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ

function displayResults(data, type) {
  const results = $('results');
  results.style.display = 'block';
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Meta
  $('report-id').textContent = `ID: ${data.report_id || 'DEMO'}`;
  $('report-time').textContent = new Date().toLocaleString('ru-RU');

  // Получаем главную оценку
  let score, level, verdict, recommend;

  if (type === 'full' && data.combined) {
    score = data.combined.risk_score;
    level = data.combined.risk_level;
    verdict = data.combined.verdict;
    recommend = data.combined.recommendation;
  } else if (type === 'message' && data.message_analysis) {
    score = data.message_analysis.risk_score;
    level = data.message_analysis.risk_level;
    verdict = data.message_analysis.verdict;
    recommend = data.message_analysis.recommendation;
  } else if (type === 'url' && data.url_analysis) {
    score = data.url_analysis.risk_score;
    level = data.url_analysis.risk_level;
    verdict = data.url_analysis.verdict;
    recommend = data.url_analysis.recommendation;
  } else {
    score = data.risk_score || 0;
    level = data.risk_level || 'БЕЗОПАСНЫЙ';
    verdict = data.verdict || '—';
    recommend = data.recommendation || '—';
  }

  // Score ring animation
  animateScore(score, level);

  // Badge + text
  const badgeClass = getBadgeClass(level);
  $('verdict-badge').className = `verdict-badge ${badgeClass}`;
  $('verdict-badge').textContent = level;
  $('verdict-text').textContent = verdict;
  $('verdict-text').className = `verdict-text ${getRiskColorClass(level)}`;
  $('verdict-recommend').textContent = recommend;

  // Нормализуем данные для отображения
  const normalData = normalizeData(data, type);

  // Заполняем панели
  renderChecks(normalData.checks);
  renderWhois(normalData.whois);
  renderAI(normalData.ai_analysis);
  renderFindings(normalData.findings);

  // Активируем первую вкладку
  $$('.rtab').forEach(b => b.classList.remove('active'));
  $$('.rpanel').forEach(p => p.classList.remove('active'));
  $$('.rtab')[0].classList.add('active');
  $('rpanel-checks').classList.add('active');
}

function normalizeData(data, type) {
  // 
  let originalMsg = '';
  if (type === 'message') originalMsg = $('message-input').value;
  if (type === 'full') originalMsg = $('full-msg-input').value;

  // 
  const urlRegex = /(?:https?:\/\/)?(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)/gi;
  const extractedUrls = originalMsg ? (originalMsg.match(urlRegex) || []) : [];

  // 
  const patchFindings = (findings) => {
    if (!findings) return [];
    return findings.map(f => {
      // 
      if (f.category === 'Ссылки в сообщении' && extractedUrls.length > 0) {
        return { ...f, message: `Найдено ${extractedUrls.length} ссылок: ${extractedUrls.join(', ')}` };
      }
      // 
      if (f.category === 'Несоответствие отправителя' && f.message.includes("на ''") && extractedUrls.length > 0) {
        return { ...f, message: f.message.replace("на ''", `на '${extractedUrls[0]}'`) };
      }
      return f;
    });
  };

  if (type === 'url') {
    return {
      checks: data.checks || {},
      whois: data.whois || {},
      ai_analysis: data.ai_analysis || {},
      findings: data.findings || []
    };
  }
  
  if (type === 'message') {
    return {
      checks: {
        keywords: { status: (data.keywords_found?.russian?.length > 0) ? 'fail' : 'pass',
                    message: `Найдено ${data.keywords_found?.russian?.length || 0} фишинговых слов` },
        sender: { status: 'pass', message: data.sender || 'Не указан' },
        urls: { status: (extractedUrls.length > 0) ? 'warn' : 'pass',
                message: `Ссылок в сообщении: ${extractedUrls.length}` },
        urgency: { status: 'unknown', message: 'Анализ давления и срочности' },
        data_request: { status: 'unknown', message: 'Проверка запросов личных данных' }
      },
      whois: { status: 'info', message: 'WHOIS недоступен для анализа сообщений' },
      ai_analysis: data.ai_analysis || {},
      // 
      findings: patchFindings(data.findings) 
    };
  }
  
  // full
  const urlData = data.url_analysis || {};
  const msgData = data.message_analysis || {};
  return {
    checks: { ...urlData.checks, ...{ keywords: msgData.checks?.keywords } },
    whois: urlData.whois || {},
    ai_analysis: urlData.ai_analysis || msgData.ai_analysis || {},
    // 
    findings: patchFindings([...(urlData.findings || []), ...(msgData.findings || [])])
  };
}

//   
function renderChecks(checks) {
  const grid = $('checks-grid');
  grid.innerHTML = '';

  const checkLabels = {
    ssl: { icon: '🔐', name: 'SSL / HTTPS' },
    tld: { icon: '🌐', name: 'Домен TLD' },
    shortener: { icon: '🔗', name: 'Сокращение URL' },
    ip_url: { icon: '📡', name: 'IP вместо домена' },
    spoofing: { icon: '🎭', name: 'Спуфинг домена' },
    reputation: { icon: '⭐', name: 'Репутация' },
    keywords: { icon: '🔍', name: 'Ключевые слова' },
    sender: { icon: '👤', name: 'Отправитель' },
    urls: { icon: '🔗', name: 'Ссылки в тексте' },
    urgency: { icon: '⏱', name: 'Давление/срочность' },
    data_request: { icon: '📋', name: 'Запрос данных' },
    whois: { icon: '📜', name: 'WHOIS' },
  };

  if (!checks || Object.keys(checks).length === 0) {
    grid.innerHTML = '<div style="color:var(--text3);font-size:14px;padding:20px">Данные проверок недоступны</div>';
    return;
  }

  Object.entries(checks).forEach(([key, val]) => {
    if (!val || key === 'whois') return;
    const meta = checkLabels[key] || { icon: '🔎', name: key };
    const status = val.status || 'unknown';
    const statusClass = { pass: 'check-pass', fail: 'check-fail', warn: 'check-warn' }[status] || 'check-unknown';

    const item = document.createElement('div');
    item.className = `check-item ${statusClass}`;
    item.innerHTML = `
      <div class="check-icon"></div>
      <div>
        <div class="check-name">${meta.name}</div>
        <div class="check-msg">${val.message || '—'}</div>
      </div>`;
    grid.appendChild(item);
  });

  if (grid.children.length === 0) {
    grid.innerHTML = '<div style="color:var(--text3);font-size:14px;padding:20px">Нет данных о проверках</div>';
  }
}

//  WHOIS 
function renderWhois(whois) {
  const table = $('whois-table');
  if (!whois || whois.status === 'error' || whois.status === 'info') {
    table.innerHTML = `<div style="padding:20px;color:var(--text2);font-size:14px;grid-column:1/-1">
      ${whois?.message || 'Данные WHOIS недоступны для данного запроса'}
    </div>`;
    return;
  }

  const rows = [
    ['Домен', whois.domain || '—'],
    ['Дата регистрации', whois.creation_date || '—'],
    ['Возраст домена', whois.domain_age_str || '—'],
    ['Дата истечения', whois.expiration_date || '—'],
    ['Регистратор', whois.registrar || '—'],
    ['Страна', whois.country || '—'],
    ['IP-адрес', whois.ip_address || '—'],
    ['DNS-серверы', (whois.name_servers || []).join(', ') || '—'],
    ['Легитимный домен РФ', whois.is_known_legitimate ? `✅ Да (${whois.known_as || ''})` : '❌ Нет в базе'],
  ];

  table.innerHTML = rows.map(([label, value]) => `
    <div class="wrow-label">${label}</div>
    <div class="wrow-value">${value}</div>
  `).join('');
}

//  AI 
function renderAI(ai) {
  const box = $('ai-response');
  box.innerHTML = `
    <div class="ai-header">
      🤖 Анализ искусственного интеллекта
      <span style="color:var(--text3);font-weight:400;font-size:11px">(GIGACHAT AI)</span>
    </div>
    <div class="ai-text ${ai?.status === 'error' ? 'ai-error' : ''}">
      ${ai?.analysis || 'ИИ-анализ недоступен'}
    </div>`;
}

//  Findings 
function renderFindings(findings) {
  const list = $('findings-list');
  if (!findings || findings.length === 0) {
    list.innerHTML = '<div style="color:var(--text3);font-size:14px;padding:20px;text-align:center">✅ Подозрительных признаков не обнаружено</div>';
    return;
  }

  // Сортировка по важности
  const sorted = [...findings].sort((a, b) => {
    const order = { danger: 0, warning: 1, info: 2, success: 3 };
    return (order[a.type] || 2) - (order[b.type] || 2);
  });

  const icons = { danger: '🚨', warning: '⚠️', success: '✅', info: 'ℹ️' };

  list.innerHTML = sorted.map(f => `
    <div class="finding-item finding-${f.type || 'info'}">
      <div class="finding-icon">${icons[f.type] || 'ℹ️'}</div>
      <div class="finding-body">
        <div class="finding-cat">${f.category || ''}</div>
        <div class="finding-msg">${f.message}</div>
        ${f.weight && f.weight !== 0 ? `<div class="finding-weight">Вес: ${f.weight > 0 ? '+' : ''}${f.weight} баллов</div>` : ''}
      </div>
    </div>
  `).join('');
}


// LOADING

function showLoading(type) {
  hideResults();
  $('loading').style.display = 'flex';
  $('loading').scrollIntoView({ behavior: 'smooth', block: 'center' });

  // Анимация шагов
  const steps = [1, 2, 3, 4];
  steps.forEach(i => {
    const el = $(`ls-${i}`);
    el.className = 'lstep';
  });

  let current = 1;
  const stepInterval = setInterval(() => {
    if (current > 1) {
      const prev = $(`ls-${current - 1}`);
      if (prev) { prev.className = 'lstep done'; prev.textContent = '✓ ' + prev.textContent.slice(2); }
    }
    if (current <= 4) {
      const cur = $(`ls-${current}`);
      if (cur) cur.className = 'lstep active';
      current++;
    } else {
      clearInterval(stepInterval);
    }
  }, 700);

  window._loadingInterval = stepInterval;
}

function hideLoading() {
  if (window._loadingInterval) clearInterval(window._loadingInterval);
  $('loading').style.display = 'none';
}

function hideResults() {
  $('results').style.display = 'none';
}


// АНИМАЦИИ

function animateScore(score, level) {
  const fill = $('score-ring-fill');
  const numEl = $('score-number');
  const circumference = 327;

  // Цвет кольца
  const colors = {
    'БЕЗОПАСНЫЙ': '#2ECC71',
    'НИЗКИЙ': '#8BC34A',
    'СРЕДНИЙ': '#F39C12',
    'ВЫСОКИЙ': '#E67E22',
    'КРИТИЧЕСКИЙ': '#E63946'
  };
  fill.style.stroke = colors[level] || '#E63946';

  // Анимация числа
  let currentNum = 0;
  const step = score / 40;
  const numInterval = setInterval(() => {
    currentNum = Math.min(currentNum + step, score);
    numEl.textContent = Math.round(currentNum);
    numEl.className = `score-number ${getRiskColorClass(level)}`;
    if (currentNum >= score) clearInterval(numInterval);
  }, 25);

  // Анимация кольца
  const offset = circumference - (score / 100) * circumference;
  setTimeout(() => { fill.style.strokeDashoffset = offset; }, 100);
}

function animateHeroStats() {
  const stats = document.querySelectorAll('.stat-num');
  stats.forEach(el => {
    const target = parseInt(el.textContent.replace(/[^0-9]/g, ''));
    if (isNaN(target)) return;
    let current = 0;
    const step = target / 50;
    const suffix = el.textContent.includes('%') ? '%' : '';
    const interval = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = Math.round(current) + suffix;
      if (current >= target) clearInterval(interval);
    }, 30);
  });
}


// ВСПОМОГАТЕЛЬНЫЕ

function getBadgeClass(level) {
  const map = {
    'БЕЗОПАСНЫЙ': 'badge-safe',
    'НИЗКИЙ': 'badge-low',
    'СРЕДНИЙ': 'badge-medium',
    'ВЫСОКИЙ': 'badge-high',
    'КРИТИЧЕСКИЙ': 'badge-critical'
  };
  return map[level] || 'badge-medium';
}

function getRiskColorClass(level) {
  const map = {
    'БЕЗОПАСНЫЙ': 'risk-safe',
    'НИЗКИЙ': 'risk-low',
    'СРЕДНИЙ': 'risk-medium',
    'ВЫСОКИЙ': 'risk-high',
    'КРИТИЧЕСКИЙ': 'risk-critical'
  };
  return map[level] || '';
}

function clearInput(id) {
  $(id).value = '';
  $(id).focus();
}

function setExample(type, value) {
  if (type === 'url') {
    $('url-input').value = value;
    $('url-input').focus();
  }
}

function loadMsgExample(num) {
  const ex = MSG_EXAMPLES[num];
  if (!ex) return;
  $('sender-input').value = ex.sender;
  $('message-input').value = ex.message;
  $('char-count').textContent = ex.message.length;
}

function showError(msg) {
  alert('⚠️ ' + msg);
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


// ДЕМО-ГЕНЕРАТОР 

function generateDemoURLResult(url) {
  const suspiciousPatterns = [
    /\.tk$/, /\.xyz$/, /\.online$/, /\.site$/, /\.ml$/,
    /sber[^.]*\.(?!ru)/, /gosuslugi[^.]*\.(?!ru)/,
    /vtb[^.]*\.(?!ru)/, /tinkoff[^.]*\.(?!ru)/,
    /bank.*\.(tk|xyz|site|online|ml|cc)/,
    /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,
    /bit\.ly|tinyurl|goo\.gl/
  ];

  const legitimateDomains = [
    'gosuslugi.ru', 'sberbank.ru', 'sber.ru', 'vtb.ru',
    'alfabank.ru', 'tinkoff.ru', 'nalog.ru', 'mos.ru',
    'cbr.ru', 'mail.ru', 'yandex.ru', 'vk.com'
  ];

  let score = 0;
  const findings = [];
  const checks = {};

  let domain = url.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0].split('?')[0].toLowerCase();
  const baseDomain = domain.split('.').slice(-2).join('.');

  // HTTP
  if (!url.startsWith('https://')) {
    score += 15;
    findings.push({ type: 'warning', category: 'Протокол', message: 'Используется незащищённый HTTP протокол', weight: 15 });
    checks.ssl = { status: 'fail', message: 'Нет SSL/TLS шифрования' };
  } else {
    checks.ssl = { status: 'pass', message: 'HTTPS шифрование активно' };
  }

  // Suspicious patterns
  let isSuspicious = false;
  suspiciousPatterns.forEach(p => {
    if (p.test(url.toLowerCase())) isSuspicious = true;
  });

  if (isSuspicious) {
    score += 55;
    findings.push({ type: 'danger', category: 'Структура URL', message: 'Обнаружены признаки фишинговой ссылки', weight: 55 });
    checks.spoofing = { status: 'fail', message: 'Подозрительный домен' };
    checks.tld = { status: 'fail', message: 'Высокорисковый домен' };
  } else {
    checks.spoofing = { status: 'pass', message: 'Споофинг не обнаружен' };
    checks.tld = { status: 'pass', message: 'Нормальный TLD' };
  }

  // Legitimate
  if (legitimateDomains.includes(baseDomain)) {
    score = Math.max(0, score - 40);
    findings.push({ type: 'success', category: 'Репутация', message: `Верифицированный домен РФ: ${baseDomain}`, weight: -40 });
    checks.reputation = { status: 'pass', message: 'Официальный домен' };
  } else {
    checks.reputation = { status: 'unknown', message: 'Домен не в базе РФ' };
  }

  checks.shortener = { status: 'pass', message: 'Прямая ссылка' };
  checks.ip_url = { status: 'pass', message: 'Доменное имя используется' };

  score = Math.min(100, Math.max(0, score));
  const level = getLevel(score);

  return {
    url, domain, base_domain: baseDomain,
    risk_score: score, risk_level: level,
    verdict: getVerdict(score),
    recommendation: getRecommendation(score),
    findings, checks,
    whois: generateDemoWhois(domain, isSuspicious),
    ai_analysis: {
      status: 'success',
      analysis: generateAIText(url, score, level),
      model: 'GigaChat'
    },
    report_id: generateID()
  };
}

function generateDemoMessageResult(message, sender) {
  const msgLower = message.toLowerCase();
  let score = 0;
  const findings = [];

  const phishingWords = ['срочно', 'заблокирован', 'подтвердите', 'пароль', 'код', 'выиграли', 'бесплатно', 'перейдите', 'введите', 'карты', 'cvv', 'немедленно'];
  const found = phishingWords.filter(w => msgLower.includes(w));

  if (found.length > 0) {
    const w = Math.min(40, found.length * 8);
    score += w;
    findings.push({ type: found.length > 3 ? 'danger' : 'warning', category: 'Ключевые слова', message: `Фишинговые слова: ${found.slice(0, 5).join(', ')}`, weight: w });
  }

  if (msgLower.includes('срочно') || msgLower.includes('немедленно') || msgLower.includes('часов')) {
    score += 20;
    findings.push({ type: 'danger', category: 'Давление и срочность', message: 'Создаётся искусственная срочность — типичная тактика мошенников', weight: 20 });
  }

  if (msgLower.includes('пароль') || msgLower.includes('карт') || msgLower.includes('cvv') || msgLower.includes('код подтверждения')) {
    score += 35;
    findings.push({ type: 'danger', category: 'Запрос данных', message: 'Запрашиваются конфиденциальные данные (пароли, коды, данные карты)', weight: 35 });
  }

  if (msgLower.includes('выиграли') || msgLower.includes('выигрыш') || msgLower.includes('лотерея')) {
    score += 20;
    findings.push({ type: 'warning', category: 'Слишком выгодное предложение', message: 'Нереалистичное предложение выигрыша — признак мошенничества', weight: 20 });
  }

  // 
  const urls = message.match(/(?:https?:\/\/)?(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)/gi) || [];
  
  if (urls.length > 0) {
    findings.push({ type: 'info', category: 'Ссылки в сообщении', message: `Найдено ${urls.length} ссылок: ${urls.slice(0, 2).join(', ')}`, weight: 0 });
    if (sender && (msgLower.includes('sber') || sender.toLowerCase().includes('сбер'))) {
      const hasWrongDomain = urls.some(u => !u.includes('sberbank.ru') && !u.includes('sber.ru'));
      if (hasWrongDomain) {
        score += 40;
        findings.push({ type: 'danger', category: 'Несоответствие отправителя', message: `Сообщение якобы от «${sender}», но ссылка ведёт на посторонний домен`, weight: 40 });
      }
    }
  }

  score = Math.min(100, score);
  const level = getLevel(score);

  return {
    message_preview: message.slice(0, 200),
    sender,
    urls_found: urls,
    risk_score: score, risk_level: level,
    verdict: getVerdict(score),
    recommendation: getRecommendation(score),
    findings,
    keywords_found: { russian: found, english: [] },
    ai_analysis: {
      status: 'success',
      analysis: generateAIMsgText(message, score, level, sender),
      model: 'GigaChat'
    },
    report_id: generateID()
  };
}

function generateDemoFullResult(url, message, sender) {
  const urlResult = url ? generateDemoURLResult(url) : null;
  const msgResult = message ? generateDemoMessageResult(message, sender) : null;

  const scores = [];
  if (urlResult) scores.push(urlResult.risk_score);
  if (msgResult) scores.push(msgResult.risk_score);
  const combined = Math.max(...scores, 0);
  const level = getLevel(combined);

  return {
    url_analysis: urlResult,
    message_analysis: msgResult,
    combined: {
      risk_score: combined, risk_level: level,
      verdict: getVerdict(combined),
      recommendation: getRecommendation(combined)
    },
    report_id: generateID()
  };
}

function generateDemoWhois(domain, suspicious) {
  const now = new Date();
  const ageDays = suspicious ? Math.floor(Math.random() * 20 + 3) : Math.floor(Math.random() * 2000 + 365);
  const createdDate = new Date(now - ageDays * 86400000);

  return {
    status: 'success',
    domain,
    registrar: suspicious ? 'Namecheap Inc.' : 'RU-CENTER',
    country: suspicious ? 'Панама' : 'Россия',
    creation_date: createdDate.toISOString().slice(0, 10),
    domain_age_days: ageDays,
    domain_age_str: ageDays < 30 ? `${ageDays} дней ⚠️ НОВЫЙ` : ageDays < 365 ? `${ageDays} дней (${Math.floor(ageDays / 30)} мес.)` : `${ageDays} дней (${Math.floor(ageDays / 365)} лет)`,
    expiration_date: new Date(now.getTime() + 365 * 86400000).toISOString().slice(0, 10),
    name_servers: suspicious ? ['ns1.cloudflare.com', 'ns2.cloudflare.com'] : ['ns1.nic.ru', 'ns2.nic.ru'],
    ip_address: suspicious ? `185.${Math.floor(Math.random()*254)}.${Math.floor(Math.random()*254)}.${Math.floor(Math.random()*254)}` : '77.88.55.66',
    is_known_legitimate: !suspicious
  };
}

function generateAIText(url, score, level) {
  if (score >= 70) return `⚠️ ОПАСНО: Данный URL демонстрирует все классические признаки фишинговой страницы. Домен был зарегистрирован совсем недавно и использует подозрительный хостинг, что типично для временных мошеннических ресурсов.\n\nСтруктура URL намеренно имитирует известные российские организации с незначительными изменениями в написании — это стандартная тактика тайпсквоттинга.\n\nНастоятельно рекомендуем: НЕ переходить по данной ссылке, не вводить никаких личных данных. Сообщите о мошенничестве в Банк России (при финансовой угрозе) или Роскомнадзор.`;
  if (score >= 40) return `⚠️ Ссылка вызывает серьёзные подозрения. Обнаружены характерные признаки фишинга, требующие внимания.\n\nПеред переходом рекомендуется самостоятельно проверить домен и убедиться в его подлинности через официальные источники.\n\nЕсли вы ожидаете сообщение от данной организации, лучше зайдите на официальный сайт напрямую через браузер.`;
  return `✅ Ресурс не содержит явных признаков фишинга. Анализ структуры URL, домена и репутации не выявил критических угроз.\n\nТем не менее, всегда проверяйте адресную строку браузера перед вводом любых паролей или платёжных данных. Даже легитимные сайты могут быть скомпрометированы.`;
}

function generateAIMsgText(msg, score, level, sender) {
  if (score >= 60) return `🚨 ФИШИНГ: Это сообщение содержит многочисленные признаки социальной инженерии и мошенничества.\n\nИспользуются классические психологические манипуляции: создание срочности, угроза блокировки аккаунта, запросы конфиденциальных данных. Это стандартная схема «вишинга» (голосового/текстового фишинга).\n\nНИ ОДНА легитимная организация (банк, госорган, сервис) никогда не запрашивает пароли, CVV-коды или коды из СМС через сообщения. Немедленно удалите это сообщение и заблокируйте отправителя.`;
  if (score >= 30) return `⚠️ Сообщение вызывает подозрения. Присутствуют некоторые признаки манипулятивной коммуникации.\n\nРекомендуется перепроверить информацию через официальные каналы связи с организацией-отправителем (официальный сайт, телефон горячей линии).\n\nНе переходите по ссылкам из данного сообщения, пока не убедитесь в его подлинности.`;
  return `✅ Признаков фишинга или социальной инженерии в данном сообщении не обнаружено. Текст не содержит типичных фишинговых манипуляций.\n\nТем не менее, соблюдайте базовые правила цифровой гигиены: не передавайте пароли и коды из СМС никому, даже представителям служб поддержки.`;
}

function getLevel(score) {
  if (score >= 70) return 'КРИТИЧЕСКИЙ';
  if (score >= 50) return 'ВЫСОКИЙ';
  if (score >= 30) return 'СРЕДНИЙ';
  if (score >= 15) return 'НИЗКИЙ';
  return 'БЕЗОПАСНЫЙ';
}

function getVerdict(score) {
  if (score >= 70) return '🚨 ФИШИНГ — Не открывайте эту ссылку!';
  if (score >= 50) return '⛔ ВЕРОЯТНЫЙ ФИШИНГ — Крайне подозрительно';
  if (score >= 30) return '⚠️ ПОДОЗРИТЕЛЬНО — Требует проверки';
  if (score >= 15) return '🔍 НЕБОЛЬШОЙ РИСК — Будьте осторожны';
  return '✅ ВЕРОЯТНО БЕЗОПАСНО — Признаков фишинга не обнаружено';
}

function getRecommendation(score) {
  if (score >= 70) return '🚫 НЕ переходите по ссылке! Не вводите никакие данные. Сообщите о мошенничестве в Роскомнадзор или Банк России (при финансовой угрозе).';
  if (score >= 50) return '⚠️ Настоятельно рекомендуем не переходить по ссылке. Если это важное уведомление — проверьте через официальный сайт организации напрямую.';
  if (score >= 30) return '🔍 Перепроверьте источник. Свяжитесь с организацией через официальные каналы для подтверждения подлинности.';
  return '✅ Ресурс выглядит легитимным. Тем не менее, всегда проверяйте адресную строку и наличие HTTPS.';
}

function generateID() {
  return Math.random().toString(36).slice(2, 10).toUpperCase();
}
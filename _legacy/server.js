// DeepSeek API proxy + 高考祝福墙 API — runs on server, key never exposed to frontend
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3001;
const API_KEY = 'sk-1b1a962fbcb54abfb8526ec9e80d29f5';
const DEEPSEEK_URL = 'https://api.deepseek.com/v1/chat/completions';

// 祝福数据存储文件
const BLESSINGS_FILE = path.join(__dirname, 'blessings.json');

// 简单写锁，防止并发写入导致数据损坏
let writeLock = false;
let writeQueue = [];

function acquireLock() {
  return new Promise(resolve => {
    if (!writeLock) {
      writeLock = true;
      resolve();
    } else {
      writeQueue.push(resolve);
    }
  });
}

function releaseLock() {
  if (writeQueue.length > 0) {
    const next = writeQueue.shift();
    next();
  } else {
    writeLock = false;
  }
}

// 读取祝福数据
function readBlessings() {
  try {
    if (fs.existsSync(BLESSINGS_FILE)) {
      return JSON.parse(fs.readFileSync(BLESSINGS_FILE, 'utf-8'));
    }
  } catch (e) { console.error('读取 blessings.json 失败:', e.message); }
  return [];
}

// 写入祝福数据（异步 + 锁）
async function writeBlessings(data) {
  await acquireLock();
  try {
    fs.writeFileSync(BLESSINGS_FILE, JSON.stringify(data), 'utf-8');
  } catch (e) {
    console.error('写入 blessings.json 失败:', e.message);
  } finally {
    releaseLock();
  }
}

const server = http.createServer((req, res) => {
  // CORS — 允许前端跨域调用
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // ===== 路由：GET /api/blessings — 获取祝福列表 =====
  if (req.method === 'GET' && req.url === '/api/blessings') {
    try {
      const data = readBlessings();
      // 按 id 降序，限制 500 条
      const sorted = data.sort((a, b) => b.id - a.id).slice(0, 500);
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify(sorted));
    } catch (e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  // ===== 路由：POST /api/blessings — 提交新祝福 =====
  if (req.method === 'POST' && req.url === '/api/blessings') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', async () => {
      try {
        const entry = JSON.parse(body);
        // 基础字段校验
        if (!entry.id || !entry.school || !entry.bless) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: '缺少必填字段 (id, school, bless)' }));
          return;
        }
        // 简单 XSS 防护：拒绝包含 script 标签的内容
        const safeCheck = JSON.stringify(entry);
        if (/<script/i.test(safeCheck)) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: '内容包含非法标签' }));
          return;
        }
        // 截断超长字段
        if (entry.bless.length > 200) entry.bless = entry.bless.slice(0, 200);
        if (entry.school.length > 50) entry.school = entry.school.slice(0, 50);
        if (entry.uni && entry.uni.length > 60) entry.uni = entry.uni.slice(0, 60);
        // 限制头像数据大小（压缩后通常 < 30KB base64）
        if (entry.avatar && entry.avatar.dataURL && entry.avatar.dataURL.length > 100000) {
          entry.avatar.dataURL = '';
        }

        const data = readBlessings();
        // 去重：同 id 不重复插入
        if (!data.find(d => d.id === entry.id)) {
          data.push(entry);
          await writeBlessings(data);
        }

        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ ok: true, total: data.length }));
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // ===== 通用 DeepSeek 代理 =====
  async function proxyDeepSeek(messages, temperature, maxTokens) {
    const dsRes = await fetch(DEEPSEEK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + API_KEY
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages,
        temperature: temperature || 0.7,
        max_completion_tokens: maxTokens || 1000
      })
    });
    const json = await dsRes.json();
    if (json.choices && json.choices[0]) {
      return { ok: true, text: json.choices[0].message.content };
    }
    return { ok: false, error: json.error || { message: 'no response from DeepSeek' } };
  }

  // 路由：POST /api/polish — 反馈润色
  if (req.method === 'POST' && req.url === '/api/polish') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', async () => {
      try {
        const { sysPrompt, draft } = JSON.parse(body);
        if (!draft || !draft.trim()) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: 'draft is required' }));
          return;
        }
        const result = await proxyDeepSeek([
          { role: 'system', content: sysPrompt || '你是一个专业的课后反馈润色助手。' },
          { role: 'user', content: '请改写以下反馈草稿：\n\n' + draft }
        ], 0.7, 1000);
        res.writeHead(result.ok ? 200 : 500, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify(result.ok ? { text: result.text } : { error: result.error }));
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: { message: e.message } }));
      }
    });
    return;
  }

  // 路由：POST /api/chat — 家长沟通 AI
  if (req.method === 'POST' && req.url === '/api/chat') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', async () => {
      try {
        const { messages, temperature, max_tokens } = JSON.parse(body);
        if (!messages || !messages.length) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: 'messages is required' }));
          return;
        }
        const result = await proxyDeepSeek(messages, temperature || 0.7, max_tokens || 500);
        res.writeHead(result.ok ? 200 : 500, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify(result.ok ? { text: result.text } : { error: result.error }));
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: { message: e.message } }));
      }
    });
    return;
  }

  // 404
  res.writeHead(404);
  res.end(JSON.stringify({ error: 'not found' }));
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('Server running on http://127.0.0.1:' + PORT);
  console.log('Endpoints: /api/polish  /api/chat  /api/blessings');
});

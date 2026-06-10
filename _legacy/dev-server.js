// 本地开发服务器：静态文件 + DeepSeek API 代理
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const API_KEY = 'sk-1b1a962fbcb54abfb8526ec9e80d29f5';
const DEEPSEEK_URL = 'https://api.deepseek.com/v1/chat/completions';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
};

const server = http.createServer((req, res) => {
  // API 代理
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
        const dsRes = await fetch(DEEPSEEK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_KEY },
          body: JSON.stringify({
            model: 'deepseek-chat',
            messages: [
              { role: 'system', content: sysPrompt || '你是一个专业的课后反馈润色助手。' },
              { role: 'user', content: '请改写以下反馈草稿：\n\n' + draft }
            ],
            temperature: 0.7,
            max_completion_tokens: 1000
          })
        });
        const json = await dsRes.json();
        if (json.choices && json.choices[0]) {
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ text: json.choices[0].message.content }));
        } else {
          res.writeHead(500);
          res.end(JSON.stringify({ error: json.error || { message: 'no response' } }));
        }
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: { message: e.message } }));
      }
    });
    return;
  }

  // /api/parent-chat
  if (req.method === 'POST' && req.url === '/api/parent-chat') {
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
        const dsRes = await fetch(DEEPSEEK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_KEY },
          body: JSON.stringify({
            model: 'deepseek-chat',
            messages,
            temperature: temperature || 0.7,
            max_completion_tokens: max_tokens || 500
          })
        });
        const json = await dsRes.json();
        if (json.choices && json.choices[0]) {
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ text: json.choices[0].message.content }));
        } else {
          res.writeHead(500);
          res.end(JSON.stringify({ error: json.error || { message: 'no response' } }));
        }
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: { message: e.message } }));
      }
    });
    return;
  }

  // 标签 API（本地 tags.json）
  if (req.method === 'GET') {
    const reqUrl = new URL(req.url, 'http://localhost');
    if (reqUrl.pathname === '/api/opts') {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'tags.json'), 'utf-8'));
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
        res.end(JSON.stringify({ focusOpts: data.focusOpts, understandOpts: data.understandOpts, participateOpts: data.participateOpts }));
      } catch(e) { res.writeHead(500); res.end(JSON.stringify({error:e.message})); }
      return;
    }
    if (reqUrl.pathname === '/api/tags/all') {
      try {
        const data = fs.readFileSync(path.join(__dirname, 'tags.json'), 'utf-8');
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
        res.end(data);
      } catch(e) { res.writeHead(500); res.end(JSON.stringify({error:e.message})); }
      return;
    }
    if (reqUrl.pathname === '/api/tags') {
      try {
        const subject = reqUrl.searchParams.get('subject') || '';
        const grade = reqUrl.searchParams.get('grade') || '';
        const allData = JSON.parse(fs.readFileSync(path.join(__dirname, 'tags.json'), 'utf-8'));
        const sjData = (allData.subjects || {})[subject];
        if (!sjData) { res.writeHead(404); res.end(JSON.stringify({error:'unknown subject'})); return; }
        let g;
        if (sjData.primary || sjData.junior || sjData.senior || sjData.kindergarten) {
          g = sjData[grade] || sjData.primary || sjData.junior;
        }
        const result = {
          subject, grade,
          strengths: g ? (g.strengths || []) : (sjData.strengths || []),
          weaks: g ? (g.weaks || []) : (sjData.weaks || []),
          homework: sjData.homework || []
        };
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
        res.end(JSON.stringify(result));
      } catch(e) { res.writeHead(500); res.end(JSON.stringify({error:e.message})); }
      return;
    }
  }

  // 静态文件
  let filePath = req.url === '/' ? '/index.html' : req.url.split('?')[0];
  filePath = path.join(__dirname, filePath);
  const ext = path.extname(filePath);
  const contentType = MIME[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not Found');
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('Dev server: http://localhost:' + PORT + '  (API proxy enabled)');
});

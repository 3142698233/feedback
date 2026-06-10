const fs = require('fs');
const path = require('path');
const minify = require('html-minifier').minify;

const src = path.join(__dirname, 'index.src.html');
const out = path.join(__dirname, 'index.html');

const html = fs.readFileSync(src, 'utf8');

const result = minify(html, {
  collapseWhitespace: true,
  removeComments: true,
  minifyCSS: true,
});

fs.writeFileSync(out, result, 'utf8');

const srcSize = (Buffer.byteLength(html, 'utf8') / 1024).toFixed(0);
const outSize = (Buffer.byteLength(result, 'utf8') / 1024).toFixed(0);
const pct = ((1 - outSize / srcSize) * 100).toFixed(0);
console.log(`Build OK: ${srcSize}KB → ${outSize}KB (${pct}% smaller)`);

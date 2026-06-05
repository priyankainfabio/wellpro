const fs = require("fs");
const path = require("path");

const files = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const target = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(target);
    } else if (entry.name.endsWith(".html")) {
      files.push(target);
    }
  }
}

walk("docs");

for (const file of files) {
  let html = fs.readFileSync(file, "utf8");
  html = html.replace(/<noscript><iframe[^>]*googletagmanager[\s\S]*?<\/iframe><\/noscript>/gi, "");
  html = html.replace(/https?:\/\/diabetes\.wellpro\.one\/?(?:index)?/gi, "/diabetes-reversal/index/");
  html = html.replace(/https?:\/\/pcod\.wellpro\.one\/?(?:index)?/gi, "/pcod/index/");
  html = html.replace(/\s+target="_blank"/g, "");
  fs.writeFileSync(file, html);
}

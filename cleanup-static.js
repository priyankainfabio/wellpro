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
  html = html.replace(/\/diabetes-reversal\/index\/?/gi, "/diabetes-reversal/");
  html = html.replace(/\/doctor-assist-registration\/index\/?/gi, "/doctor-assist-registration/");
  html = html.replace(/\/cholesterol\/index\/?/gi, "/cholesterol/");
  html = html.replace(/\/pcod\/index\/?/gi, "/pcod/");
  html = html.replace(/\/soleus\/index\/?/gi, "/soleus/");
  html = html.replace(/\s+target="_blank"/g, "");
  fs.writeFileSync(file, html);
}

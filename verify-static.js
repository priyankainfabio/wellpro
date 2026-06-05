const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "docs");
const pages = [
  "/",
  "/about-us/",
  "/contact-us/",
  "/wellness-protocol-basis/",
  "/diabetes-assist-program/"
];
const refs = new Set(pages);
const externalLoadRefs = [];

function addRef(value, basePath) {
  if (
    !value ||
    value.startsWith("#") ||
    value.startsWith("javascript:") ||
    value.startsWith("mailto:") ||
    value.startsWith("tel:") ||
    value.startsWith("data:")
  ) {
    return;
  }

  if (/^https?:\/\//i.test(value)) {
    externalLoadRefs.push(value);
    return;
  }

  try {
    refs.add(new URL(value, `http://localhost:8080${basePath}`).pathname);
  } catch {
  }
}

function readPage(pagePath) {
  return fs.readFileSync(
    pagePath === "/" ? path.join(root, "index.html") : path.join(root, pagePath, "index.html"),
    "utf8"
  );
}

for (const page of pages) {
  const html = readPage(page);
  for (const match of html.matchAll(/\ssrc=["']([^"']+)["']/g)) {
    addRef(match[1], page);
  }
  for (const match of html.matchAll(/<link\b[^>]*\shref=["']([^"']+)["'][^>]*>/g)) {
    addRef(match[1], page);
  }
  for (const match of html.matchAll(/url\(["']?([^)"']+)["']?\)/g)) {
    addRef(match[1], page);
  }
}

for (const file of fs.readdirSync(path.join(root, "assets", "css"))) {
  if (!file.endsWith(".css")) continue;
  const cssPath = `/assets/css/${file}`;
  const text = fs.readFileSync(path.join(root, "assets", "css", file), "utf8");
  for (const match of text.matchAll(/url\(["']?([^)"']+)["']?\)/g)) {
    addRef(match[1], cssPath);
  }
}

function checkPath(requestPath) {
  let filePath = path.join(root, requestPath);
  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, "index.html");
  }
  if (!fs.existsSync(filePath) && !path.extname(filePath)) {
    filePath = path.join(filePath, "index.html");
  }
  return [requestPath, fs.existsSync(filePath) ? 200 : 404];
}

(async () => {
  const results = [...refs].map(checkPath);
  const bad = results.filter(([, status]) => status >= 400 || String(status).startsWith("ERR"));
  console.log(JSON.stringify({ checked: results.length, bad, externalLoadRefs }, null, 2));
})();

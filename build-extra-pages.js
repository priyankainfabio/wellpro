const fs = require("fs");
const path = require("path");

const root = "docs";
const rawRoot = path.join("mirror_raw", "extra");
const urlMapPath = path.join("mirror_raw", "url_map.json");
const urlMap = fs.existsSync(urlMapPath) ? JSON.parse(fs.readFileSync(urlMapPath, "utf8")) : {};

const pageMap = {
  "advisory-board.html": "advisory-board/index.html",
  "blog.html": "blog/index.html",
  "cholesterol__index.html": "cholesterol/index/index.html",
  "diabetes-assist-program__buy-now.html": "diabetes-assist-program/buy-now/index.html",
  "diabetes-assist-program__diabetes-reversal.html": "diabetes-assist-program/diabetes-reversal/index.html",
  "diabetes-reversal__index.html": "diabetes-reversal/index/index.html",
  "doctor-assist.html": "doctor-assist/index.html",
  "doctor-assist-registration__index.html": "doctor-assist-registration/index/index.html",
  "lifestyle-disorders__cholesterol.html": "lifestyle-disorders/cholesterol/index.html",
  "lifestyle-disorders__depression.html": "lifestyle-disorders/depression/index.html",
  "lifestyle-disorders__diabetes.html": "lifestyle-disorders/diabetes/index.html",
  "lifestyle-disorders__erectile-dysfunction.html": "lifestyle-disorders/erectile-dysfunction/index.html",
  "lifestyle-disorders__immune-system.html": "lifestyle-disorders/immune-system/index.html",
  "lifestyle-disorders__joint-pain.html": "lifestyle-disorders/joint-pain/index.html",
  "lifestyle-disorders__thyroid.html": "lifestyle-disorders/thyroid/index.html",
  "lifestyle-disorders__vegan-omega-oil.html": "lifestyle-disorders/vegan-omega-oil/index.html",
  "pcod__index.html": "pcod/index/index.html",
  "refund-and-exchange-policy.html": "refund-and-exchange-policy/index.html",
  "soleus__index.html": "soleus/index/index.html",
  "wellness-dietitian__registration.html": "wellness-dietitian/registration/index.html",
  "wellpro.html": "wellpro/index.html"
};

const internalRoutes = {
  "/wellpro": "/",
  "/about-us": "/about-us/",
  "/contact-us": "/contact-us/",
  "/diabetes-assist-program": "/diabetes-assist-program/",
  "/diabetes-assist-program/index": "/diabetes-assist-program/",
  "/wellness-protocol-basis": "/wellness-protocol-basis/",
  "/advisory-board": "/advisory-board/",
  "/blog": "/blog/",
  "/cholesterol/index": "/cholesterol/index/",
  "/diabetes-assist-program/buy-now": "/diabetes-assist-program/buy-now/",
  "/diabetes-assist-program/diabetes-reversal": "/diabetes-assist-program/diabetes-reversal/",
  "/diabetes-reversal/index": "/diabetes-reversal/index/",
  "/doctor-assist": "/doctor-assist/",
  "/doctor-assist-registration/index": "/doctor-assist-registration/index/",
  "/lifestyle-disorders/cholesterol": "/lifestyle-disorders/cholesterol/",
  "/lifestyle-disorders/depression": "/lifestyle-disorders/depression/",
  "/lifestyle-disorders/diabetes": "/lifestyle-disorders/diabetes/",
  "/lifestyle-disorders/erectile-dysfunction": "/lifestyle-disorders/erectile-dysfunction/",
  "/lifestyle-disorders/immune-system": "/lifestyle-disorders/immune-system/",
  "/lifestyle-disorders/joint-pain": "/lifestyle-disorders/joint-pain/",
  "/lifestyle-disorders/thyroid": "/lifestyle-disorders/thyroid/",
  "/lifestyle-disorders/vegan-omega-oil": "/lifestyle-disorders/vegan-omega-oil/",
  "/pcod/index": "/pcod/index/",
  "/refund-and-exchange-policy": "/refund-and-exchange-policy/",
  "/soleus/index": "/soleus/index/",
  "/wellness-dietitian/registration": "/wellness-dietitian/registration/"
};

function normalizeUrl(value) {
  if (value.startsWith("//")) return `https:${value}`;
  if (value.startsWith("http://")) return `https://${value.slice("http://".length)}`;
  return value;
}

function getLocalPath(value) {
  if (!value) return null;
  const normalized = normalizeUrl(value);
  const noQuery = normalized.replace(/\?.*$/, "");

  if (urlMap[normalized]) return `/${urlMap[normalized]}`;
  if (urlMap[noQuery]) return `/${urlMap[noQuery]}`;

  try {
    const url = new URL(normalized);
    if (url.hostname === "wellpro.one") {
      return internalRoutes[url.pathname.replace(/\/$/, "")] || url.pathname;
    }
  } catch {
  }

  if (normalized.startsWith("/") && internalRoutes[normalized.replace(/\/$/, "")]) {
    return internalRoutes[normalized.replace(/\/$/, "")];
  }

  if (/content\.app-sources\.com/.test(noQuery)) {
    return "/assets/images/placeholder.png";
  }

  return null;
}

function rewriteHtml(html) {
  html = html.replace(/<link[^>]+rel=["'](?:dns-prefetch|preconnect)["'][^>]*>\s*/gi, "");
  html = html.replace(/<link[^>]+rel=["']preload["'][^>]*as=["']script["'][^>]*>\s*/gi, "");
  html = html.replace(/<script[^>]+src=["'][^"']*(?:googletagmanager|google-analytics|doubleclick|youtube|apps\.elfsight|convert\.gocommercially|play\.fabulousmedia)[^"']*["'][^>]*>\s*<\/script>\s*/gi, "");
  html = html.replace(/<script[^>]*>[\s\S]*?(?:gtag|dataLayer|Google Tag Manager|service-api\.app-sources|convert\.gocommercially|play\.fabulousmedia)[\s\S]*?<\/script>\s*/gi, "");
  html = html.replace(/<iframe[^>]+src=["'][^"']*(?:docs\.google|youtube|vimeo)[^"']*["'][^>]*>[\s\S]*?<\/iframe>/gi, "");
  html = html.replace(/<div[^>]+class=["'][^"']*elfsight-app[^"']*["'][^>]*>[\s\S]*?<\/div>/gi, "");
  html = html.replace(/\sdata-resources=["'][^"']*["']/gi, "");
  html = html.replace(/\sdata-content=["'][^"']*["']/gi, "");
  html = html.replace(/<script[^>]+src=["']\/assets\/js\/(?:hit|platform\.client\.min)\.js["'][^>]*>\s*<\/script>\s*/gi, "");

  html = html.replace(/\b(href|src|content|data-slide)=(["'])([^"']+)(["'])/gi, (match, attr, quote, value) => {
    const local = getLocalPath(value);
    return local ? `${attr}=${quote}${local}${quote}` : match;
  });

  html = html.replace(/url\((["']?)([^)"']+)(["']?)\)/gi, (match, q1, value, q2) => {
    const local = getLocalPath(value);
    return local ? `url(${q1}${local}${q2})` : match;
  });

  html = html.replace(/https?:\/\/wellpro\.one\/([^"'\s<>]*)/gi, (_, route) => {
    const clean = `/${route}`.replace(/\/$/, "");
    return internalRoutes[clean] || `/${route}`;
  });

  if (!html.includes("/assets/css/offline-fixes.css")) {
    html = html.replace("</head>", '<link rel="stylesheet" href="/assets/css/offline-fixes.css">\n</head>');
  }

  return html;
}

for (const [rawFile, outputFile] of Object.entries(pageMap)) {
  const rawPath = path.join(rawRoot, rawFile);
  if (!fs.existsSync(rawPath)) continue;
  const targetPath = path.join(root, outputFile);
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
  fs.writeFileSync(targetPath, rewriteHtml(fs.readFileSync(rawPath, "utf8")));
  console.log(`wrote ${targetPath}`);
}

fs.mkdirSync(path.join(root, "store", "cart"), { recursive: true });
fs.writeFileSync(
  path.join(root, "store", "cart", "index.html"),
  '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=/"><title>Cart unavailable offline</title><p>Cart is unavailable in this offline mirror.</p>'
);

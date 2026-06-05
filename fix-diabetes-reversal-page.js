const fs = require("fs");

let html = fs.readFileSync("mirror_raw/extra/diabetes-reversal__index.html", "utf8");

html = html.replace(/<link[^>]+rel=["'](?:dns-prefetch|preconnect)["'][^>]*>\s*/gi, "");
html = html.replace(/<link[^>]+rel=["']preload["'][^>]*as=["']script["'][^>]*>\s*/gi, "");
html = html.replace(/<script[^>]+src=["'][^"']*(?:googletagmanager|google-analytics|doubleclick|connect\.facebook|botsrv2|convert\.gocommercially|play\.fabulousmedia|youtube|vimeo)[^"']*["'][^>]*>\s*<\/script>\s*/gi, "");
html = html.replace(/<noscript>[\s\S]*?(?:googletagmanager|facebook)[\s\S]*?<\/noscript>\s*/gi, "");
html = html.replace(/<script[^>]*>[\s\S]*?(?:Google Tag Manager|Facebook Pixel Code|fbq\(|gtag\(|dataLayer|qbOptions)[\s\S]*?<\/script>\s*/gi, "");

html = html.replace(/<script[^>]+src=["']https?:\/\/static\.web-repository\.com\/scripts\/platform\.client\.min\.js[^"']*["'][^>]*>\s*<\/script>/gi, '<script type="text/javascript" src="/assets/js/platform.client.min.js"></script>');
html = html.replace(/<script[^>]+src=["']https?:\/\/static\.web-repository\.com\/scripts\/common\/hit\.js[^"']*["'][^>]*>\s*<\/script>/gi, '<script type="text/javascript" src="/assets/js/hit.js"></script>');

html = html.replace(/https?:\/\/static\.web-repository\.com\/styles\/platform\.client\.min\.css\?v=\d+/gi, "/assets/css/platform.client.min.css");
html = html.replace(/https?:\/\/static\.web-repository\.com\/t\/theme25\/css\/trunk\.min\.css\?v=\d+/gi, "/assets/css/trunk.min.css");
html = html.replace(/https?:\/\/static\.web-repository\.com\/t\/theme25\/css\/trunk-1024\.min\.css\?v=\d+/gi, "/assets/css/trunk-1024.min.css");
html = html.replace(/https?:\/\/static\.web-repository\.com\/t\/theme25\/css\/trunk-768\.min\.css\?v=\d+/gi, "/assets/css/trunk-768.min.css");
html = html.replace(/https?:\/\/static\.web-repository\.com\/t\/theme25\/css\/trunk-480\.min\.css\?v=\d+/gi, "/assets/css/trunk-480.min.css");
html = html.replace(/\/\/fonts\.googleapis\.com[^"']+/gi, "/assets/css/google-fonts.css");

html = html.replace(/https?:\/\/diabetes\.wellpro\.one\/?(?:index)?/gi, "/diabetes-reversal/");
html = html.replace(/https?:\/\/wellpro\.one\/doctor-assist\/?/gi, "/doctor-assist/");
html = html.replace(/https?:\/\/wellpro\.one\/doctor-assist-registration\/?(?:index)?/gi, "/doctor-assist-registration/");
html = html.replace(/https?:\/\/wellpro\.one\/soleus\/?(?:index)?/gi, "/soleus/");
html = html.replace(/https?:\/\/wellpro\.one\/?/gi, "/");

html = html.replace(/\b(href|src|content|data-slide)=(["'])(https?:\/\/content\.app-sources\.com[^"']+)(["'])/gi, (_match, attr, quote, _value, endQuote) => {
  return `${attr}=${quote}/assets/images/placeholder.png${endQuote}`;
});
html = html.replace(/url\((["']?)https?:\/\/content\.app-sources\.com[^)"']+(["']?)\)/gi, "url(/assets/images/placeholder.png)");

html = html.replace(/\sdata-resources=["'][^"']*["']/gi, "");
html = html.replace(/\sdata-content=["'][^"']*["']/gi, "");

if (!html.includes("/assets/css/offline-fixes.css")) {
  html = html.replace("</head>", '<link rel="stylesheet" href="/assets/css/offline-fixes.css">\n</head>');
}

fs.mkdirSync("docs/diabetes-reversal", { recursive: true });
fs.writeFileSync("docs/diabetes-reversal/index.html", html);
fs.mkdirSync("docs/diabetes-reversal/index", { recursive: true });
fs.writeFileSync("docs/diabetes-reversal/index/index.html", html);

console.log(`rebuilt diabetes-reversal (${html.length} bytes)`);

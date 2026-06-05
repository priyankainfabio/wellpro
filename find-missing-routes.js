const fs = require("fs");
const path = require("path");

const pages = [
  "docs/index.html",
  "docs/about-us/index.html",
  "docs/contact-us/index.html",
  "docs/wellness-protocol-basis/index.html",
  "docs/diabetes-assist-program/index.html"
];

const links = new Set();

for (const file of pages) {
  const html = fs.readFileSync(file, "utf8");
  for (const match of html.matchAll(/href=["'](\/[^"'#?]+)["']/g)) {
    let link = match[1];
    if (
      link === "/" ||
      link.startsWith("/assets/") ||
      link.startsWith("/fonts/") ||
      link.startsWith("/images/") ||
      path.extname(link)
    ) {
      continue;
    }
    links.add(link.replace(/\/$/, ""));
  }
}

for (const link of [...links].sort()) {
  const target = path.join("docs", link, "index.html");
  if (!fs.existsSync(target)) {
    console.log(link);
  }
}

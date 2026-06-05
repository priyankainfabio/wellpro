const fs = require("fs");
const path = require("path");

const routes = [
  "/advisory-board",
  "/blog",
  "/cholesterol/index",
  "/diabetes-assist-program/buy-now",
  "/diabetes-assist-program/diabetes-reversal",
  "/diabetes-reversal/index",
  "/doctor-assist",
  "/doctor-assist-registration/index",
  "/lifestyle-disorders/cholesterol",
  "/lifestyle-disorders/depression",
  "/lifestyle-disorders/diabetes",
  "/lifestyle-disorders/erectile-dysfunction",
  "/lifestyle-disorders/immune-system",
  "/lifestyle-disorders/joint-pain",
  "/lifestyle-disorders/thyroid",
  "/lifestyle-disorders/vegan-omega-oil",
  "/pcod/index",
  "/refund-and-exchange-policy",
  "/soleus/index",
  "/wellness-dietitian/registration",
  "/wellpro"
];

const headers = {
  "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0 Safari/537.36"
};

fs.mkdirSync("mirror_raw/extra", { recursive: true });

(async () => {
  for (const route of routes) {
    const url = `https://wellpro.one${route}`;
    const name = route.replace(/^\/|\/$/g, "").replace(/[\/]/g, "__") || "home";
    try {
      const response = await fetch(url, { headers, redirect: "follow" });
      const contentType = response.headers.get("content-type") || "";
      if (!response.ok || !contentType.includes("text/html")) {
        console.log(`skip ${route} ${response.status} ${contentType}`);
        continue;
      }
      const html = await response.text();
      fs.writeFileSync(path.join("mirror_raw", "extra", `${name}.html`), html);
      console.log(`saved ${route}`);
    } catch (error) {
      console.log(`failed ${route} ${error.message}`);
    }
  }
})();

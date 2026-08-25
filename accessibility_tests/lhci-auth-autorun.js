const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { launch } = require("chrome-launcher");
const puppeteer = require("puppeteer-core");

const REQUIRED_ENV_VARS = [
  "AYR_AAU_USER_USERNAME",
  "AYR_AAU_USER_PASSWORD",
];

const BASE_URL = process.env.LHCI_BASE_URL || "https://localhost:5000";

function getMissingEnvVars() {
  return REQUIRED_ENV_VARS.filter((name) => !process.env[name]);
}

function runLhciWithSessionCookie(sessionCookieHeader) {
  const extraHeaders = JSON.stringify({
    Cookie: sessionCookieHeader,
  });

  const result = spawnSync(
    "npx",
    [
      "lhci",
      "autorun",
      "--config=lighthouserc.js",
      `--collect.settings.extraHeaders=${extraHeaders}`,
    ],
    {
      stdio: "inherit",
      env: process.env,
    },
  );

  if (result.error) {
    throw result.error;
  }

  validateProtectedRoutesWereScanned();

  process.exit(result.status ?? 1);
}

const PROTECTED_ROUTE_PREFIXES = [
  "/browse",
  "/browse/records",
  "/browse/series/",
  "/browse/consignment/",
  "/record/",
  "/search_results_summary",
  "/search/transferring_body/",
];

function isProtectedRoute(pathname) {
  return PROTECTED_ROUTE_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

function getLhrFilePaths(dir) {
  if (!fs.existsSync(dir)) {
    return [];
  }

  return fs
    .readdirSync(dir)
    .filter((entry) => entry.startsWith("lhr-") && entry.endsWith(".json"))
    .map((entry) => path.join(dir, entry));
}

function parseUrlOrNull(value) {
  try {
    return new URL(value);
  } catch {
    return null;
  }
}

function validateProtectedRoutesWereScanned() {
  const reportDir = path.resolve(process.cwd(), ".lighthouseci");
  const lhrFiles = getLhrFilePaths(reportDir);

  if (lhrFiles.length === 0) {
    throw new Error(
      "No Lighthouse JSON reports were found in .lighthouseci; unable to validate protected-route scans.",
    );
  }

  const protectedRouteResults = lhrFiles
    .map((filePath) => {
      const report = JSON.parse(fs.readFileSync(filePath, "utf8"));
      return {
        requestedUrl: report.requestedUrl,
        finalUrl: report.finalUrl,
      };
    })
    .filter((entry) => {
      const requested = parseUrlOrNull(entry.requestedUrl);
      return requested && isProtectedRoute(requested.pathname);
    });

  if (protectedRouteResults.length === 0) {
    throw new Error(
      "No protected AYR routes were present in Lighthouse reports; accessibility run may have been misconfigured.",
    );
  }

  const redirectFailures = protectedRouteResults.filter((entry) => {
    const requested = parseUrlOrNull(entry.requestedUrl);
    const final = parseUrlOrNull(entry.finalUrl);

    if (!requested || !final) {
      return true;
    }

    const sameOrigin = requested.origin === final.origin;
    const stayedOnProtectedRoute = isProtectedRoute(final.pathname);
    return !sameOrigin || !stayedOnProtectedRoute;
  });

  if (redirectFailures.length > 0) {
    const failureDetails = redirectFailures
      .map(
        ({ requestedUrl, finalUrl }) =>
          `requested=${requestedUrl} final=${finalUrl}`,
      )
      .join("\n");

    throw new Error(
      `Lighthouse scanned redirected pages instead of protected AYR routes.\n${failureDetails}`,
    );
  }
}

function getCookieHeaderForUrl(cookies, url) {
  const parsedUrl = new URL(url);
  const hostname = parsedUrl.hostname;
  const isHttps = parsedUrl.protocol === "https:";
  const pathName = parsedUrl.pathname || "/";

  const matchingCookies = cookies.filter((cookie) => {
    const domain = (cookie.domain || "").replace(/^\./, "");
    const domainMatches =
      domain.length === 0 ||
      hostname === domain ||
      hostname.endsWith(`.${domain}`);

    const cookiePath = cookie.path || "/";
    const pathMatches = pathName.startsWith(cookiePath);
    const secureMatches = !cookie.secure || isHttps;

    return domainMatches && pathMatches && secureMatches;
  });

  if (matchingCookies.length === 0) {
    throw new Error(
      "No cookies found for Lighthouse base URL after login; cannot run authenticated Lighthouse.",
    );
  }

  return matchingCookies.map((cookie) => `${cookie.name}=${cookie.value}`).join("; ");
}

async function loginAndGetSessionCookieHeader() {
  const chrome = await launch({
    chromeFlags: [
      "--headless=new",
      "--no-sandbox",
      "--ignore-certificate-errors",
      "--allow-insecure-localhost",
    ],
  });

  let browser;
  try {
    browser = await puppeteer.connect({
      browserURL: `http://127.0.0.1:${chrome.port}`,
      defaultViewport: {
        width: 1280,
        height: 1080,
      },
    });

    const page = await browser.newPage();

    await page.goto(`${BASE_URL}/sign-in`, {
      waitUntil: "networkidle2",
      timeout: 60000,
    });

    await page.waitForSelector("#username", { timeout: 60000 });
    await page.waitForSelector("#password", { timeout: 60000 });

    await page.type("#username", process.env.AYR_AAU_USER_USERNAME);
    await page.type("#password", process.env.AYR_AAU_USER_PASSWORD);

    await Promise.all([
      page.waitForNavigation({ waitUntil: "networkidle2", timeout: 60000 }),
      page.click('button[type="submit"]'),
    ]);

    await page.waitForFunction(
      (baseUrl) => window.location.href.startsWith(`${baseUrl}/browse`),
      { timeout: 60000 },
      BASE_URL,
    );

    const cookies = await browser.cookies(BASE_URL);
    return getCookieHeaderForUrl(cookies, BASE_URL);
  } finally {
    if (browser) {
      await browser.close();
    }
    await chrome.kill();
  }
}

(async () => {
  const missing = getMissingEnvVars();

  if (missing.length > 0) {
    console.error(
      `Missing required env vars for authenticated Lighthouse run: ${missing.join(
        ", ",
      )}`,
    );
    process.exit(1);
  }

  const sessionCookieHeader = await loginAndGetSessionCookieHeader();
  runLhciWithSessionCookie(sessionCookieHeader);
})().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});

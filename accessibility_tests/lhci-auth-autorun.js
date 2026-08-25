const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const REQUIRED_ENV_VARS = [
  "KEYCLOAK_AUTH_URL",
  "KEYCLOAK_CLIENT_ID",
  "KEYCLOAK_CLIENT_SECRET",
  "AYR_AAU_USER_USERNAME",
  "AYR_AAU_USER_PASSWORD",
];

function getMissingEnvVars() {
  return REQUIRED_ENV_VARS.filter((name) => !process.env[name]);
}

async function fetchAccessToken() {
  const payload = new URLSearchParams({
    client_id: process.env.KEYCLOAK_CLIENT_ID,
    client_secret: process.env.KEYCLOAK_CLIENT_SECRET,
    username: process.env.AYR_AAU_USER_USERNAME,
    password: process.env.AYR_AAU_USER_PASSWORD,
    grant_type: "password",
  });

  const response = await fetch(process.env.KEYCLOAK_AUTH_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: payload,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      `Keycloak auth failed (${response.status}): ${body.slice(0, 500)}`,
    );
  }

  const json = await response.json();

  if (!json.access_token) {
    throw new Error("Keycloak response did not contain access_token");
  }

  return json.access_token;
}

function runLhciWithToken(accessToken) {
  const extraHeaders = JSON.stringify({
    Authorization: `Bearer ${accessToken}`,
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
  return PROTECTED_ROUTE_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix),
  );
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

  const token = await fetchAccessToken();
  runLhciWithToken(token);
})().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});

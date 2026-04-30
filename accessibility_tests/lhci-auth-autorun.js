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

  process.exit(result.status ?? 1);
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

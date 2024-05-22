const base_url = "https://127.0.0.1:5000";

module.exports = {
  defaults: {
    timeout: 2000,
    useIncognitoBrowserContext: false,
    chromeLaunchConfig: {
      ignoreHTTPSErrors: true,
    },
    viewport: {
      width: 1280,
      height: 1080,
    },
    userAgent: "A11Y TESTS",
  },
  urls: [
    // static pages
    `${base_url}/how-to-use-this-service`,
    `${base_url}/terms-of-use`,
    `${base_url}/privacy`,
    `${base_url}/cookies`,
    `${base_url}/accessibility`,
    `${base_url}/signed-out`,
    `${base_url}/`,

    // authentication steps
    `${base_url}/sign-out`,
    {
      url: `${base_url}/sign-in`,
      actions: [
        "wait for element #username to be visible",
        `set field #username to ${process.env.AYR_AAU_USER_USERNAME}`,
        `set field #password to ${process.env.AYR_AAU_USER_PASSWORD}`,
        'click element button[type="submit"]',
        "wait for path to be /browse",
      ],
    },

    // pages that require authentication
    `${base_url}/browse`,
    `${base_url}/browse/series/1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7`,
    `${base_url}/browse/consignment/bf203811-357a-45a8-8b38-770d1580691c`,
    `${base_url}/record/097e1fde-70f5-4eef-9a46-c85ea4350bf7`,
    `${base_url}/search_results_summary?query=test`,
    `${base_url}/search/transferring_body/c3e3fd83-4d52-4638-a085-1f4e4e4dfa50?query=test`,
  ],
};

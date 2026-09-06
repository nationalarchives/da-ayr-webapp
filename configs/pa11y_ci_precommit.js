const base_url = `https://localhost:${process.env.WEBAPP_HOST_PORT || 5000}`;

module.exports = {
  defaults: {
    timeout: 10000,
    useIncognitoBrowserContext: false,
    chromeLaunchConfig: {
      ignoreHTTPSErrors: true,
      args: ["--ignore-certificate-errors", "--allow-insecure-localhost"],
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
    `${base_url}/browse/records?sort=file_name-asc&per_page=10`,
    `${base_url}/browse/records?sort=date_of_record-desc&per_page=20`,
    `${base_url}/browse/transferring_body/4654e9f9-335b-4ab1-acd8-edff54f908d4`,
    `${base_url}/browse/series/1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7`,
    `${base_url}/browse/series/93ed0101-2318-45ab-8730-c681958ded7e?sort=consignment_reference-asc`,
    `${base_url}/browse/series/8bd7ad22-90d1-4c7f-ae00-645dfd1987cc?sort=last_record_transferred-desc`,
    `${base_url}/browse/consignment/b4a8379c-0767-4a9b-8537-181aed23e837`,
    `${base_url}/search?query=test&search_area=everywhere&search_filter=test`,
    `${base_url}/search_results_summary?query=test`,
    `${base_url}/search/transferring_body/c3e3fd83-4d52-4638-a085-1f4e4e4dfa50?query=test`,
    `${base_url}/search/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337?query=a&sort=series-asc&search_filter=test`,
  ],
};

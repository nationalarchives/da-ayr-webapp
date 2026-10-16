const BASE_URL = "https://localhost:5000";

const searchTerms = ["test", "ab"];
const transferringBodyFilters = ["a", "b"];
const seriesFilters = ["ab", "y"];

const seriesSorts = [
  "consignment_reference-asc",
  "last_record_transferred-desc",
];

const fixedDateSets = [
  {
    date_from_day: 1,
    date_from_month: 1,
    date_from_year: 1990,
    date_to_day: 28,
    date_to_month: 12,
    date_to_year: 1993,
  },
];

const staticUrls = [
  `${BASE_URL}/`,
  `${BASE_URL}/signed-out`,
  `${BASE_URL}/accessibility`,
  `${BASE_URL}/how-to-use-this-service`,
  `${BASE_URL}/terms-of-use`,
  `${BASE_URL}/privacy`,
  `${BASE_URL}/cookies`,
];

const browseLandingUrls = [`${BASE_URL}/browse`];

const browseRouteUrls = [`${BASE_URL}/browse?sort=file_name-asc&per_page=10`];

const browseUrls = fixedDateSets.map((dates, idx) => {
  const transferringBodyFilter =
    transferringBodyFilters[idx % transferringBodyFilters.length];
  const seriesFilter = seriesFilters[idx % seriesFilters.length];

  const params = new URLSearchParams({
    sort: "transferring_body-asc",
    transferring_body_filter: transferringBodyFilter,
    series_filter: seriesFilter,
    date_from_day: String(dates.date_from_day),
    date_from_month: String(dates.date_from_month),
    date_from_year: String(dates.date_from_year),
    date_to_day: String(dates.date_to_day),
    date_to_month: String(dates.date_to_month),
    date_to_year: String(dates.date_to_year),
  });

  return `${BASE_URL}/browse?${params.toString()}#browse`;
});

const searchLandingUrls = [
  `${BASE_URL}/search/results?query=test%2Btest&search_area=everywhere`,
  `${BASE_URL}/search/results?query=ab%2Bgo&search_area=record`,
];

const searchResultsByTermUrls = searchTerms.map(
  (query) => `${BASE_URL}/search/results?query=${query}`,
);

const searchFilteredUrls = [
  `${BASE_URL}/search/results?query=a%2Btest&sort=series-asc`,
];

const recordIds = [
  "123e4567-e89b-12d3-a456-426614174000",
  "100251bb-5b93-48a9-953f-ad5bd9abfbdc",
];

const recordViewUrls = recordIds.map(
  (id) => `${BASE_URL}/record/${id}#record-view`,
);

const prSmokeUrls = [
  ...staticUrls,
  ...browseLandingUrls.slice(0, 1),
  ...browseRouteUrls.slice(0, 1),
  ...browseUrls.slice(0, 1),
  ...searchLandingUrls.slice(0, 1),
  ...searchResultsByTermUrls.slice(0, 1),
  ...recordViewUrls.slice(0, 1),
];

const allUrls = [
  ...staticUrls,
  ...browseLandingUrls,
  ...browseRouteUrls,
  ...browseUrls,
  ...searchLandingUrls,
  ...searchResultsByTermUrls,
  ...searchFilteredUrls,
  ...recordViewUrls,
];

const isPrSmokeMode = process.env.LHCI_PR_SMOKE === "true";

module.exports = {
  ci: {
    collect: {
      numberOfRuns: 1,
      url: isPrSmokeMode ? prSmokeUrls : allUrls,
      settings: {
        chromeFlags:
          "--no-sandbox --headless=new --ignore-certificate-errors --allow-insecure-localhost",
      },
    },
    assert: {
      assertions: {
        "categories:performance": [
          "warn",
          {
            minScore: 0.75,
          },
        ],
        "categories:accessibility": [
          "error",
          {
            minScore: 0.98,
          },
        ],
        "categories:best-practices": [
          "warn",
          {
            minScore: 0.78,
          },
        ],
        "categories:seo": [
          "warn",
          {
            minScore: 0.9,
          },
        ],
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};

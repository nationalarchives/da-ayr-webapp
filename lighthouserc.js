const BASE_URL = "https://localhost:5000";

const transferringBodyIds = [
  "4654e9f9-335b-4ab1-acd8-edff54f908d4",
  "8ccc8cd1-c0ee-431d-afad-70cf404ba337",
];

const seriesIds = [
  "93ed0101-2318-45ab-8730-c681958ded7e",
  "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc",
];

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

const browseRecordsRouteUrls = [
  `${BASE_URL}/browse/records?sort=file_name-asc&per_page=10`,
];

const transferringBodyUrls = transferringBodyIds.map(
  (id) => `${BASE_URL}/browse/transferring_body/${id}`,
);

const seriesUrls = seriesSorts.map((sort, idx) => {
  const seriesId = seriesIds[idx % seriesIds.length];
  return `${BASE_URL}/browse/series/${seriesId}?sort=${sort}`;
});

const consignmentIds = [
  "2fd4e03e-5913-4c04-b4f2-5a823fafd430",
  "016031db-1398-4fe4-b743-630aa82ea32a",
];

const consignmentUrls = consignmentIds.map(
  (id) => `${BASE_URL}/browse/consignment/${id}`,
);

const consignmentFilteredUrls = consignmentIds.slice(0, 2).map((id) => {
  const params = new URLSearchParams({
    series_filter: "AYR 1",
    date_from_day: "01",
    date_from_month: "01",
    date_from_year: "2020",
    date_to_day: "01",
    date_to_month: "01",
    date_to_year: "2026",
    page: "1",
    per_page: "10",
  });

  return `${BASE_URL}/browse/consignment/${id}?${params.toString()}`;
});

const browseRecordUrls = fixedDateSets.map((dates, idx) => {
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

  return `${BASE_URL}/browse?${params.toString()}#browse-records`;
});

const browseSeriesUrls = seriesFilters.map((seriesFilter, idx) => {
  const dates = fixedDateSets[idx % fixedDateSets.length];
  const params = new URLSearchParams({
    sort: "series-asc",
    transferring_body_filter: "",
    series_filter: seriesFilter,
    date_from_year: String(dates.date_from_year),
    date_to_year: String(dates.date_to_year),
  });

  return `${BASE_URL}/browse?${params.toString()}#browse-series`;
});

const searchLandingUrls = [
  `${BASE_URL}/search?query=test&search_area=everywhere&search_filter=test`,
  `${BASE_URL}/search?query=ab&search_area=record&search_filter=go`,
];

const searchResultsByTermUrls = searchTerms.map(
  (query) => `${BASE_URL}/search_results_summary?query=${query}`,
);

const searchTransferringBodyUrls = [
  `${BASE_URL}/search/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337?query=a&sort=series-asc&search_filter=test`,
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
  ...browseRecordsRouteUrls.slice(0, 1),
  ...transferringBodyUrls.slice(0, 1),
  ...seriesUrls.slice(0, 1),
  ...consignmentUrls.slice(0, 1),
  ...browseRecordUrls.slice(0, 1),
  ...searchLandingUrls.slice(0, 1),
  ...searchResultsByTermUrls.slice(0, 1),
  ...recordViewUrls.slice(0, 1),
];

const allUrls = [
  ...staticUrls,
  ...browseLandingUrls,
  ...browseRecordsRouteUrls,
  ...transferringBodyUrls,
  ...seriesUrls,
  ...consignmentUrls,
  ...consignmentFilteredUrls,
  ...browseRecordUrls,
  ...browseSeriesUrls,
  ...searchLandingUrls,
  ...searchResultsByTermUrls,
  ...searchTransferringBodyUrls,
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

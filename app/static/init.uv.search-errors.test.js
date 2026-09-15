const {
  resizeObserverState,
  setupDOM,
  setupSearchableSearch,
  mockFetchResolved,
  mockFetchError,
  mockFetchRejected,
  mockFetchPending,
  flushPromises,
  runSubmittedSearch,
} = require("./init.uv.test-helpers.js");

afterEach(() => {
  jest.clearAllMocks();
});

beforeEach(() => {
  setupDOM();
});

const SAME_PAGE_RECT = { x: 0, y: 0, w: 0.1, h: 0.1 };

const testDisablesSubmitDuringFetch = async () => {
  setupSearchableSearch();
  const resolveFetch = mockFetchPending();

  const submitButton = document.getElementById("uv-search-submit");
  document.getElementById("uv-search-input").value = "foo";
  submitButton.click();
  await flushPromises();

  expect(submitButton.disabled).toBe(true);

  resolveFetch({ ok: true, json: () => Promise.resolve({ hits: [] }) });
  await flushPromises();

  expect(submitButton.disabled).toBe(false);
};

const testIgnoresConcurrentSearchTrigger = async () => {
  setupSearchableSearch();
  const resolveFetch = mockFetchPending();

  document.getElementById("uv-search-input").value = "foo";
  const submitButton = document.getElementById("uv-search-submit");
  submitButton.click();
  submitButton.click();
  await flushPromises();

  expect(global.fetch).toHaveBeenCalledTimes(1);

  resolveFetch({ ok: true, json: () => Promise.resolve({ hits: [] }) });
  await flushPromises();
};

const testShowsNoResultsMessage = async () => {
  setupSearchableSearch();
  mockFetchResolved([]);

  await runSubmittedSearch("nomatch");

  expect(document.getElementById("uv-search-results").hidden).toBe(true);
  const noResults = document.getElementById("uv-search-no-results");
  expect(noResults.hidden).toBe(false);
  expect(noResults.textContent).toBe("No results found");
};

const SEARCH_ERROR_STATUS = 500;

const testClearsPreviousErrorOnNewSearch = async () => {
  setupSearchableSearch();
  mockFetchError(SEARCH_ERROR_STATUS);

  await runSubmittedSearch("foo");
  expect(document.getElementById("uv-search-error").hidden).toBe(false);

  mockFetchResolved([{ page: 1, rect: SAME_PAGE_RECT, text: "a" }]);
  await runSubmittedSearch("a");

  expect(document.getElementById("uv-search-error").hidden).toBe(true);
};

describe("search fetch state", () => {
  it(
    "disables the search button while a fetch is in progress and re-enables it after",
    testDisablesSubmitDuringFetch,
  );

  it(
    "ignores a second search trigger while a fetch is already in progress",
    testIgnoresConcurrentSearchTrigger,
  );

  it(
    "shows a no-results message and hides prev/next when the search has no hits",
    testShowsNoResultsMessage,
  );

  it(
    "clears a previous error message when a new search is run",
    testClearsPreviousErrorOnNewSearch,
  );
});

const testShowsErrorOnNonOkStatus = async () => {
  setupSearchableSearch();
  mockFetchError(SEARCH_ERROR_STATUS);

  await runSubmittedSearch("foo");

  expect(document.getElementById("uv-search-results").hidden).toBe(true);
  expect(document.getElementById("uv-search-no-results").hidden).toBe(true);
  const errorEl = document.getElementById("uv-search-error");
  expect(errorEl.hidden).toBe(false);
  expect(errorEl.textContent).toContain(
    "There was a problem searching this record",
  );
};

const testShowsErrorOnNetworkFailure = async () => {
  setupSearchableSearch();
  mockFetchRejected();

  await runSubmittedSearch("foo");

  expect(document.getElementById("uv-search-error").hidden).toBe(false);
};

const RESIZE_BURST_COUNT = 20;
const RESIZE_DEBOUNCE_MS = 100;

const triggerResizeBurst = () => {
  Array.from({ length: RESIZE_BURST_COUNT }).forEach(() => {
    window.dispatchEvent(new Event("resize"));
  });
};

const triggerResizeObserverBurst = () => {
  Array.from({ length: RESIZE_BURST_COUNT }).forEach(() => {
    resizeObserverState.current();
  });
};

const expectRedrawDebounced = (highlightBefore, triggerBurst) => {
  triggerBurst();
  expect(document.querySelector(".uv-search-highlight")).toBe(highlightBefore);
  jest.advanceTimersByTime(RESIZE_DEBOUNCE_MS - 1);
  expect(document.querySelector(".uv-search-highlight")).toBe(highlightBefore);
  jest.advanceTimersByTime(1);
};

const expectRedrawDebouncedSimple = (highlightBefore, triggerBurst) => {
  triggerBurst();
  expect(document.querySelector(".uv-search-highlight")).toBe(highlightBefore);
  jest.advanceTimersByTime(RESIZE_DEBOUNCE_MS);
};

const expectNewHighlight = (highlightBefore) => {
  const highlightAfter = document.querySelector(".uv-search-highlight");
  expect(highlightAfter).not.toBeNull();
  expect(highlightAfter).not.toBe(highlightBefore);
};

const testDebouncesOnWindowResize = async () => {
  jest.useFakeTimers();
  setupSearchableSearch();
  mockFetchResolved([{ page: 1, rect: SAME_PAGE_RECT, text: "a" }]);
  await runSubmittedSearch("a");

  const highlightBefore = document.querySelector(".uv-search-highlight");
  expect(highlightBefore).not.toBeNull();

  expectRedrawDebounced(highlightBefore, triggerResizeBurst);
  expectNewHighlight(highlightBefore);

  jest.useRealTimers();
};

const testDebouncesOnResizeObserver = async () => {
  jest.useFakeTimers();
  setupSearchableSearch();
  mockFetchResolved([{ page: 1, rect: SAME_PAGE_RECT, text: "a" }]);
  await runSubmittedSearch("a");

  const highlightBefore = document.querySelector(".uv-search-highlight");
  expect(highlightBefore).not.toBeNull();
  expect(resizeObserverState.current).toEqual(expect.any(Function));

  expectRedrawDebouncedSimple(highlightBefore, triggerResizeObserverBurst);
  expectNewHighlight(highlightBefore);

  jest.useRealTimers();
};

describe("search errors and debounce", () => {
  it(
    "shows an error message and hides results when the search API returns a non-OK status",
    testShowsErrorOnNonOkStatus,
  );

  it(
    "shows an error message when the search request fails outright (network error)",
    testShowsErrorOnNetworkFailure,
  );

  it(
    "debounces highlight redraws on rapid window resize, redrawing once after the burst settles",
    testDebouncesOnWindowResize,
  );

  it(
    "debounces highlight redraws on rapid canvas ResizeObserver callbacks (e.g. PDF.js re-rendering at a new zoom level)",
    testDebouncesOnResizeObserver,
  );
});

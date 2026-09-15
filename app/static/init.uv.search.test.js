const {
  setupDOM,
  initWithHandlers,
  setupSearchableSearch,
  mockFetchResolved,
  flushPromises,
  runSubmittedSearch,
} = require("./init.uv.test-helpers.js");

afterEach(() => {
  jest.clearAllMocks();
});

beforeEach(() => {
  setupDOM();
});

const testCreatesSearchBar = () => {
  initWithHandlers();
  expect(document.getElementById("uv-search")).not.toBeNull();
  expect(document.getElementById("uv-search-input")).not.toBeNull();
  expect(document.getElementById("uv-search-results").hidden).toBe(true);
  expect(document.getElementById("uv-search-no-results").hidden).toBe(true);
};

const testWrapsSearchInputInForm = () => {
  initWithHandlers();

  const search = document.querySelector("#uv-search > search");
  const form = document.getElementById("uv-search-form");
  const submitButton = document.getElementById("uv-search-submit");

  expect(search).not.toBeNull();
  expect(search.contains(form)).toBe(true);
  expect(form.contains(document.getElementById("uv-search-input"))).toBe(true);
  expect(form.contains(submitButton)).toBe(true);
  expect(submitButton.getAttribute("type")).toBe("submit");
};

const testNoDuplicateSearchListeners = async () => {
  setupSearchableSearch();
  document.dispatchEvent(new Event("DOMContentLoaded"));
  mockFetchResolved([]);

  await runSubmittedSearch("foo");

  expect(global.fetch).toHaveBeenCalledTimes(1);
};

const testRunsSearchOnFormSubmit = async () => {
  setupSearchableSearch();
  mockFetchResolved([]);

  document.getElementById("uv-search-input").value = "foo";
  const form = document.getElementById("uv-search-form");
  const submitEvent = new Event("submit", {
    bubbles: true,
    cancelable: true,
  });
  form.dispatchEvent(submitEvent);
  await flushPromises();

  expect(global.fetch).toHaveBeenCalledWith("test-search-url?q=foo");
  expect(submitEvent.defaultPrevented).toBe(true);
};

describe("search bar setup", () => {
  it(
    "creates a search bar next to the viewer when search_url is present, with prev/next hidden until a search is made",
    testCreatesSearchBar,
  );

  it(
    "wraps the search input in a <search><form> with a submit-type button, for pressing Enter to submit",
    testWrapsSearchInputInForm,
  );

  it(
    "does not attach duplicate search listeners when initSearchBar runs again (e.g. re-init on tab switch)",
    testNoDuplicateSearchListeners,
  );

  it("runs a search when the form is submitted", testRunsSearchOnFormSubmit);
});

const FIRST_HIT_RECT = { x: 0.1, y: 0.2, w: 0.3, h: 0.05 };
const SECOND_HIT_RECT = { x: 0, y: 0, w: 0.1, h: 0.05 };

const expectHighlightPosition = (highlight, expectedStyle) => {
  expect(highlight).not.toBeNull();
  expect({
    left: highlight.style.left,
    top: highlight.style.top,
    width: highlight.style.width,
    height: highlight.style.height,
  }).toEqual(expectedStyle);
};

const testFetchesHitsAndHighlightsFirst = async () => {
  setupSearchableSearch();

  mockFetchResolved([
    { page: 1, rect: FIRST_HIT_RECT, text: "foo" },
    { page: 2, rect: SECOND_HIT_RECT, text: "foo" },
  ]);

  await runSubmittedSearch("foo");

  expect(global.fetch).toHaveBeenCalledWith("test-search-url?q=foo");
  expect(document.getElementById("uv-search-results").hidden).toBe(false);
  expect(document.getElementById("uv-search-count").textContent).toBe("1 of 2");
  expect({
    prevHasHref: document.getElementById("uv-search-prev").hasAttribute("href"),
    nextHasHref: document.getElementById("uv-search-next").hasAttribute("href"),
  }).toEqual({ prevHasHref: false, nextHasHref: true });

  const highlight = document.querySelector(".uv-search-highlight");
  expectHighlightPosition(highlight, {
    left: "100px",
    top: "400px",
    width: "300px",
    height: "100px",
  });
  expect(highlight.classList.contains("uv-search-highlight--active")).toBe(
    true,
  );
};

const SAME_PAGE_RECT = { x: 0, y: 0, w: 0.1, h: 0.1 };
const SAME_PAGE_SECOND_RECT = { x: 0, y: 0.2, w: 0.1, h: 0.1 };

const expectSearchNavState = ({ count, prevHasHref, nextHasHref }) => {
  const prev = document.getElementById("uv-search-prev");
  const next = document.getElementById("uv-search-next");
  expect(document.getElementById("uv-search-count").textContent).toBe(count);
  expect(prev.hasAttribute("href")).toBe(prevHasHref);
  expect(next.hasAttribute("href")).toBe(nextHasHref);
};

const clickSearchNav = (direction) => {
  document.getElementById(`uv-search-${direction}`).click();
};

const testNavigatesForwardBackward = async () => {
  setupSearchableSearch();

  mockFetchResolved([
    { page: 1, rect: SAME_PAGE_RECT, text: "a" },
    { page: 1, rect: SAME_PAGE_SECOND_RECT, text: "a" },
  ]);

  await runSubmittedSearch("a");

  expectSearchNavState({
    count: "1 of 2",
    prevHasHref: false,
    nextHasHref: true,
  });

  clickSearchNav("next");
  expectSearchNavState({
    count: "2 of 2",
    prevHasHref: true,
    nextHasHref: false,
  });

  clickSearchNav("next");
  expectSearchNavState({
    count: "2 of 2",
    prevHasHref: true,
    nextHasHref: false,
  });

  clickSearchNav("prev");
  expectSearchNavState({
    count: "1 of 2",
    prevHasHref: false,
    nextHasHref: true,
  });
};

const OTHER_PAGE_RECT = { x: 0, y: 0, w: 0.1, h: 0.1 };
const TARGET_PAGE_NUMBER = 3;

const testDrivesPageNumberField = async () => {
  const { pageIndexChange } = setupSearchableSearch();

  mockFetchResolved([
    { page: TARGET_PAGE_NUMBER, rect: OTHER_PAGE_RECT, text: "x" },
  ]);

  const goButton = document.querySelector("#uv button.go");
  const goSpy = jest.spyOn(goButton, "click");

  await runSubmittedSearch("x");

  expect(document.querySelector("#uv input.searchText").value).toBe(
    String(TARGET_PAGE_NUMBER),
  );
  expect(goSpy).toHaveBeenCalledTimes(1);
  expect(document.querySelector(".uv-search-highlight")).toBeNull();

  pageIndexChange(TARGET_PAGE_NUMBER);
  expect(document.querySelector(".uv-search-highlight")).not.toBeNull();
};

const testClearsHighlightsOnNewPdfLoad = async () => {
  const { pdfLoaded } = setupSearchableSearch();

  mockFetchResolved([{ page: 1, rect: SAME_PAGE_RECT, text: "a" }]);

  await runSubmittedSearch("a");

  expect(document.querySelector(".uv-search-highlight")).not.toBeNull();

  pdfLoaded();

  expect(document.querySelector(".uv-search-highlight")).toBeNull();
  expect(document.getElementById("uv-search-count").textContent).toBe("");
  expect(document.getElementById("uv-search-results").hidden).toBe(true);
  expect(document.getElementById("uv-search-no-results").hidden).toBe(true);
};

describe("search results and highlighting", () => {
  it(
    "fetches hits, shows the count, and highlights the first hit on the current page",
    testFetchesHitsAndHighlightsFirst,
  );

  it(
    "navigates forward/backward between hits and disables prev/next as plain text at each end",
    testNavigatesForwardBackward,
  );

  it(
    "drives UV's page-number field and waits for pageIndexChange when a hit is on another page",
    testDrivesPageNumberField,
  );

  it(
    "clears highlights and resets the count when a new PDF loads",
    testClearsHighlightsOnNewPdfLoad,
  );
});

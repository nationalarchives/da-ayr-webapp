require("@testing-library/jest-dom");
global.MutationObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  disconnect: jest.fn(),
  takeRecords: jest.fn(() => []),
}));

const resizeObserverState = { current: null };
global.ResizeObserver = jest.fn().mockImplementation((callback) => {
  resizeObserverState.current = callback;
  return {
    observe: jest.fn(),
    disconnect: jest.fn(),
  };
});

/* eslint-disable no-secrets/no-secrets -- markup fragment, not a secret; the
   plugin's entropy check flags the "govuk-visually-hidden">Error:</span>"
   substring as a false positive */
const SEARCH_BAR_HTML = `
  <div id="uv-search">
    <search>
      <form id="uv-search-form">
        <label for="uv-search-input" class="govuk-label govuk-label--s uv-search-label">Search within record</label>
        <div class="uv-search-controls">
          <input type="text" id="uv-search-input" class="govuk-input" />
          <button type="submit" id="uv-search-submit" class="govuk-button" data-module="govuk-button">Search</button>
        </div>
      </form>
    </search>
    <div id="uv-search-results" class="uv-search-results" hidden>
      <a href="#" id="uv-search-prev" class="uv-search-nav">Previous</a>
      <span id="uv-search-count" aria-live="polite"></span>
      <a href="#" id="uv-search-next" class="uv-search-nav">Next</a>
    </div>
    <p id="uv-search-no-results" class="govuk-body" hidden>No results found</p>
    <p id="uv-search-error" class="govuk-error-message" aria-live="polite" hidden>
      <span class="govuk-visually-hidden">Error:</span> There was a problem searching this record. Please try again.
    </p>
  </div>
`;
/* eslint-enable no-secrets/no-secrets */

const setupDOM = (options = {}) => {
  document.body.innerHTML = `
    <div id="viewer">
      <script id="init-uv" manifest_url="test-manifest" search_url="test-search-url"></script>
      ${SEARCH_BAR_HTML}
      <div id="uv"></div>
    </div>
  `;
  window.UV = {
    init: jest.fn(() => ({ on: jest.fn() })),
  };
  window.matchMedia = jest.fn().mockImplementation((query) => {
    if (options.mediaQuery) {
      return { matches: query.includes(options.mediaQuery) };
    }
    return { matches: !query.includes("640px") };
  });
  document.dispatchEvent(new Event("DOMContentLoaded"));
};

const requireUvScripts = () => {
  require("./init.uv.pdf-fit.js");
  require("./init.uv.search-status.js");
  require("./init.uv.search.js");
  require("./init.uv.js");
};

const mockUvWithHandlers = () => {
  const handlers = {};
  window.UV = {
    init: jest.fn(() => ({
      on: jest.fn((event, handler) => {
        handlers[event] = handler;
      }),
    })),
  };
  return handlers;
};

const initWithHandlers = () => {
  const handlers = mockUvWithHandlers();
  requireUvScripts();
  document.dispatchEvent(new Event("DOMContentLoaded"));
  return {
    pdfLoaded: () => handlers["pdfExtension.pdfLoaded"](),
    pageIndexChange: (pageIndex) =>
      handlers["pdfExtension.pageIndexChange"](pageIndex),
  };
};

/* eslint-disable no-secrets/no-secrets -- markup fragment, not a secret */
const setupPdfCanvas = (canvasWidth, { withZoomOut = true } = {}) => {
  document.getElementById("uv").innerHTML = `
    <div class="pdfContainer"><canvas width="${canvasWidth}"></canvas></div>
    <button class="btn zoomIn"></button>
    ${withZoomOut ? '<button class="btn zoomOut"></button>' : ""}
  `;
  const container = document.querySelector("#uv .pdfContainer");
  Object.defineProperty(container, "clientWidth", { value: 800 });
  return {
    container,
    canvas: container.querySelector("canvas"),
    zoomInButton: document.querySelector("#uv button.zoomIn"),
    zoomOutButton: document.querySelector("#uv button.zoomOut"),
  };
};

const setupSearchableUv = () => {
  document.getElementById("uv").innerHTML = `
    <div class="pdfContainer"><canvas width="800"></canvas></div>
    <input class="searchText" />
    <button class="go"></button>
  `;
  const container = document.querySelector("#uv .pdfContainer");
  Object.defineProperty(container, "clientWidth", {
    value: 800,
    configurable: true,
  });
  const canvas = container.querySelector("canvas");
  Object.defineProperty(canvas, "clientWidth", {
    value: 1000,
    configurable: true,
  });
  Object.defineProperty(canvas, "clientHeight", {
    value: 2000,
    configurable: true,
  });
  return { container, canvas };
};
/* eslint-enable no-secrets/no-secrets */

const setupSearchableSearch = () => {
  setupSearchableUv();
  const { pdfLoaded, pageIndexChange } = initWithHandlers();
  pdfLoaded();
  return { pdfLoaded, pageIndexChange };
};

const mockFetchResolved = (hits) => {
  global.fetch = jest.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve({ hits }) }),
  );
};

const mockFetchError = (status) => {
  global.fetch = jest.fn(() =>
    Promise.resolve({ ok: false, status, json: () => Promise.resolve({}) }),
  );
};

const mockFetchRejected = () => {
  global.fetch = jest.fn(() => Promise.reject(new Error("network down")));
};

const mockFetchPending = () => {
  let resolveFetch = null;
  global.fetch = jest.fn(
    () =>
      new Promise((resolve) => {
        resolveFetch = resolve;
      }),
  );
  return (result) => resolveFetch(result);
};

const FLUSH_MICROTASK_COUNT = 6;
const flushPromises = () =>
  Array.from({ length: FLUSH_MICROTASK_COUNT }).reduce(
    (chain) => chain.then(() => null),
    Promise.resolve(),
  );

const runSubmittedSearch = (query) => {
  document.getElementById("uv-search-input").value = query;
  document.getElementById("uv-search-submit").click();
  return flushPromises();
};

module.exports = {
  resizeObserverState,
  setupDOM,
  requireUvScripts,
  mockUvWithHandlers,
  initWithHandlers,
  setupPdfCanvas,
  setupSearchableUv,
  setupSearchableSearch,
  mockFetchResolved,
  mockFetchError,
  mockFetchRejected,
  mockFetchPending,
  flushPromises,
  runSubmittedSearch,
};

const searchScriptElement = document.getElementById("init-uv");
const searchUrl = searchScriptElement.getAttribute("search_url");

const searchState = {
  hits: [],
  currentIndex: -1,
  searched: false,
  fetchInProgress: false,
};

let currentPdfPageIndex = 1;
let pendingPageChangeCallback = null;

const clearHighlights = () => {
  document.querySelectorAll(".uv-search-highlight").forEach((el) => {
    el.remove();
  });
};

const resetSearch = () => {
  searchState.hits = [];
  searchState.currentIndex = -1;
  searchState.searched = false;
  clearHighlights();
  window.UvSearchStatus.hideError();
  window.UvSearchStatus.update(searchState);
};

const debounce = (fn, delayMs) => {
  let timeout = null;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delayMs);
  };
};

const HIGHLIGHTS_REDRAW_DEBOUNCE_MS = 100;

let highlightResizeObserver = null;
let observedCanvas = null;

const observeCanvasResize = (canvas, onResize) => {
  if (observedCanvas === canvas) {
    return;
  }
  if (highlightResizeObserver) {
    highlightResizeObserver.disconnect();
  }
  observedCanvas = canvas;
  highlightResizeObserver = new ResizeObserver(() => onResize());
  highlightResizeObserver.observe(canvas);
};

const createHighlightBox = (hit, index, canvas) => {
  const box = document.createElement("div");
  const activeClass =
    index === searchState.currentIndex ? " uv-search-highlight--active" : "";
  box.className = `uv-search-highlight${activeClass}`;
  box.style.left = `${canvas.offsetLeft + hit.rect.x * canvas.clientWidth}px`;
  box.style.top = `${canvas.offsetTop + hit.rect.y * canvas.clientHeight}px`;
  box.style.width = `${hit.rect.w * canvas.clientWidth}px`;
  box.style.height = `${hit.rect.h * canvas.clientHeight}px`;
  return box;
};

let scheduleHighlightsRedraw = null;

const drawHighlights = () => {
  clearHighlights();

  const container = document.querySelector("#uv .pdfContainer");
  const canvas = container && container.querySelector("canvas");
  if (!container || !canvas) {
    return;
  }

  if (getComputedStyle(container).position === "static") {
    container.style.position = "relative";
  }
  observeCanvasResize(canvas, () => scheduleHighlightsRedraw());

  searchState.hits.forEach((hit, index) => {
    if (hit.page === currentPdfPageIndex) {
      container.appendChild(createHighlightBox(hit, index, canvas));
    }
  });
};

scheduleHighlightsRedraw = debounce(
  drawHighlights,
  HIGHLIGHTS_REDRAW_DEBOUNCE_MS,
);

const navigateToPage = (pageNumber, onDone) => {
  if (currentPdfPageIndex === pageNumber) {
    onDone();
    return;
  }

  const input = document.querySelector("#uv input.searchText");
  const button = document.querySelector("#uv button.go");
  if (!input || !button) {
    return;
  }

  pendingPageChangeCallback = onDone;
  input.value = pageNumber;
  button.click();
};

const goToHit = (index) => {
  const { hits } = searchState;
  if (hits.length === 0) {
    return;
  }

  searchState.currentIndex = Math.max(0, Math.min(index, hits.length - 1));
  window.UvSearchStatus.update(searchState);

  const hit = hits[searchState.currentIndex];
  navigateToPage(hit.page, drawHighlights);
};

const attachNavClickHandler = (link, getNextIndex) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    if (!link.hasAttribute("href")) {
      return;
    }
    goToHit(getNextIndex());
  });
};

const getTrimmedSearchQuery = () => {
  const input = document.getElementById("uv-search-input");
  return input ? input.value.trim() : "";
};

const setSearchSubmitDisabled = (disabled) => {
  const submitButton = document.getElementById("uv-search-submit");
  if (submitButton) {
    submitButton.disabled = disabled;
  }
};

const prepareSearchQuery = () => {
  const query = getTrimmedSearchQuery();
  resetSearch();
  return query;
};

const beginSearchFetch = () => {
  searchState.fetchInProgress = true;
  setSearchSubmitDisabled(true);
};

const endSearchFetch = () => {
  searchState.fetchInProgress = false;
  setSearchSubmitDisabled(false);
};

const fetchSearchHits = async (query) => {
  const response = await fetch(`${searchUrl}?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error(`Search request failed with status ${response.status}`);
  }
  const data = await response.json();
  return (data && data.hits) || [];
};

const applySearchHits = (hits) => {
  searchState.hits = hits;
  searchState.searched = true;
  window.UvSearchStatus.update(searchState);
  if (searchState.hits.length > 0) {
    goToHit(0);
  }
};

const runSearch = async () => {
  if (searchState.fetchInProgress) {
    return;
  }

  const query = prepareSearchQuery();
  if (!query || !searchUrl) {
    return;
  }

  beginSearchFetch();
  try {
    applySearchHits(await fetchSearchHits(query));
  } catch {
    window.UvSearchStatus.showError();
  } finally {
    endSearchFetch();
  }
};

const initSearchBar = () => {
  if (!searchUrl) {
    return;
  }

  const bar = document.getElementById("uv-search");
  if (!bar || bar.dataset.listenersAttached) {
    return;
  }
  bar.dataset.listenersAttached = "true";

  document
    .getElementById("uv-search-form")
    .addEventListener("submit", (event) => {
      event.preventDefault();
      runSearch();
    });

  attachNavClickHandler(
    document.getElementById("uv-search-prev"),
    () => searchState.currentIndex - 1,
  );
  attachNavClickHandler(
    document.getElementById("uv-search-next"),
    () => searchState.currentIndex + 1,
  );

  window.addEventListener("resize", scheduleHighlightsRedraw);
};

const onPdfLoaded = () => {
  currentPdfPageIndex = 1;
  resetSearch();
  window.fitPdfToWidth();
};

const onPageIndexChange = (pageIndex) => {
  currentPdfPageIndex = pageIndex;
  if (pendingPageChangeCallback) {
    const callback = pendingPageChangeCallback;
    pendingPageChangeCallback = null;
    callback();
  } else {
    drawHighlights();
  }
};

window.UvSearch = { onPdfLoaded, onPageIndexChange, initSearchBar };

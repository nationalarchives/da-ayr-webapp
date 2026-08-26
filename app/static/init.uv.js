const script = document.getElementById("init-uv");
const manifest_url = script.getAttribute("manifest_url");
const search_url = script.getAttribute("search_url");

let currentPdfPageIndex = 1;
let pendingPageChangeCallback = null;

const searchState = {
  hits: [],
  currentIndex: -1,
  searched: false,
  fetchInProgress: false,
};

function initUniversalViewer() {
  const data = {
    manifest: manifest_url,
    embedded: true,
  };

  const uv = UV.init("uv", data);
  uv.on("configure", function ({ config, cb }) {
    config.modules.pdfCenterPanel = config.modules.pdfCenterPanel || {};
    config.modules.pdfCenterPanel.options = {
      ...(config.modules.pdfCenterPanel.options || {}),
      usePdfJs: true,
    };
    config.modules.footerPanel.options = {
      ...(config.modules.footerPanel.options || {}),
      downloadEnabled: false,
      embedEnabled: false,
      fullscreenEnabled: true,
      moreInfoEnabled: false,
      shareEnabled: false,
    };
    config.modules.pdfHeaderPanel = config.modules.pdfHeaderPanel || {};
    config.modules.pdfHeaderPanel.options = {
      centerOptionsEnabled: true,
      downloadEnabled: false,
      shareEnabled: false,
    };
    cb({
      options: {
        footerPanelEnabled: true,
        leftPanelEnabled: true,
        rightPanelEnabled: false,
        headerPanelEnabled: true,
        preserveViewport: true,
        zoomToSearchResultEnabled: false,
      },
    });
  });
  uv.on("pdfExtension.pdfLoaded", function () {
    currentPdfPageIndex = 1;
    resetSearch();
    fitPdfToWidth();
  });
  uv.on("pdfExtension.pageIndexChange", function (pageIndex) {
    currentPdfPageIndex = pageIndex;
    if (pendingPageChangeCallback) {
      const cb = pendingPageChangeCallback;
      pendingPageChangeCallback = null;
      cb();
    } else {
      drawHighlights();
    }
  });

  initSearchBar();
}

// Universal Viewer's PDF.js panel always renders at a fixed scale with no
// fit-to-width, and that fixed scale can land either side of the container
// width depending on the document's page size (some load too big, some too
// small). The zoom button's per-click scale change isn't a fixed,
// predictable amount either (e.g. pdf.js caps the rendered canvas
// resolution for some page sizes), so rather than pre-computing a click
// count from an assumed scale/step, re-measure the actual canvas width
// after every click.
//
const UV_PDF_FIT_TARGET_RATIO = 0.8;
const UV_PDF_FIT_TOLERANCE = 0.1;
const UV_PDF_FIT_MAX_ATTEMPTS = 20;
const UV_PDF_FIT_MAX_CLICKS = 20;

function fitPdfToWidth(attempt = 0) {
  const container = document.querySelector("#uv .pdfContainer");
  const canvas = container && container.querySelector("canvas");
  if (!container || !canvas || !canvas.width || !container.clientWidth) {
    // The first render may not have finished when pdfLoaded fires
    if (attempt < UV_PDF_FIT_MAX_ATTEMPTS) {
      setTimeout(function () {
        fitPdfToWidth(attempt + 1);
      }, 250);
    }
    return;
  }

  const targetWidth = container.clientWidth * UV_PDF_FIT_TARGET_RATIO;
  const tolerance = targetWidth * UV_PDF_FIT_TOLERANCE;
  if (canvas.width < targetWidth - tolerance) {
    zoomPdfTowardsTargetWidth("zoomIn", targetWidth, tolerance);
  } else if (canvas.width > targetWidth + tolerance) {
    zoomPdfTowardsTargetWidth("zoomOut", targetWidth, tolerance);
  }
}

function zoomPdfTowardsTargetWidth(
  direction,
  targetWidth,
  tolerance,
  clicks = 0,
) {
  const container = document.querySelector("#uv .pdfContainer");
  const canvas = container && container.querySelector("canvas");
  if (!container || !canvas || !canvas.width || !container.clientWidth) {
    return;
  }

  const withinTarget =
    direction === "zoomIn"
      ? canvas.width >= targetWidth - tolerance
      : canvas.width <= targetWidth + tolerance;
  if (withinTarget || clicks >= UV_PDF_FIT_MAX_CLICKS) {
    return;
  }

  const button = document.querySelector(`#uv button.${direction}`);
  if (!button) {
    return;
  }
  button.click();

  // Let pdf.js finish re-rendering the page at the new scale before
  // measuring again, otherwise we'd read the pre-click canvas size.
  setTimeout(function () {
    zoomPdfTowardsTargetWidth(direction, targetWidth, tolerance, clicks + 1);
  }, 250);
}

function initSearchBar() {
  if (!search_url) {
    return;
  }

  const viewerContainer = document.getElementById("viewer");
  if (!viewerContainer || document.getElementById("uv-search")) {
    return;
  }

  const bar = document.createElement("div");
  bar.id = "uv-search";
  bar.innerHTML = `
    <label for="uv-search-input" class="govuk-label govuk-label--s uv-search-label">Search within record</label>
    <div class="uv-search-controls">
      <input type="text" id="uv-search-input" class="govuk-input" />
      <button type="button" id="uv-search-submit" class="govuk-button" data-module="govuk-button">Search</button>
    </div>
    <div id="uv-search-results" class="uv-search-results" hidden>
      <a href="#" id="uv-search-prev" class="uv-search-nav">Previous</a>
      <span id="uv-search-count" aria-live="polite"></span>
      <a href="#" id="uv-search-next" class="uv-search-nav">Next</a>
    </div>
    <p id="uv-search-no-results" class="govuk-body" hidden>No results found</p>
    <p id="uv-search-error" class="govuk-error-message" aria-live="polite" hidden>
      <span class="govuk-visually-hidden">Error:</span> There was a problem searching this record. Please try again.
    </p>
  `;
  viewerContainer.insertBefore(bar, viewerContainer.firstChild);

  document
    .getElementById("uv-search-submit")
    .addEventListener("click", runSearch);
  document
    .getElementById("uv-search-input")
    .addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        runSearch();
      }
    });
  document
    .getElementById("uv-search-prev")
    .addEventListener("click", function (event) {
      event.preventDefault();
      if (!this.hasAttribute("href")) {
        return;
      }
      goToHit(searchState.currentIndex - 1);
    });
  document
    .getElementById("uv-search-next")
    .addEventListener("click", function (event) {
      event.preventDefault();
      if (!this.hasAttribute("href")) {
        return;
      }
      goToHit(searchState.currentIndex + 1);
    });

  window.addEventListener("resize", drawHighlights);
}

function resetSearch() {
  searchState.hits = [];
  searchState.currentIndex = -1;
  searchState.searched = false;
  clearHighlights();
  hideSearchError();
  updateSearchStatus();
}

function hideSearchError() {
  const errorEl = document.getElementById("uv-search-error");
  if (errorEl) {
    errorEl.hidden = true;
  }
}

function showSearchError() {
  const resultsEl = document.getElementById("uv-search-results");
  const noResultsEl = document.getElementById("uv-search-no-results");
  const errorEl = document.getElementById("uv-search-error");
  if (resultsEl) {
    resultsEl.hidden = true;
  }
  if (noResultsEl) {
    noResultsEl.hidden = true;
  }
  if (errorEl) {
    errorEl.hidden = false;
  }
}

function runSearch() {
  if (searchState.fetchInProgress) {
    return;
  }

  const input = document.getElementById("uv-search-input");
  const query = input ? input.value.trim() : "";

  resetSearch();

  if (!query || !search_url) {
    return;
  }

  const submitButton = document.getElementById("uv-search-submit");
  searchState.fetchInProgress = true;
  if (submitButton) {
    submitButton.disabled = true;
  }

  fetch(`${search_url}?q=${encodeURIComponent(query)}`)
    .then(function (response) {
      if (!response.ok) {
        throw new Error(`Search request failed with status ${response.status}`);
      }
      return response.json();
    })
    .then(function (data) {
      searchState.hits = (data && data.hits) || [];
      searchState.searched = true;
      updateSearchStatus();
      if (searchState.hits.length > 0) {
        goToHit(0);
      }
    })
    .catch(function () {
      showSearchError();
    })
    .finally(function () {
      searchState.fetchInProgress = false;
      if (submitButton) {
        submitButton.disabled = false;
      }
    });
}

function updateSearchStatus() {
  const resultsEl = document.getElementById("uv-search-results");
  const noResultsEl = document.getElementById("uv-search-no-results");
  const countEl = document.getElementById("uv-search-count");
  const prevLink = document.getElementById("uv-search-prev");
  const nextLink = document.getElementById("uv-search-next");

  if (!searchState.searched) {
    if (resultsEl) resultsEl.hidden = true;
    if (noResultsEl) noResultsEl.hidden = true;
    if (countEl) countEl.textContent = "";
    return;
  }

  const hasHits = searchState.hits.length > 0;

  if (!hasHits) {
    if (resultsEl) resultsEl.hidden = true;
    if (noResultsEl) noResultsEl.hidden = false;
    return;
  }

  if (noResultsEl) noResultsEl.hidden = true;
  if (resultsEl) resultsEl.hidden = false;
  if (countEl) {
    countEl.textContent = `${searchState.currentIndex + 1} of ${searchState.hits.length}`;
  }

  setNavLinkState(prevLink, searchState.currentIndex > 0);
  setNavLinkState(
    nextLink,
    searchState.currentIndex < searchState.hits.length - 1,
  );
}

function setNavLinkState(link, enabled) {
  if (!link) {
    return;
  }
  if (enabled) {
    link.setAttribute("href", "#");
    link.classList.remove("uv-search-nav--disabled");
  } else {
    link.removeAttribute("href");
    link.classList.add("uv-search-nav--disabled");
  }
}

function goToHit(index) {
  const hits = searchState.hits;
  if (hits.length === 0) {
    return;
  }

  searchState.currentIndex = Math.max(0, Math.min(index, hits.length - 1));
  updateSearchStatus();

  const hit = hits[searchState.currentIndex];
  navigateToPage(hit.page, drawHighlights);
}

function navigateToPage(pageNumber, onDone) {
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
}

function clearHighlights() {
  document.querySelectorAll(".uv-search-highlight").forEach(function (el) {
    el.remove();
  });
}

function drawHighlights() {
  clearHighlights();

  const container = document.querySelector("#uv .pdfContainer");
  const canvas = container && container.querySelector("canvas");
  if (!container || !canvas) {
    return;
  }

  if (getComputedStyle(container).position === "static") {
    container.style.position = "relative";
  }

  observeCanvasResize(canvas);

  searchState.hits.forEach(function (hit, index) {
    if (hit.page !== currentPdfPageIndex) {
      return;
    }

    const box = document.createElement("div");
    box.className =
      "uv-search-highlight" +
      (index === searchState.currentIndex
        ? " uv-search-highlight--active"
        : "");

    box.style.left = `${canvas.offsetLeft + hit.rect.x * canvas.clientWidth}px`;
    box.style.top = `${canvas.offsetTop + hit.rect.y * canvas.clientHeight}px`;
    box.style.width = `${hit.rect.w * canvas.clientWidth}px`;
    box.style.height = `${hit.rect.h * canvas.clientHeight}px`;
    container.appendChild(box);
  });
}

let highlightResizeObserver = null;
let observedCanvas = null;

function observeCanvasResize(canvas) {
  if (observedCanvas === canvas) {
    return;
  }
  if (highlightResizeObserver) {
    highlightResizeObserver.disconnect();
  }
  observedCanvas = canvas;
  highlightResizeObserver = new ResizeObserver(function () {
    drawHighlights();
  });
  highlightResizeObserver.observe(canvas);
}

document.addEventListener("DOMContentLoaded", function () {
  initUniversalViewer();
});

document.querySelectorAll(".govuk-tabs__tab").forEach((tab) => {
  tab.addEventListener("click", function (event) {
    if (this.getAttribute("href") === "#record-view") {
      setTimeout(initUniversalViewer, 0);
    }
  });
});

// Function to remove the .attribution element
function removeAttribution() {
  const attribution = document.querySelector(".attribution");
  if (attribution) {
    attribution.remove();
  }
}

const observer = new MutationObserver(function (mutationsList, observer) {
  for (const mutation of mutationsList) {
    if (mutation.type === "childList") {
      removeAttribution();
    }
  }
});

const observerConfig = { childList: true, subtree: true };

observer.observe(document.body, observerConfig);

document.addEventListener("DOMContentLoaded", function () {
  removeAttribution();
});

document.addEventListener("DOMContentLoaded", function () {
  let uvElement = document.getElementById("uv");
  if (uvElement) {
    uvElement.style.width = "100%";
    uvElement.style.height = "80vh";

    // Apply media query for small devices
    if (window.matchMedia("(max-width: 810px)").matches) {
      uvElement.style.height = "80vh";
      uvElement.style.width = "85vw";
      uvElement.style.padding = "1rem";
    }

    // Apply media query for small devices
    if (window.matchMedia("(max-width: 640px)").matches) {
      uvElement.style.height = "50vh";
      uvElement.style.width = "90vw";
      uvElement.style.padding = "0.25rem";
    }
  }

  document.querySelectorAll(".btn").forEach((button) => {
    if (button.tagName.toLowerCase() === "div") {
      button.setAttribute("role", "button");
    }
  });
});

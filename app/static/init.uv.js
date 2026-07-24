const script = document.getElementById("init-uv");
const manifest_url = script.getAttribute("manifest_url");

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
    fitPdfToWidth();
  });
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

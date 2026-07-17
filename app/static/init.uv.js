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

// Universal Viewer's PDF.js panel always renders at a fixed 0.7 scale and
// has no fit-to-width, so pages open partly zoomed out. Its scale is only
// reachable through the zoom buttons (+0.5 per click), so once the PDF has
// loaded, click zoom-in until the page width approximately fills the
// container (which scrolls vertically via overflow: auto).
const UV_PDF_INITIAL_SCALE = 0.7;
const UV_PDF_ZOOM_STEP = 0.5;
const UV_PDF_FIT_MAX_ATTEMPTS = 20;

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
  const pageWidthAtFullScale = canvas.width / UV_PDF_INITIAL_SCALE;
  const targetScale = (container.clientWidth * 0.95) / pageWidthAtFullScale;
  const clicks = Math.floor(
    (targetScale - UV_PDF_INITIAL_SCALE) / UV_PDF_ZOOM_STEP,
  );
  const zoomInButton = document.querySelector("#uv button.zoomIn");
  for (let i = 0; zoomInButton && i < clicks; i++) {
    zoomInButton.click();
  }
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

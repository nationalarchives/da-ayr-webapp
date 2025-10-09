const script = document.getElementById("init-uv");
const manifest_url = script.getAttribute("manifest_url");

function initUniversalViewer() {
  const data = {
    manifest: manifest_url,
    embedded: true,
  };

  const uv = UV.init("uv", data);
  uv.on("configure", function ({ config, cb }) {
    config.modules.centerPanel.options = {
      usePdfJs: true,
    };
    config.modules.footerPanel.options = {
      downloadEnabled: false,
      embedEnabled: false,
      fullscreenEnabled: false,
      moreInfoEnabled: false,
      shareEnabled: false,
    };
    cb({
      options: {
        footerPanelEnabled: false,
        leftPanelEnabled: true,
        rightPanelEnabled: false,
        headerPanelEnabled: true,
      },
      pdfHeaderPanel: {
        options: {
          centerOptionsEnabled: false,
        },
      },
    });
  });
}

// Remove .attribution element if present
function removeAttribution() {
  const attribution = document.querySelector(".attribution");
  if (attribution) {
    attribution.remove();
  }
}

// Responsive resizing for #uv element
function resizeUvElement() {
  const uvElement = document.getElementById("uv");
  if (!uvElement) return;

  uvElement.style.width = "100%";
  uvElement.style.height = "80vh";
  uvElement.style.padding = "";

  if (window.matchMedia("(max-width: 810px)").matches) {
    uvElement.style.height = "80vh";
    uvElement.style.width = "85vw";
    uvElement.style.padding = "1rem";
  }
  if (window.matchMedia("(max-width: 640px)").matches) {
    uvElement.style.height = "50vh";
    uvElement.style.width = "90vw";
    uvElement.style.padding = "0.25rem";
  }
}

// Accessibility for .btn elements
function enhanceButtons() {
  document.querySelectorAll(".btn").forEach((button) => {
    if (button.tagName.toLowerCase() === "div") {
      button.setAttribute("role", "button");
      button.setAttribute("tabindex", "0");
    }
  });
}

// MutationObserver to remove attribution if it appears
const observer = new MutationObserver(() => removeAttribution());
const observerConfig = { childList: true, subtree: true };

document.addEventListener("DOMContentLoaded", function () {
  // Init Universal Viewer
  initUniversalViewer();

  // Remove attribution and observe for future additions
  removeAttribution();
  observer.observe(document.body, observerConfig);

  // Responsive UV element
  resizeUvElement();
  window.addEventListener("resize", resizeUvElement);

  // Enhance button accessibility
  enhanceButtons();

  // Tab click handler (debounced)
  let uvInitTimeout = null;
  document.querySelectorAll(".govuk-tabs__tab").forEach((tab) => {
    tab.addEventListener("click", function () {
      if (this.getAttribute("href") === "#record-view") {
        clearTimeout(uvInitTimeout);
        uvInitTimeout = setTimeout(initUniversalViewer, 0);
      }
    });
  });
});

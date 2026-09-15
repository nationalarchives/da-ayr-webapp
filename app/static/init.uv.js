/* global UV */

const initScriptElement = document.getElementById("init-uv");
const manifestUrl = initScriptElement.getAttribute("manifest_url");

const configurePdfCenterPanel = (modules) => {
  modules.pdfCenterPanel ||= {};
  modules.pdfCenterPanel.options = {
    ...(modules.pdfCenterPanel.options || {}),
    usePdfJs: true,
  };
};

const configureFooterPanel = (modules) => {
  modules.footerPanel.options = {
    ...(modules.footerPanel.options || {}),
    downloadEnabled: false,
    embedEnabled: false,
    fullscreenEnabled: true,
    moreInfoEnabled: false,
    shareEnabled: false,
  };
};

const configurePdfHeaderPanel = (modules) => {
  modules.pdfHeaderPanel ||= {};
  modules.pdfHeaderPanel.options = {
    centerOptionsEnabled: true,
    downloadEnabled: false,
    shareEnabled: false,
  };
};

const handleUvConfigure = ({ config, cb }) => {
  configurePdfCenterPanel(config.modules);
  configureFooterPanel(config.modules);
  configurePdfHeaderPanel(config.modules);
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
};

const initUniversalViewer = () => {
  const uv = UV.init("uv", { manifest: manifestUrl, embedded: true });
  uv.on("configure", handleUvConfigure);
  uv.on("pdfExtension.pdfLoaded", () => window.UvSearch.onPdfLoaded());
  uv.on("pdfExtension.pageIndexChange", (pageIndex) =>
    window.UvSearch.onPageIndexChange(pageIndex),
  );
  window.UvSearch.initSearchBar();
};

document.addEventListener("DOMContentLoaded", () => {
  initUniversalViewer();
});

document.querySelectorAll(".govuk-tabs__tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    if (tab.getAttribute("href") === "#record-view") {
      setTimeout(initUniversalViewer, 0);
    }
  });
});

const removeAttribution = () => {
  const attribution = document.querySelector(".attribution");
  if (attribution) {
    attribution.remove();
  }
};

const handleAttributionMutations = (mutationsList) => {
  mutationsList.forEach((mutation) => {
    if (mutation.type === "childList") {
      removeAttribution();
    }
  });
};

const attributionObserver = new MutationObserver(handleAttributionMutations);
attributionObserver.observe(document.body, {
  childList: true,
  subtree: true,
});

document.addEventListener("DOMContentLoaded", () => {
  removeAttribution();
});

const UV_TABLET_BREAKPOINT_QUERY = "(max-width: 810px)";
const UV_MOBILE_BREAKPOINT_QUERY = "(max-width: 640px)";

const applyResponsiveUvSize = (uvElement) => {
  uvElement.style.width = "100%";
  uvElement.style.height = "80vh";

  if (window.matchMedia(UV_TABLET_BREAKPOINT_QUERY).matches) {
    uvElement.style.height = "80vh";
    uvElement.style.width = "85vw";
    uvElement.style.padding = "1rem";
  }
  if (window.matchMedia(UV_MOBILE_BREAKPOINT_QUERY).matches) {
    uvElement.style.height = "50vh";
    uvElement.style.width = "90vw";
    uvElement.style.padding = "0.25rem";
  }
};

const fixDivButtonRoles = () => {
  document.querySelectorAll(".btn").forEach((button) => {
    if (button.tagName.toLowerCase() === "div") {
      button.setAttribute("role", "button");
    }
  });
};

document.addEventListener("DOMContentLoaded", () => {
  const uvElement = document.getElementById("uv");
  if (uvElement) {
    applyResponsiveUvSize(uvElement);
  }
  fixDivButtonRoles();
});

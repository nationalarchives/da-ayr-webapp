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

document.addEventListener("DOMContentLoaded", function () {
  initUniversalViewer();
});

// Automatically zooms into the first page thumbnail after a sec delay
const defaultZoom = function () {
  setTimeout(function () {
    let firstPage = document.getElementById("thumb-0");
    if (firstPage) {
      let thumbDiv = firstPage.querySelector("div.thumb");
      thumbDiv.click();
    }
  }, 1000);
};

document.querySelectorAll(".govuk-tabs__tab").forEach((tab) => {
  tab.addEventListener("click", function (event) {
    defaultZoom();
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
  defaultZoom();
});

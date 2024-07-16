const script = document.getElementById("init-uv");
const manifest_url = script.getAttribute("manifest_url");

function initUniversalViewer() {
  const data = {
    // manifest: "{{ url_for('static', filename='universalviewer/manifests/pdf.json') }}",
    manifest: manifest_url,
    embedded: true,
  };

  const uv = UV.init("uv", data);
  uv.on("configure", function ({ config, cb }) {
    config.modules.centerPanel.options.usePdfJs = true;
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

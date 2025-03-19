const script = document.getElementById("init-uv");

if (!script) {
  console.error("Error: Could not find script element with ID 'init-uv'");
}

const manifest_url = script ? script.getAttribute("manifest_url") : null;

console.log("Manifest URL:", manifest_url, typeof manifest_url);

function initUniversalViewer() {
  console.log("Initializing Universal Viewer...");

  if (!manifest_url) {
    console.error("Error: manifest_url is missing or undefined");
    return;
  }

  const data = {
    manifest: manifest_url,
    embedded: true,
  };

  try {
    console.log("Creating Universal Viewer with data:", data);

    if (typeof UV === "undefined") {
      console.error("Error: Universal Viewer (UV) is not loaded");
      return;
    }

    const uv = UV.init("uv", data);

    uv.on("error", function (err) {
      console.error("Universal Viewer error:", err);
    });

    uv.on("configure", function ({ config, cb }) {
      console.log("Universal Viewer configured");

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
  } catch (err) {
    console.error("Universal Viewer Init Error:", err);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  try {
    initUniversalViewer();
  } catch (err) {
    console.error("Error in DOMContentLoaded event:", err);
  }
});

document.querySelectorAll(".govuk-tabs__tab").forEach((tab) => {
  tab.addEventListener("click", function (event) {
    if (this.getAttribute("href") === "#record-view") {
      console.log("Tab clicked, initializing Universal Viewer...");
      setTimeout(initUniversalViewer, 0);
    }
  });
});

// Function to remove the .attribution element
function removeAttribution() {
  const attribution = document.querySelector(".attribution");
  if (attribution) {
    console.log("Removing .attribution element");
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

  if (!uvElement) {
    console.error("Error: Could not find element with ID 'uv'");
    return;
  }

  console.log("Setting up Universal Viewer container styles");

  uvElement.style.width = "100%";
  uvElement.style.height = "60vh";

  if (window.matchMedia("(max-width: 810px)").matches) {
    uvElement.style.height = "60vh";
    uvElement.style.width = "85vw";
    uvElement.style.padding = "1rem";
  }

  if (window.matchMedia("(max-width: 640px)").matches) {
    uvElement.style.height = "50vh";
    uvElement.style.width = "90vw";
    uvElement.style.padding = "0.25rem";
  }
});

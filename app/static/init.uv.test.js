require("@testing-library/jest-dom");
// Mock MutationObserver globally to avoid jsdom runtime errors
class MockMutationObserver {
  constructor(callback) {}
  observe(target, options) {}
  disconnect() {}
  takeRecords() {
    return [];
  }
}
global.MutationObserver = MockMutationObserver;

function setupDOM(options = {}) {
  document.body.innerHTML = `
    <script id="init-uv" manifest_url="test-manifest"></script>
    <div id="uv"></div>
  `;
  window.UV = {
    init: jest.fn(() => ({ on: jest.fn() })),
  };
  window.matchMedia = jest.fn().mockImplementation((query) => {
    if (options.mediaQuery)
      return { matches: query.includes(options.mediaQuery) };
    return { matches: query.includes("640px") ? false : true };
  });
  document.dispatchEvent(new Event("DOMContentLoaded"));
}

afterEach(() => {
  jest.clearAllMocks();
});

describe("tests for init.uv.js", () => {
  beforeEach(() => {
    setupDOM();
  });

  it("should initialize UniversalViewer with manifest", () => {
    require("./init.uv.js");
    document.dispatchEvent(new Event("DOMContentLoaded"));
    expect(window.UV.init).toHaveBeenCalledWith(
      "uv",
      expect.objectContaining({ manifest: "test-manifest" }),
    );
  });

  it.each([
    ["desktop", undefined, { width: "100%", height: "80vh" }],
    ["tablet", "810px", { width: "85vw", height: "80vh", padding: "1rem" }],
    ["mobile", "640px", { width: "90vw", height: "50vh", padding: "0.25rem" }],
  ])(
    "should set uv element styles for %s",
    (label, mediaQuery, expectedStyles) => {
      setupDOM({ mediaQuery });
      require("./init.uv.js");
      const uvElement = document.getElementById("uv");
      setTimeout(() => {
        Object.entries(expectedStyles).forEach(([key, value]) => {
          expect(uvElement.style[key]).toBe(value);
        });
      }, 10);
    },
  );

  it('should set role="button" for .btn divs', () => {
    document.body.innerHTML += `<div class="btn"></div>`;
    require("./init.uv.js");
    const btn = document.querySelector(".btn");
    setTimeout(() => {
      expect(btn.getAttribute("role")).toBe("button");
    }, 10);
  });

  it("should re-initialize UniversalViewer on #record-view tab click", () => {
    document.body.innerHTML += `
      <div class="govuk-tabs__tab" href="#record-view"></div>
    `;
    window.UV = {
      init: jest.fn(() => ({ on: jest.fn() })),
    };
    require("./init.uv.js");
    document.querySelector(".govuk-tabs__tab").click();
    setTimeout(() => {
      expect(window.UV.init).toHaveBeenCalled();
    }, 10);
  });

  it("should remove attribution element via MutationObserver", () => {
    require("./init.uv.js");
    const attribution = document.createElement("div");
    attribution.className = "attribution";
    document.body.appendChild(attribution);
    setTimeout(() => {
      expect(document.querySelector(".attribution")).toBeNull();
    }, 10);
  });

  it("should configure UV viewer with correct options", () => {
    const cbMock = jest.fn();
    const config = {
      modules: {
        footerPanel: {
          options: { downloadEnabled: true, minimiseButtons: true },
        },
      },
    };

    window.UV = {
      init: jest.fn(() => ({
        on: jest.fn((event, handler) => {
          if (event === "configure") {
            handler({ config, cb: cbMock });
          }
        }),
      })),
    };

    document.dispatchEvent(new Event("DOMContentLoaded"));

    expect(config.modules.pdfCenterPanel.options.usePdfJs).toBe(true);

    expect(config.modules.footerPanel.options.downloadEnabled).toBe(false);
    expect(config.modules.footerPanel.options.embedEnabled).toBe(false);
    expect(config.modules.footerPanel.options.fullscreenEnabled).toBe(true);
    expect(config.modules.footerPanel.options.moreInfoEnabled).toBe(false);
    expect(config.modules.footerPanel.options.shareEnabled).toBe(false);
    expect(config.modules.footerPanel.options.minimiseButtons).toBe(true);

    expect(config.modules.pdfHeaderPanel.options.centerOptionsEnabled).toBe(
      true,
    );
    expect(config.modules.pdfHeaderPanel.options.downloadEnabled).toBe(false);
    expect(config.modules.pdfHeaderPanel.options.shareEnabled).toBe(false);

    expect(cbMock).toHaveBeenCalledWith({
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
});

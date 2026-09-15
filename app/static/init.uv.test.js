const {
  setupDOM,
  requireUvScripts,
  mockUvWithHandlers,
  setupPdfCanvas,
} = require("./init.uv.test-helpers.js");

afterEach(() => {
  jest.clearAllMocks();
});

beforeEach(() => {
  setupDOM();
});

const testInitializesUvWithManifest = () => {
  requireUvScripts();
  document.dispatchEvent(new Event("DOMContentLoaded"));
  expect(window.UV.init).toHaveBeenCalledWith(
    "uv",
    expect.objectContaining({ manifest: "test-manifest" }),
  );
};

const UV_STYLE_TIMEOUT_MS = 10;

const testSetsUvElementStyles = (label, mediaQuery, expectedStyles) => {
  setupDOM({ mediaQuery });
  requireUvScripts();
  const uvElement = document.getElementById("uv");
  setTimeout(() => {
    Object.entries(expectedStyles).forEach(([key, value]) => {
      expect(uvElement.style[key]).toBe(value);
    });
  }, UV_STYLE_TIMEOUT_MS);
};

const testSetsRoleButtonForBtnDivs = () => {
  document.body.innerHTML += `<div class="btn"></div>`;
  requireUvScripts();
  const btn = document.querySelector(".btn");
  setTimeout(() => {
    expect(btn.getAttribute("role")).toBe("button");
  }, UV_STYLE_TIMEOUT_MS);
};

const testReinitializesOnTabClick = () => {
  document.body.innerHTML += `
    <div class="govuk-tabs__tab" href="#record-view"></div>
  `;
  window.UV = {
    init: jest.fn(() => ({ on: jest.fn() })),
  };
  requireUvScripts();
  document.querySelector(".govuk-tabs__tab").click();
  setTimeout(() => {
    expect(window.UV.init).toHaveBeenCalled();
  }, UV_STYLE_TIMEOUT_MS);
};

const testRemovesAttributionElement = () => {
  requireUvScripts();
  const attribution = document.createElement("div");
  attribution.className = "attribution";
  document.body.appendChild(attribution);
  setTimeout(() => {
    expect(document.querySelector(".attribution")).toBeNull();
  }, UV_STYLE_TIMEOUT_MS);
};

const setupZoomFitTest = (canvasWidth, options) => {
  jest.useFakeTimers();
  const handlers = mockUvWithHandlers();
  const canvasRefs = setupPdfCanvas(canvasWidth, options);
  requireUvScripts();
  document.dispatchEvent(new Event("DOMContentLoaded"));
  return { handlers, ...canvasRefs };
};

const ZOOM_FIT_CANVAS_SMALL_WIDTH = 280;
const ZOOM_FIT_CANVAS_STEP = 200;

const testZoomsInTowardsTargetWidth = () => {
  const { handlers, canvas, zoomInButton, zoomOutButton } = setupZoomFitTest(
    ZOOM_FIT_CANVAS_SMALL_WIDTH,
  );
  const zoomInSpy = jest.spyOn(zoomInButton, "click").mockImplementation(() => {
    canvas.width += ZOOM_FIT_CANVAS_STEP;
  });
  const zoomOutSpy = jest.spyOn(zoomOutButton, "click");

  handlers["pdfExtension.pdfLoaded"]();
  jest.runAllTimers();

  expect(zoomInSpy).toHaveBeenCalledTimes(2);
  expect(zoomOutSpy).not.toHaveBeenCalled();
  expect(canvas.width).toBe(680);

  jest.useRealTimers();
};

const ZOOM_FIT_CANVAS_LARGE_WIDTH = 1000;

const testZoomsOutTowardsTargetWidth = () => {
  const { handlers, canvas, zoomInButton, zoomOutButton } = setupZoomFitTest(
    ZOOM_FIT_CANVAS_LARGE_WIDTH,
  );
  const zoomInSpy = jest.spyOn(zoomInButton, "click");
  const zoomOutSpy = jest
    .spyOn(zoomOutButton, "click")
    .mockImplementation(() => {
      canvas.width -= ZOOM_FIT_CANVAS_STEP;
    });

  handlers["pdfExtension.pdfLoaded"]();
  jest.runAllTimers();

  expect(zoomOutSpy).toHaveBeenCalledTimes(2);
  expect(zoomInSpy).not.toHaveBeenCalled();
  expect(canvas.width).toBe(600);

  jest.useRealTimers();
};

const ZOOM_FIT_CANVAS_TINY_WIDTH = 10;
const MAX_ZOOM_CLICKS = 20;

const testStopsZoomingAfterMaxAttempts = () => {
  const { handlers, zoomInButton } = setupZoomFitTest(
    ZOOM_FIT_CANVAS_TINY_WIDTH,
    { withZoomOut: false },
  );
  const clickSpy = jest.spyOn(zoomInButton, "click");

  handlers["pdfExtension.pdfLoaded"]();
  jest.runAllTimers();

  expect(clickSpy).toHaveBeenCalledTimes(MAX_ZOOM_CLICKS);

  jest.useRealTimers();
};

const testConfiguresUvViewer = () => {
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
  expect(config.modules.footerPanel.options).toEqual({
    downloadEnabled: false,
    embedEnabled: false,
    fullscreenEnabled: true,
    moreInfoEnabled: false,
    shareEnabled: false,
    minimiseButtons: true,
  });
  expect(config.modules.pdfHeaderPanel.options).toEqual({
    centerOptionsEnabled: true,
    downloadEnabled: false,
    shareEnabled: false,
  });
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
};

describe("tests for init.uv.js", () => {
  it(
    "should initialize UniversalViewer with manifest",
    testInitializesUvWithManifest,
  );

  it.each([
    ["desktop", null, { width: "100%", height: "80vh" }],
    ["tablet", "810px", { width: "85vw", height: "80vh", padding: "1rem" }],
    ["mobile", "640px", { width: "90vw", height: "50vh", padding: "0.25rem" }],
  ])("should set uv element styles for %s", testSetsUvElementStyles);

  it('should set role="button" for .btn divs', testSetsRoleButtonForBtnDivs);

  it(
    "should re-initialize UniversalViewer on #record-view tab click",
    testReinitializesOnTabClick,
  );

  it(
    "should remove attribution element via MutationObserver",
    testRemovesAttributionElement,
  );

  it(
    "should zoom in towards the container width when the PDF loads too small, re-measuring after each click",
    testZoomsInTowardsTargetWidth,
  );

  it(
    "should zoom out towards the container width when the PDF loads too large, never zooming in",
    testZoomsOutTowardsTargetWidth,
  );

  it(
    "should stop clicking zoom-in after the maximum number of attempts",
    testStopsZoomingAfterMaxAttempts,
  );

  it("should configure UV viewer with correct options", testConfiguresUvViewer);
});

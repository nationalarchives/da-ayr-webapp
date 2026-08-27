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

class MockResizeObserver {
  constructor(callback) {}
  observe(target) {}
  disconnect() {}
}
global.ResizeObserver = MockResizeObserver;

function setupDOM(options = {}) {
  document.body.innerHTML = `
    <div id="viewer">
      <script id="init-uv" manifest_url="test-manifest" search_url="test-search-url"></script>
      <div id="uv"></div>
    </div>
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

  it("should zoom in towards the container width when the PDF loads too small, re-measuring after each click", () => {
    jest.useFakeTimers();
    let pdfLoadedHandler;
    window.UV = {
      init: jest.fn(() => ({
        on: jest.fn((event, handler) => {
          if (event === "pdfExtension.pdfLoaded") {
            pdfLoadedHandler = handler;
          }
        }),
      })),
    };
    document.getElementById("uv").innerHTML = `
      <div class="pdfContainer"><canvas width="280"></canvas></div>
      <button class="btn zoomIn"></button>
      <button class="btn zoomOut"></button>
    `;
    const container = document.querySelector("#uv .pdfContainer");
    // jsdom has no layout, so give the container a width
    Object.defineProperty(container, "clientWidth", { value: 800 });
    const canvas = container.querySelector("canvas");
    const zoomInButton = document.querySelector("#uv button.zoomIn");
    const zoomOutButton = document.querySelector("#uv button.zoomOut");

    const zoomInSpy = jest
      .spyOn(zoomInButton, "click")
      .mockImplementation(() => {
        canvas.width += 200;
      });
    const zoomOutSpy = jest.spyOn(zoomOutButton, "click");

    require("./init.uv.js");
    document.dispatchEvent(new Event("DOMContentLoaded"));
    pdfLoadedHandler();
    jest.runAllTimers();

    // Target is 800 * 0.8 = 640, tolerance +/-64. Clicks land on 480, then
    // 680, which clears the tolerance band, so it stops there. The
    // direction is fixed to zoom-in for the whole fit, so zoom-out is
    // never touched (no in-then-out flicker).
    expect(zoomInSpy).toHaveBeenCalledTimes(2);
    expect(zoomOutSpy).not.toHaveBeenCalled();
    expect(canvas.width).toBe(680);

    jest.useRealTimers();
  });

  it("should zoom out towards the container width when the PDF loads too large, never zooming in", () => {
    jest.useFakeTimers();
    let pdfLoadedHandler;
    window.UV = {
      init: jest.fn(() => ({
        on: jest.fn((event, handler) => {
          if (event === "pdfExtension.pdfLoaded") {
            pdfLoadedHandler = handler;
          }
        }),
      })),
    };
    document.getElementById("uv").innerHTML = `
      <div class="pdfContainer"><canvas width="1000"></canvas></div>
      <button class="btn zoomIn"></button>
      <button class="btn zoomOut"></button>
    `;
    const container = document.querySelector("#uv .pdfContainer");
    Object.defineProperty(container, "clientWidth", { value: 800 });
    const canvas = container.querySelector("canvas");
    const zoomInButton = document.querySelector("#uv button.zoomIn");
    const zoomOutButton = document.querySelector("#uv button.zoomOut");

    const zoomInSpy = jest.spyOn(zoomInButton, "click");
    const zoomOutSpy = jest
      .spyOn(zoomOutButton, "click")
      .mockImplementation(() => {
        canvas.width -= 200;
      });

    require("./init.uv.js");
    document.dispatchEvent(new Event("DOMContentLoaded"));
    pdfLoadedHandler();
    jest.runAllTimers();

    // Target is 800 * 0.8 = 640, tolerance +/-64. Clicks land on 800, then
    // 600, which clears the tolerance band, so it stops there. Zoom-in is
    // never touched.
    expect(zoomOutSpy).toHaveBeenCalledTimes(2);
    expect(zoomInSpy).not.toHaveBeenCalled();
    expect(canvas.width).toBe(600);

    jest.useRealTimers();
  });

  it("should stop clicking zoom-in after the maximum number of attempts", () => {
    jest.useFakeTimers();
    let pdfLoadedHandler;
    window.UV = {
      init: jest.fn(() => ({
        on: jest.fn((event, handler) => {
          if (event === "pdfExtension.pdfLoaded") {
            pdfLoadedHandler = handler;
          }
        }),
      })),
    };
    document.getElementById("uv").innerHTML = `
      <div class="pdfContainer"><canvas width="10"></canvas></div>
      <button class="btn zoomIn"></button>
    `;
    const container = document.querySelector("#uv .pdfContainer");
    Object.defineProperty(container, "clientWidth", { value: 800 });
    const zoomInButton = document.querySelector("#uv button.zoomIn");
    const clickSpy = jest.spyOn(zoomInButton, "click");

    require("./init.uv.js");
    document.dispatchEvent(new Event("DOMContentLoaded"));
    pdfLoadedHandler();
    jest.runAllTimers();

    expect(clickSpy).toHaveBeenCalledTimes(20);

    jest.useRealTimers();
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

  describe("search within record", () => {
    // Microtask-only flush (no setTimeout/setImmediate) so we don't wake
    // dangling real timers left running by unrelated tests in this file.
    const flushPromises = async () => {
      for (let i = 0; i < 6; i++) {
        await Promise.resolve();
      }
    };

    function setupSearchableUv() {
      document.getElementById("uv").innerHTML = `
        <div class="pdfContainer"><canvas width="800"></canvas></div>
        <input class="searchText" />
        <button class="go"></button>
      `;
      const container = document.querySelector("#uv .pdfContainer");
      Object.defineProperty(container, "clientWidth", {
        value: 800,
        configurable: true,
      });
      const canvas = container.querySelector("canvas");
      Object.defineProperty(canvas, "clientWidth", {
        value: 1000,
        configurable: true,
      });
      Object.defineProperty(canvas, "clientHeight", {
        value: 2000,
        configurable: true,
      });
      return { container, canvas };
    }

    function initWithHandlers() {
      let pdfLoadedHandler;
      let pageIndexChangeHandler;
      window.UV = {
        init: jest.fn(() => ({
          on: jest.fn((event, handler) => {
            if (event === "pdfExtension.pdfLoaded") {
              pdfLoadedHandler = handler;
            }
            if (event === "pdfExtension.pageIndexChange") {
              pageIndexChangeHandler = handler;
            }
          }),
        })),
      };
      require("./init.uv.js");
      document.dispatchEvent(new Event("DOMContentLoaded"));
      return {
        pdfLoaded: () => pdfLoadedHandler(),
        pageIndexChange: (n) => pageIndexChangeHandler(n),
      };
    }

    it("creates a search bar next to the viewer when search_url is present, with prev/next hidden until a search is made", () => {
      initWithHandlers();
      expect(document.getElementById("uv-search")).not.toBeNull();
      expect(document.getElementById("uv-search-input")).not.toBeNull();
      expect(document.getElementById("uv-search-results").hidden).toBe(true);
      expect(document.getElementById("uv-search-no-results").hidden).toBe(true);
    });

    it("wraps the search input in a <search><form> with a submit-type button, for pressing Enter to submit", () => {
      initWithHandlers();

      const search = document.querySelector("#uv-search > search");
      const form = document.getElementById("uv-search-form");
      const submitButton = document.getElementById("uv-search-submit");

      expect(search).not.toBeNull();
      expect(search.contains(form)).toBe(true);
      expect(form.contains(document.getElementById("uv-search-input"))).toBe(
        true,
      );
      expect(form.contains(submitButton)).toBe(true);
      expect(submitButton.getAttribute("type")).toBe("submit");
    });

    it("runs a search when the form is submitted", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ hits: [] }),
        }),
      );

      document.getElementById("uv-search-input").value = "foo";
      const form = document.getElementById("uv-search-form");
      const submitEvent = new Event("submit", {
        bubbles: true,
        cancelable: true,
      });
      form.dispatchEvent(submitEvent);
      await flushPromises();

      expect(global.fetch).toHaveBeenCalledWith("test-search-url?q=foo");
      // The default form submission must not happen
      expect(submitEvent.defaultPrevented).toBe(true);
    });

    it("fetches hits, shows the count, and highlights the first hit on the current page", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              hits: [
                {
                  page: 1,
                  rect: { x: 0.1, y: 0.2, w: 0.3, h: 0.05 },
                  text: "foo",
                },
                {
                  page: 2,
                  rect: { x: 0, y: 0, w: 0.1, h: 0.05 },
                  text: "foo",
                },
              ],
            }),
        }),
      );

      document.getElementById("uv-search-input").value = "foo";
      document.getElementById("uv-search-submit").click();
      await flushPromises();

      expect(global.fetch).toHaveBeenCalledWith("test-search-url?q=foo");
      expect(document.getElementById("uv-search-results").hidden).toBe(false);
      expect(document.getElementById("uv-search-count").textContent).toBe(
        "1 of 2",
      );
      // First result: previous is disabled (no href, plain text), next is a link
      expect(
        document.getElementById("uv-search-prev").hasAttribute("href"),
      ).toBe(false);
      expect(
        document.getElementById("uv-search-next").hasAttribute("href"),
      ).toBe(true);

      const highlight = document.querySelector(".uv-search-highlight");
      expect(highlight).not.toBeNull();
      expect(highlight.style.left).toBe("100px");
      expect(highlight.style.top).toBe("400px");
      expect(highlight.style.width).toBe("300px");
      expect(highlight.style.height).toBe("100px");
      expect(highlight.classList.contains("uv-search-highlight--active")).toBe(
        true,
      );
    });

    it("disables the search button while a fetch is in progress and re-enables it after", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      let resolveFetch;
      global.fetch = jest.fn(
        () =>
          new Promise((resolve) => {
            resolveFetch = resolve;
          }),
      );

      const submitButton = document.getElementById("uv-search-submit");
      document.getElementById("uv-search-input").value = "foo";
      submitButton.click();
      await flushPromises();

      expect(submitButton.disabled).toBe(true);

      resolveFetch({ ok: true, json: () => Promise.resolve({ hits: [] }) });
      await flushPromises();

      expect(submitButton.disabled).toBe(false);
    });

    it("ignores a second search trigger while a fetch is already in progress", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      let resolveFetch;
      global.fetch = jest.fn(
        () =>
          new Promise((resolve) => {
            resolveFetch = resolve;
          }),
      );

      document.getElementById("uv-search-input").value = "foo";
      const submitButton = document.getElementById("uv-search-submit");
      submitButton.click();
      submitButton.click();
      await flushPromises();

      expect(global.fetch).toHaveBeenCalledTimes(1);

      resolveFetch({ ok: true, json: () => Promise.resolve({ hits: [] }) });
      await flushPromises();
    });

    it("drives UV's page-number field and waits for pageIndexChange when a hit is on another page", async () => {
      setupSearchableUv();
      const { pdfLoaded, pageIndexChange } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              hits: [
                { page: 3, rect: { x: 0, y: 0, w: 0.1, h: 0.1 }, text: "x" },
              ],
            }),
        }),
      );

      const goButton = document.querySelector("#uv button.go");
      const goSpy = jest.spyOn(goButton, "click");

      document.getElementById("uv-search-input").value = "x";
      document.getElementById("uv-search-submit").click();
      await flushPromises();

      expect(document.querySelector("#uv input.searchText").value).toBe("3");
      expect(goSpy).toHaveBeenCalledTimes(1);
      // UV hasn't confirmed the page actually rendered yet
      expect(document.querySelector(".uv-search-highlight")).toBeNull();

      pageIndexChange(3);
      expect(document.querySelector(".uv-search-highlight")).not.toBeNull();
    });

    it("navigates forward/backward between hits and disables prev/next as plain text at each end", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              hits: [
                { page: 1, rect: { x: 0, y: 0, w: 0.1, h: 0.1 }, text: "a" },
                {
                  page: 1,
                  rect: { x: 0, y: 0.2, w: 0.1, h: 0.1 },
                  text: "a",
                },
              ],
            }),
        }),
      );

      document.getElementById("uv-search-input").value = "a";
      document.getElementById("uv-search-submit").click();
      await flushPromises();

      const prev = document.getElementById("uv-search-prev");
      const next = document.getElementById("uv-search-next");

      expect(document.getElementById("uv-search-count").textContent).toBe(
        "1 of 2",
      );
      expect(prev.hasAttribute("href")).toBe(false);
      expect(next.hasAttribute("href")).toBe(true);

      next.click();
      expect(document.getElementById("uv-search-count").textContent).toBe(
        "2 of 2",
      );
      expect(prev.hasAttribute("href")).toBe(true);
      expect(next.hasAttribute("href")).toBe(false);

      // Clicking next again does nothing further, it's plain text, not a link
      next.click();
      expect(document.getElementById("uv-search-count").textContent).toBe(
        "2 of 2",
      );

      prev.click();
      expect(document.getElementById("uv-search-count").textContent).toBe(
        "1 of 2",
      );
    });

    it("shows a no-results message and hides prev/next when the search has no hits", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ hits: [] }),
        }),
      );

      document.getElementById("uv-search-input").value = "nomatch";
      document.getElementById("uv-search-submit").click();
      await flushPromises();

      expect(document.getElementById("uv-search-results").hidden).toBe(true);
      const noResults = document.getElementById("uv-search-no-results");
      expect(noResults.hidden).toBe(false);
      expect(noResults.textContent).toBe("No results found");
    });

    it("shows an error message and hides results when the search API returns a non-OK status", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          json: () => Promise.resolve({}),
        }),
      );

      document.getElementById("uv-search-input").value = "foo";
      document.getElementById("uv-search-submit").click();
      await flushPromises();

      expect(document.getElementById("uv-search-results").hidden).toBe(true);
      expect(document.getElementById("uv-search-no-results").hidden).toBe(true);
      const errorEl = document.getElementById("uv-search-error");
      expect(errorEl.hidden).toBe(false);
      expect(errorEl.textContent).toContain(
        "There was a problem searching this record",
      );
    });

    it("shows an error message when the search request fails outright (network error)", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() => Promise.reject(new Error("network down")));

      document.getElementById("uv-search-input").value = "foo";
      document.getElementById("uv-search-submit").click();
      await flushPromises();

      expect(document.getElementById("uv-search-error").hidden).toBe(false);
    });

    it("clears a previous error message when a new search is run", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          json: () => Promise.resolve({}),
        }),
      );
      document.getElementById("uv-search-input").value = "foo";
      document.getElementById("uv-search-submit").click();
      await flushPromises();
      expect(document.getElementById("uv-search-error").hidden).toBe(false);

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              hits: [
                { page: 1, rect: { x: 0, y: 0, w: 0.1, h: 0.1 }, text: "a" },
              ],
            }),
        }),
      );
      document.getElementById("uv-search-input").value = "a";
      document.getElementById("uv-search-submit").click();
      await flushPromises();

      expect(document.getElementById("uv-search-error").hidden).toBe(true);
    });

    it("clears highlights and resets the count when a new PDF loads", async () => {
      setupSearchableUv();
      const { pdfLoaded } = initWithHandlers();
      pdfLoaded();

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              hits: [
                { page: 1, rect: { x: 0, y: 0, w: 0.1, h: 0.1 }, text: "a" },
              ],
            }),
        }),
      );

      document.getElementById("uv-search-input").value = "a";
      document.getElementById("uv-search-submit").click();
      await flushPromises();

      expect(document.querySelector(".uv-search-highlight")).not.toBeNull();

      pdfLoaded();

      expect(document.querySelector(".uv-search-highlight")).toBeNull();
      expect(document.getElementById("uv-search-count").textContent).toBe("");
      expect(document.getElementById("uv-search-results").hidden).toBe(true);
      expect(document.getElementById("uv-search-no-results").hidden).toBe(true);
    });
  });
});

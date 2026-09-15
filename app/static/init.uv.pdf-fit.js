// Universal Viewer's PDF.js panel always renders at a fixed scale with no
// fit-to-width, and that fixed scale can land either side of the container
// width depending on the document's page size (some load too big, some too
// small). The zoom button's per-click scale change isn't a fixed,
// predictable amount either (e.g. pdf.js caps the rendered canvas
// resolution for some page sizes), so rather than pre-computing a click
// count from an assumed scale/step, re-measure the actual canvas width
// after every click.

const UV_PDF_FIT_TARGET_RATIO = 0.8;
const UV_PDF_FIT_TOLERANCE = 0.1;
const UV_PDF_FIT_MAX_ATTEMPTS = 20;
const UV_PDF_FIT_MAX_CLICKS = 20;
const UV_PDF_FIT_RETRY_DELAY_MS = 250;

const getPdfCanvas = () => {
  const container = document.querySelector("#uv .pdfContainer");
  const canvas = container && container.querySelector("canvas");
  return { container, canvas };
};

const isCanvasMeasurable = ({ container, canvas }) =>
  Boolean(container && canvas && canvas.width && container.clientWidth);

const getFitTargets = (container) => {
  const targetWidth = container.clientWidth * UV_PDF_FIT_TARGET_RATIO;
  return { targetWidth, tolerance: targetWidth * UV_PDF_FIT_TOLERANCE };
};

const getZoomDirection = (canvas, targetWidth, tolerance) => {
  if (canvas.width < targetWidth - tolerance) {
    return "zoomIn";
  }
  if (canvas.width > targetWidth + tolerance) {
    return "zoomOut";
  }
  return null;
};

const isWithinFitTolerance = (canvas, fit) => {
  const { direction, targetWidth, tolerance } = fit;
  if (direction === "zoomIn") {
    return canvas.width >= targetWidth - tolerance;
  }
  return canvas.width <= targetWidth + tolerance;
};

const clickZoomButton = (direction) => {
  const button = document.querySelector(`#uv button.${direction}`);
  if (!button) {
    return false;
  }
  button.click();
  return true;
};

const zoomTowardsTargetWidth = (fit, clicks = 0) => {
  const { direction } = fit;
  const measurements = getPdfCanvas();
  if (!isCanvasMeasurable(measurements)) {
    return;
  }

  const withinTarget = isWithinFitTolerance(measurements.canvas, fit);
  if (withinTarget || clicks >= UV_PDF_FIT_MAX_CLICKS) {
    return;
  }
  if (!clickZoomButton(direction)) {
    return;
  }

  // Let pdf.js finish re-rendering the page at the new scale before
  // measuring again, otherwise we'd read the pre-click canvas size.
  setTimeout(() => {
    zoomTowardsTargetWidth(fit, clicks + 1);
  }, UV_PDF_FIT_RETRY_DELAY_MS);
};

const fitPdfToWidth = (attempt = 0) => {
  const measurements = getPdfCanvas();
  if (!isCanvasMeasurable(measurements)) {
    // The first render may not have finished when pdfLoaded fires
    if (attempt < UV_PDF_FIT_MAX_ATTEMPTS) {
      setTimeout(() => fitPdfToWidth(attempt + 1), UV_PDF_FIT_RETRY_DELAY_MS);
    }
    return;
  }

  const { container, canvas } = measurements;
  const { targetWidth, tolerance } = getFitTargets(container);
  const direction = getZoomDirection(canvas, targetWidth, tolerance);
  if (direction) {
    zoomTowardsTargetWidth({ direction, targetWidth, tolerance });
  }
};

window.fitPdfToWidth = fitPdfToWidth;

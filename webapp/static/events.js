// Captures scroll depth and time-spent events on a product page (US-8)
// and reports them to the backend EventCaptureService via small JSON posts.
(function () {
  const script = document.currentScript;
  const productId = script.getAttribute("data-product-id");
  if (!productId) return;

  let maxScrollDepth = 0;
  const pageLoadTime = Date.now();

  function currentScrollDepthPercent() {
    const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollableHeight <= 0) return 100;
    return Math.min(100, Math.round((window.scrollY / scrollableHeight) * 100));
  }

  window.addEventListener("scroll", function () {
    const depth = currentScrollDepthPercent();
    if (depth > maxScrollDepth) {
      maxScrollDepth = depth;
      fetch("/api/events/scroll", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId, scroll_depth_percent: depth }),
        keepalive: true,
      });
    }
  });

  window.addEventListener("beforeunload", function () {
    const durationSeconds = Math.round((Date.now() - pageLoadTime) / 1000);
    navigator.sendBeacon(
      "/api/events/time_spent",
      new Blob(
        [JSON.stringify({ product_id: productId, duration_seconds: durationSeconds })],
        { type: "application/json" }
      )
    );
  });
})();

// All images live in JS, no API needed
const IMAGES = [
  "https://picsum.photos/id/1015/600/400",
  "https://picsum.photos/id/1016/600/400",
  "https://picsum.photos/id/1024/600/400",
  "https://picsum.photos/id/1025/600/400",
  "https://picsum.photos/id/1035/600/400",
  "https://picsum.photos/id/1041/600/400",
  "https://picsum.photos/id/1050/600/400",
  "https://picsum.photos/id/1069/600/400",
  "https://picsum.photos/id/1074/600/400",
  "https://picsum.photos/id/1084/600/400"
];

// Read limit from URL query param
function getLimit() {
  const params = new URLSearchParams(window.location.search);
  let limit = parseInt(params.get('limit'), 10);
  if (!limit || limit <= 0) {
    limit = 5; // default value
  }
  return Math.min(limit, IMAGES.length); // don’t exceed total images
}

// Render images dynamically
function renderImages(container, template) {
  const limit = getLimit();
  const urls = IMAGES.slice(0, limit);

  container.innerHTML = '';
  urls.forEach(url => {
    const instance = template.content.cloneNode(true);
    const link = instance.querySelector('[data-image-link]');
    const img = instance.querySelector('[data-image-src]');

    if (link) link.href = url;
    if (img) img.src = url;

    container.appendChild(instance);
  });
}

// Keep all query parameters in the URL when clicking navigation links
function preserveQueryParams() {
  const currentParams = new URLSearchParams(window.location.search);
  const viewLinksButton = document.querySelector('a[href*="/links"]');
  if (!viewLinksButton) return;
  
  const linkUrl = new URL(viewLinksButton.href, window.location.origin);
  currentParams.forEach((value, key) => {
    linkUrl.searchParams.set(key, value);
  });
  viewLinksButton.href = linkUrl.pathname + linkUrl.search;
}

// Run after DOM loads
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('image-grid');
  const template = document.getElementById('image-card-template');
  if (!container || !template) return;

  renderImages(container, template);
  preserveQueryParams();
});
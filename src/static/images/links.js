// All images live in JS
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

// Render image links dynamically
function renderLinks(container, template) {
  const limit = getLimit();
  const urls = IMAGES.slice(0, limit);

  container.innerHTML = '';
  urls.forEach(url => {
    const instance = template.content.cloneNode(true);
    const anchor = instance.querySelector('[data-image-link]');
    if (anchor) {
      anchor.href = url;
      anchor.textContent = url;
    }
    container.appendChild(instance);
  });
}

// Keep all query parameters in the URL when clicking navigation links
function preserveQueryParams() {
  const currentParams = new URLSearchParams(window.location.search);
  const viewGalleryButton = document.querySelector('a[href*="/gallery"]');
  if (!viewGalleryButton) return;
  
  const linkUrl = new URL(viewGalleryButton.href, window.location.origin);
  currentParams.forEach((value, key) => {
    linkUrl.searchParams.set(key, value);
  });
  viewGalleryButton.href = linkUrl.pathname + linkUrl.search;
}

// Run after DOM loads
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('image-links');
  const template = document.getElementById('image-link-template');
  if (!container || !template) return;

  renderLinks(container, template);
  preserveQueryParams();
});
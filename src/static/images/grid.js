// Read limit and username from URL query param
function getParams() {
  const params = new URLSearchParams(window.location.search);
  let limit = parseInt(params.get('limit'), 10);
  if (!limit || limit <= 0) {
    limit = 100; // default high limit if not specified
  }
  const username = params.get('username');
  return { limit, username };
}

// Fetch images from API
async function fetchImages() {
    const { limit, username } = getParams();
    if (!username) return [];

    try {
        const response = await fetch(`/api/images?username=${encodeURIComponent(username)}`);
        const images = await response.json();
        return images.slice(0, limit);
    } catch (error) {
        console.error("Failed to fetch images", error);
        return [];
    }
}

// Render images dynamically
async function renderImages(container, template) {
  const urls = await fetchImages();

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
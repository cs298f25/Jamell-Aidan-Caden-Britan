// Read limit and username from URL query param
function getParams() {
  const params = new URLSearchParams(window.location.search);
  let limit = parseInt(params.get('limit'), 10);
  if (!limit || limit <= 0) {
    limit = 100;
  }
  const username = params.get('username');
  const category = params.get('category');
  return { limit, username, category };
}

// Fetch images from API
async function fetchImages() {
    const { limit, username, category } = getParams();
    if (!username) return [];

    try {
        let url = `/api/images?username=${encodeURIComponent(username)}`;
        if (category) {
            url += `&category=${encodeURIComponent(category)}`;
        }
        const response = await fetch(url);
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

function preserveQueryParams() {
  const currentParams = new URLSearchParams(window.location.search);
  const username = currentParams.get('username') || sessionStorage.getItem('username');
  
  // Store username in sessionStorage if found in URL
  if (currentParams.get('username')) {
    sessionStorage.setItem('username', currentParams.get('username'));
  }
  
  // Preserve username for main menu link
  const mainMenuLink = document.getElementById('main-menu-link');
  if (mainMenuLink && username) {
    mainMenuLink.href = `/auth?username=${encodeURIComponent(username)}`;
  }
  
  // Preserve all params for view links button
  const viewLinksButton = document.getElementById('view-links-link');
  if (viewLinksButton) {
    const linkUrl = new URL(viewLinksButton.href, window.location.origin);
    currentParams.forEach((value, key) => {
      linkUrl.searchParams.set(key, value);
    });
    viewLinksButton.href = linkUrl.pathname + linkUrl.search;
  }
}

// Run after DOM loads
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('image-grid');
  const template = document.getElementById('image-card-template');
  if (!container || !template) return;
  renderImages(container, template);
  preserveQueryParams();
});
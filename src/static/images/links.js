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

// Render image links dynamically
async function renderLinks(container, template) {
  const urls = await fetchImages();
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

function preserveQueryParams() {
  const currentParams = new URLSearchParams(window.location.search);
  const username = currentParams.get('username');
  
  // Preserve username for main menu link
  const mainMenuLink = document.getElementById('main-menu-link');
  if (mainMenuLink && username) {
    mainMenuLink.href = `/auth?username=${encodeURIComponent(username)}`;
  }
  
  // Preserve all params for view gallery button
  const viewGalleryButton = document.getElementById('view-gallery-link');
  if (viewGalleryButton) {
    const linkUrl = new URL(viewGalleryButton.href, window.location.origin);
    currentParams.forEach((value, key) => {
      linkUrl.searchParams.set(key, value);
    });
    viewGalleryButton.href = linkUrl.pathname + linkUrl.search;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('image-links');
  const template = document.getElementById('image-link-template');
  if (!container || !template) return;
  renderLinks(container, template);
  preserveQueryParams();
});
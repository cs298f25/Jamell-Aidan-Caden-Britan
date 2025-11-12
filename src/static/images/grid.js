const IMAGES_ENDPOINT = '/api/images';

function buildEndpoint() {
  const searchParams = new URLSearchParams(window.location.search);
  const limit = searchParams.get('limit');

  if (limit) {
    return `${IMAGES_ENDPOINT}?limit=${encodeURIComponent(limit)}`;
  }

  return IMAGES_ENDPOINT;
}

async function fetchImageUrls() {
  const endpoint = buildEndpoint();
  const response = await fetch(endpoint);

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  const data = await response.json();

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.images)) {
    return data.images;
  }

  return [];
}

function renderImages(urls, template, container) {
  urls.forEach((url) => {
    const instance = template.content.cloneNode(true);
    const link = instance.querySelector('[data-image-link]');
    const image = instance.querySelector('[data-image-src]');

    if (link) {
      link.href = url;
    }

    if (image) {
      image.src = url;
      image.alt = 'Image';
    }

    container.appendChild(instance);
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  const template = document.getElementById('image-card-template');
  const container = document.getElementById('image-grid');

  if (!template || !container) {
    return;
  }

  try {
    const urls = await fetchImageUrls();
    renderImages(urls, template, container);
  } catch (error) {
    console.error('Failed to load images:', error);
  }
});


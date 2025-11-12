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

function renderImageLinks(urls, template, list) {
  urls.forEach((url) => {
    const instance = template.content.cloneNode(true);
    const anchor = instance.querySelector('[data-image-link]');

    if (anchor) {
      anchor.href = url;
      anchor.textContent = url;
    }

    list.appendChild(instance);
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  const template = document.getElementById('image-link-template');
  const list = document.getElementById('image-links');

  if (!template || !list) {
    return;
  }

  try {
    const urls = await fetchImageUrls();
    renderImageLinks(urls, template, list);
  } catch (error) {
    console.error('Failed to load image links:', error);
  }
});


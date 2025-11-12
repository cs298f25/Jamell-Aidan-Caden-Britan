document.addEventListener('DOMContentLoaded', () => {
  const dataElement = document.getElementById('image-data');
  const template = document.getElementById('image-card-template');
  const container = document.getElementById('image-grid');

  if (!dataElement || !template || !container) {
    return;
  }

  let imageUrls = [];

  try {
    imageUrls = JSON.parse(dataElement.textContent || '[]');
  } catch (error) {
    console.error('Failed to parse image data:', error);
    return;
  }

  imageUrls.forEach((url) => {
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
});


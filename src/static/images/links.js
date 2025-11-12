document.addEventListener('DOMContentLoaded', () => {
  const dataElement = document.getElementById('image-links-data');
  const template = document.getElementById('image-link-template');
  const list = document.getElementById('image-links');

  if (!dataElement || !template || !list) {
    return;
  }

  let imageUrls = [];

  try {
    imageUrls = JSON.parse(dataElement.textContent || '[]');
  } catch (error) {
    console.error('Failed to parse image links data:', error);
    return;
  }

  imageUrls.forEach((url) => {
    const instance = template.content.cloneNode(true);
    const anchor = instance.querySelector('[data-image-link]');

    if (anchor) {
      anchor.href = url;
      anchor.textContent = url;
    }

    list.appendChild(instance);
  });
});


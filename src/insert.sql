INSERT INTO users (username) VALUES ('testuser'), ('testuser2'), ('testuser3');
INSERT INTO images (user_id, image_url) VALUES (1, 'https://picsum.photos/id/1015/600/400'), (2, 'https://picsum.photos/id/1016/600/400'), (3, 'https://picsum.photos/id/1024/600/400');
INSERT INTO categories (user_id, name) VALUES (1, 'testcategory'), (2, 'testcategory2'), (3, 'testcategory3');
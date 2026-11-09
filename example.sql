-- ===========================================================
--  ตัวอย่างฐานข้อมูล: ร้านเค้ก (Cake Shop) · IT234
--  วิธีใช้: เปิด DB Browser for SQLite > แท็บ Execute SQL
--          วางทั้งไฟล์นี้ แล้วกด ▶ (Execute all) และกด Write Changes
-- ===========================================================

PRAGMA foreign_keys = ON;

-- หมวดหมู่เค้ก (1 หมวด มีได้หลายเค้ก)
CREATE TABLE categories (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

-- เค้ก (แต่ละชิ้นอยู่ใน 1 หมวด หรือยังไม่มีหมวดก็ได้)
CREATE TABLE cakes (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL,
  price       REAL    NOT NULL CHECK (price >= 0),
  image       TEXT,                                        -- ลิงก์รูปภาพ
  stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
  category_id INTEGER REFERENCES categories(id)
);

-- สมาชิก (1 คน สั่งได้หลายออเดอร์)
CREATE TABLE members (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  nickname  TEXT NOT NULL,
  email     TEXT NOT NULL UNIQUE,
  joined_at DATE NOT NULL DEFAULT (date('now'))
);

-- ออเดอร์ (แต่ละออเดอร์เป็นของสมาชิก 1 คน)
CREATE TABLE orders (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id  INTEGER NOT NULL REFERENCES members(id),
  order_date DATE    NOT NULL DEFAULT (date('now'))
);

-- รายการในออเดอร์ (ตารางเชื่อม: 1 ออเดอร์มีหลายเค้ก และ 1 เค้กอยู่ได้หลายออเดอร์)
CREATE TABLE order_items (
  order_id INTEGER NOT NULL REFERENCES orders(id),
  cake_id  INTEGER NOT NULL REFERENCES cakes(id),
  qty      INTEGER NOT NULL DEFAULT 1 CHECK (qty > 0),
  PRIMARY KEY (order_id, cake_id)
);

-- ---------------- ข้อมูลตัวอย่าง ----------------
INSERT INTO categories (name) VALUES
  ('Chocolate'), ('Fruit'), ('Cheese cake'), ('Premium'), ('Birthday');

INSERT INTO cakes (name, price, image, stock, category_id) VALUES
  ('Chocolate Lava Cake',        120, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c', 2,  1),
  ('Dark Chocolate Mousse',      150, 'https://images.unsplash.com/photo-1578985545062-69928b1d9587', 20, 1),
  ('Strawberry Shortcake',       135, 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e', 10, 2),
  ('Blueberry Cheesecake',       160, 'https://images.unsplash.com/photo-1542826438-bd32f43d626f',   5,  3),
  ('New York Cheesecake',        140, 'https://images.unsplash.com/photo-1551024601-bec78aea704b',   3,  3),
  ('Burnt Cheesecake',           155, 'https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b', 0,  3),
  ('Gold Chocolate Cake',        290, 'https://images.unsplash.com/photo-1599785209796-786432b228bc', 1,  4),
  ('Royal Strawberry Crown Cake',280, 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62', 4,  4);

INSERT INTO members (nickname, email, joined_at) VALUES
  ('มินตรา', 'mintra@example.com', '2026-09-01'),
  ('ภูมิ',   'phum@example.com',   '2026-09-15'),
  ('ฟ้าใส',  'fasai@example.com',  '2026-10-02');

INSERT INTO orders (member_id, order_date) VALUES
  (1, '2026-10-05'), (1, '2026-10-12'), (2, '2026-10-12'), (3, '2026-10-20');

INSERT INTO order_items (order_id, cake_id, qty) VALUES
  (1, 1, 2), (1, 3, 1),
  (2, 5, 1),
  (3, 2, 1), (3, 7, 1),
  (4, 4, 2), (4, 1, 1);

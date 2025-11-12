# PostgreSQL 实践示例

本章节提供实际的 PostgreSQL 使用示例，包括完整的应用场景、SQL 查询示例和数据库操作示例。

## 电商应用数据库设计

### 1. 数据库结构设计

```sql
-- 创建数据库
CREATE DATABASE ecommerce;
\c ecommerce

-- 创建枚举类型
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE payment_method AS ENUM ('credit_card', 'debit_card', 'paypal', 'bank_transfer');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    user_status user_status DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 用户地址表
CREATE TABLE user_addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_type VARCHAR(20) NOT NULL CHECK (address_type IN ('shipping', 'billing')),
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT false
);

-- 产品分类表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id),
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    cost_price NUMERIC(10,2),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    weight NUMERIC(8,3),
    dimensions JSONB,
    images JSONB,
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品变体表（颜色、尺寸等）
CREATE TABLE product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(100) UNIQUE NOT NULL,
    variant_name VARCHAR(100),
    price_adjustment NUMERIC(10,2) DEFAULT 0,
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    attributes JSONB NOT NULL
);

-- 购物车表
CREATE TABLE shopping_carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),  -- 对于未登录用户
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, session_id)
);

-- 购物车项目表
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES shopping_carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL,  -- 添加时的价格
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    status order_status DEFAULT 'pending',
    subtotal NUMERIC(10,2) NOT NULL,
    tax_amount NUMERIC(10,2) DEFAULT 0,
    shipping_amount NUMERIC(10,2) DEFAULT 0,
    total_amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method payment_method,
    payment_status VARCHAR(20) DEFAULT 'pending',
    shipping_address JSONB NOT NULL,
    billing_address JSONB NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单项目表
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(10,2) NOT NULL
);

-- 库存变动记录表
CREATE TABLE inventory_movements (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('purchase', 'sale', 'adjustment', 'return')),
    quantity_change INTEGER NOT NULL,  -- 正数为增加，负数为减少
    reference_id INTEGER,  -- 关联的订单ID或其他参考
    reference_type VARCHAR(50),  -- 'order', 'purchase', 'adjustment'
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- 产品评论表
CREATE TABLE product_reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    user_id INTEGER REFERENCES users(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    review_text TEXT,
    is_verified BOOLEAN DEFAULT false,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户浏览历史表
CREATE TABLE user_browsing_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),  -- 对于未登录用户
    product_id INTEGER REFERENCES products(id),
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER  -- 查看时长（秒）
);

-- 索引创建
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(user_status);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_products_name ON products USING gin(to_tsvector('english', name));
CREATE INDEX idx_products_tags ON products USING gin(tags);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_number ON orders(order_number);

CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id, variant_id);

CREATE INDEX idx_inventory_movements_product ON inventory_movements(product_id, variant_id);
CREATE INDEX idx_inventory_movements_created_at ON inventory_movements(created_at);

CREATE INDEX idx_product_reviews_product ON product_reviews(product_id);
CREATE INDEX idx_product_reviews_rating ON product_reviews(rating);

-- 创建触发器更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shopping_carts_updated_at
    BEFORE UPDATE ON shopping_carts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_reviews_updated_at
    BEFORE UPDATE ON product_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2. 数据插入示例

```sql
-- 插入分类数据
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Home & Garden', 'Home improvement and garden supplies'),
('Books', 'Books and educational materials'),
('Sports', 'Sports equipment and accessories');

-- 插入子分类
INSERT INTO categories (name, description, parent_id) VALUES
('Smartphones', 'Mobile phones and accessories', 1),
('Laptops', 'Laptop computers', 1),
('T-Shirts', 'Casual t-shirts', 2),
('Jeans', 'Denim jeans', 2);

-- 插入用户数据
INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES
('john_doe', 'john@example.com', crypt('password123', gen_salt('bf', 12)), 'John', 'Doe'),
('jane_smith', 'jane@example.com', crypt('password456', gen_salt('bf', 12)), 'Jane', 'Smith'),
('bob_johnson', 'bob@example.com', crypt('password789', gen_salt('bf', 12)), 'Bob', 'Johnson');

-- 插入产品数据
INSERT INTO products (category_id, sku, name, description, price, stock_quantity, tags) VALUES
(6, 'IPHONE14-128-BLK', 'iPhone 14 128GB Black', 'Apple iPhone 14 with 128GB storage', 799.00, 50, ARRAY['apple', 'smartphone', '5g']),
(6, 'GALAXY-S23-128', 'Samsung Galaxy S23 128GB', 'Samsung Galaxy S23 with 128GB storage', 799.00, 30, ARRAY['samsung', 'smartphone', 'android']),
(7, 'MACBOOK-AIR-M2', 'MacBook Air M2', 'Apple MacBook Air with M2 chip', 1199.00, 25, ARRAY['apple', 'laptop', 'm2']),
(7, 'THINKPAD-X1', 'ThinkPad X1 Carbon', 'Lenovo ThinkPad X1 Carbon laptop', 1599.00, 15, ARRAY['lenovo', 'laptop', 'business']),
(8, 'COTTON-TSHIRT-M', 'Cotton T-Shirt Medium', '100% cotton t-shirt', 19.99, 100, ARRAY['cotton', 'casual', 't-shirt']),
(9, 'SLIM-FIT-JEANS-32', 'Slim Fit Jeans 32', 'Modern slim fit denim jeans', 79.99, 75, ARRAY['denim', 'jeans', 'slim-fit']);

-- 插入产品变体
INSERT INTO product_variants (product_id, sku, variant_name, price_adjustment, stock_quantity, attributes) VALUES
(8, 'COTTON-TSHIRT-M-BLUE', 'Cotton T-Shirt Medium Blue', 0.00, 30, '{"color": "blue", "size": "M"}'),
(8, 'COTTON-TSHIRT-M-RED', 'Cotton T-Shirt Medium Red', 0.00, 25, '{"color": "red", "size": "M"}'),
(8, 'COTTON-TSHIRT-L-BLUE', 'Cotton T-Shirt Large Blue', 0.00, 20, '{"color": "blue", "size": "L"}'),
(9, 'SLIM-FIT-JEANS-32-BLACK', 'Slim Fit Jeans 32 Black', 0.00, 25, '{"color": "black", "size": "32"}'),
(9, 'SLIM-FIT-JEANS-32-BLUE', 'Slim Fit Jeans 32 Blue', 0.00, 30, '{"color": "blue", "size": "32"}');
```

## 高级 SQL 查询示例

### 1. 销售分析查询

```sql
-- 月度销售统计
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', created_at) as month,
        COUNT(*) as order_count,
        SUM(total_amount) as total_sales,
        AVG(total_amount) as avg_order_value
    FROM orders
    WHERE status NOT IN ('cancelled')
    AND created_at >= DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '1 year'
    GROUP BY DATE_TRUNC('month', created_at)
)
SELECT
    month,
    order_count,
    ROUND(total_sales, 2) as total_sales,
    ROUND(avg_order_value, 2) as avg_order_value,
    ROUND(total_sales - LAG(total_sales) OVER (ORDER BY month), 2) as sales_change
FROM monthly_sales
ORDER BY month DESC;

-- 热门产品销售排行
SELECT
    p.name,
    p.category_id,
    c.name as category_name,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.total_price) as total_revenue,
    COUNT(DISTINCT o.id) as order_count,
    AVG(oi.unit_price) as avg_selling_price
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
WHERE o.status NOT IN ('cancelled')
AND o.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.id, p.name, p.category_id, c.name
ORDER BY total_quantity_sold DESC
LIMIT 10;

-- 用户购买行为分析
WITH user_purchases AS (
    SELECT
        u.id as user_id,
        u.username,
        COUNT(DISTINCT o.id) as order_count,
        SUM(o.total_amount) as total_spent,
        AVG(o.total_amount) as avg_order_value,
        MIN(o.created_at) as first_purchase,
        MAX(o.created_at) as last_purchase,
        COUNT(DISTINCT p.category_id) as categories_purchased
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id AND o.status NOT IN ('cancelled')
    LEFT JOIN order_items oi ON o.id = oi.order_id
    LEFT JOIN products p ON oi.product_id = p.id
    GROUP BY u.id, u.username
)
SELECT
    user_id,
    username,
    order_count,
    ROUND(total_spent, 2) as total_spent,
    ROUND(avg_order_value, 2) as avg_order_value,
    first_purchase,
    last_purchase,
    categories_purchased,
    CASE
        WHEN order_count = 0 THEN 'New'
        WHEN order_count <= 2 THEN 'Occasional'
        WHEN order_count <= 5 THEN 'Regular'
        ELSE 'VIP'
    END as customer_tier
FROM user_purchases
ORDER BY total_spent DESC;

-- 库存周转分析
SELECT
    p.name,
    p.stock_quantity,
    COALESCE(SUM(oi.quantity), 0) as sold_last_month,
    CASE
        WHEN COALESCE(SUM(oi.quantity), 0) = 0 THEN 'Never Sold'
        WHEN p.stock_quantity = 0 THEN 'Out of Stock'
        WHEN p.stock_quantity <= COALESCE(SUM(oi.quantity), 0) * 0.1 THEN 'Low Stock'
        ELSE 'In Stock'
    END as stock_status,
    ROUND(
        CASE
            WHEN COALESCE(SUM(oi.quantity), 0) > 0
            THEN p.stock_quantity::NUMERIC / COALESCE(SUM(oi.quantity), 1) * 30
            ELSE 999
        END, 1
    ) as days_of_inventory
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.created_at >= CURRENT_DATE - INTERVAL '30 days' AND o.status NOT IN ('cancelled')
WHERE p.is_active = true
GROUP BY p.id, p.name, p.stock_quantity
ORDER BY days_of_inventory ASC;
```

### 2. 实时库存查询

```sql
-- 实时库存状态（包括预订单库存）
WITH inventory_summary AS (
    -- 当前库存
    SELECT
        product_id,
        variant_id,
        stock_quantity as available_stock
    FROM product_variants

    UNION ALL

    -- 产品本身（没有变体的情况）
    SELECT
        id as product_id,
        NULL as variant_id,
        stock_quantity as available_stock
    FROM products
    WHERE id NOT IN (SELECT DISTINCT product_id FROM product_variants)

    UNION ALL

    -- 购物车中预留的库存
    SELECT
        ci.product_id,
        ci.variant_id,
        SUM(ci.quantity) * -1 as available_stock
    FROM cart_items ci
    JOIN shopping_carts sc ON ci.cart_id = sc.id
    JOIN orders o ON sc.user_id = o.user_id AND o.status = 'pending'
    WHERE ci.created_at >= CURRENT_DATE - INTERVAL '1 hour'  -- 1小时内的购物车
    GROUP BY ci.product_id, ci.variant_id
)
SELECT
    COALESCE(p.name, pv.product_id::TEXT) as product_name,
    COALESCE(c.name, 'Uncategorized') as category_name,
    pv.variant_name,
    SUM(available_stock) as real_available_stock,
    CASE
        WHEN SUM(available_stock) <= 0 THEN 'Out of Stock'
        WHEN SUM(available_stock) <= 5 THEN 'Low Stock'
        ELSE 'Available'
    END as stock_status
FROM inventory_summary inv
LEFT JOIN product_variants pv ON inv.product_id = pv.product_id AND inv.variant_id = pv.variant_id
LEFT JOIN products p ON inv.product_id = p.id
LEFT JOIN categories c ON p.category_id = c.id
GROUP BY p.name, pv.product_id, pv.variant_name, c.name
ORDER BY real_available_stock ASC;
```

### 3. 推荐系统查询

```sql
-- 基于用户行为的商品推荐
WITH user_profile AS (
    -- 用户购买和浏览的商品类别偏好
    SELECT
        u.id as user_id,
        p.category_id,
        COUNT(*) as interaction_count,
        SUM(CASE WHEN o.id IS NOT NULL THEN 3 ELSE 1 END) as weighted_score
    FROM users u
    LEFT JOIN user_browsing_history bh ON u.id = bh.user_id
    LEFT JOIN orders o ON u.id = o.user_id AND o.status NOT IN ('cancelled')
    LEFT JOIN order_items oi ON o.id = oi.order_id
    LEFT JOIN products p ON (bh.product_id = p.id OR oi.product_id = p.id)
    WHERE p.id IS NOT NULL
    GROUP BY u.id, p.category_id
),
category_recommendations AS (
    -- 找出用户偏好的类别中的热门商品
    SELECT
        up.user_id,
        up.category_id,
        p.id as product_id,
        p.name,
        p.price,
        SUM(oi.quantity) as category_popularity
    FROM user_profile up
    JOIN products p ON up.category_id = p.category_id
    LEFT JOIN order_items oi ON p.id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.id AND o.status NOT IN ('cancelled'
WHERE p.is_active = true
    AND p.stock_quantity > 0
    GROUP BY up.user_id, up.category_id, p.id, p.name, p.price
)
SELECT DISTINCT ON (user_id)
    user_id,
    product_id,
    name,
    price,
    category_popularity
FROM category_recommendations
WHERE product_id NOT IN (
    SELECT product_id FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE o.user_id = category_recommendations.user_id
)
ORDER BY user_id, category_popularity DESC;

-- 协同过滤推荐
WITH similar_users AS (
    -- 找到相似用户（购买相同商品的用户）
    SELECT
        o1.user_id as user_a,
        o2.user_id as user_b,
        COUNT(DISTINCT oi1.product_id) as common_products
    FROM orders o1
    JOIN order_items oi1 ON o1.id = oi1.order_id
    JOIN orders o2 ON o1.user_id != o2.user_id
    JOIN order_items oi2 ON o2.id = oi2.order_id AND oi1.product_id = oi2.product_id
    WHERE o1.status NOT IN ('cancelled') AND o2.status NOT IN ('cancelled')
    GROUP BY o1.user_id, o2.user_id
    HAVING COUNT(DISTINCT oi1.product_id) >= 2
),
collaborative_recommendations AS (
    -- 基于相似用户的购买推荐商品
    SELECT
        su.user_a,
        oi2.product_id,
        p.name,
        p.price,
        COUNT(*) as recommendation_score
    FROM similar_users su
    JOIN order_items oi2 ON su.user_b = oi2.order_id
    JOIN products p ON oi2.product_id = p.id
    WHERE oi2.product_id NOT IN (
        SELECT product_id FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.user_id = su.user_a AND o.status NOT IN ('cancelled')
    )
    GROUP BY su.user_a, oi2.product_id, p.name, p.price
)
SELECT
    cr.user_a as user_id,
    cr.product_id,
    cr.name,
    cr.price,
    cr.recommendation_score
FROM collaborative_recommendations cr
ORDER BY cr.user_a, cr.recommendation_score DESC;
```

## 复杂业务逻辑示例

### 1. 动态定价策略

```sql
-- 基于库存和需求的动态定价函数
CREATE OR REPLACE FUNCTION calculate_dynamic_price(
    product_id_param INTEGER,
    variant_id_param INTEGER DEFAULT NULL
) RETURNS NUMERIC AS $$
DECLARE
    current_price NUMERIC;
    stock_level INTEGER;
    recent_sales INTEGER;
    price_adjustment NUMERIC := 0;
    base_price NUMERIC;
BEGIN
    -- 获取当前价格
    IF variant_id_param IS NOT NULL THEN
        SELECT p.price + COALESCE(pv.price_adjustment, 0), pv.stock_quantity
        INTO base_price, stock_level
        FROM products p
        JOIN product_variants pv ON p.id = pv.product_id
        WHERE p.id = product_id_param AND pv.id = variant_id_param;
    ELSE
        SELECT price, stock_quantity
        INTO base_price, stock_level
        FROM products
        WHERE id = product_id_param;
    END IF;

    -- 获取最近7天的销售量
    SELECT COALESCE(SUM(quantity), 0)
    INTO recent_sales
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE (oi.product_id = product_id_param)
      AND (variant_id_param IS NULL OR oi.variant_id = variant_id_param)
      AND o.created_at >= CURRENT_DATE - INTERVAL '7 days'
      AND o.status NOT IN ('cancelled');

    -- 基于库存水平调整价格
    IF stock_level <= 5 THEN
        price_adjustment := price_adjustment + (base_price * 0.10);  -- 低库存涨价10%
    ELSIF stock_level <= 20 THEN
        price_adjustment := price_adjustment + (base_price * 0.05);  -- 中等库存涨价5%
    END IF;

    -- 基于销售速度调整价格
    IF recent_sales > 50 THEN
        price_adjustment := price_adjustment + (base_price * 0.15);  -- 热销涨价15%
    ELSIF recent_sales > 20 THEN
        price_adjustment := price_adjustment + (base_price * 0.08);  -- 畅销涨价8%
    ELSIF recent_sales < 5 THEN
        price_adjustment := price_adjustment - (base_price * 0.10);  -- 滞销降价10%
    END IF;

    -- 确保价格不会低于成本的80%
    SELECT cost_price INTO FROM products WHERE id = product_id_param;
    IF cost_price IS NOT NULL THEN
        price_adjustment := GREATEST(price_adjustment, (base_price * 0.80) - base_price);
    END IF;

    RETURN base_price + price_adjustment;
END;
$$ LANGUAGE plpgsql;

-- 使用动态定价
SELECT
    p.name,
    pv.variant_name,
    p.price as base_price,
    calculate_dynamic_price(p.id, pv.id) as dynamic_price,
    ROUND(calculate_dynamic_price(p.id, pv.id) - p.price, 2) as price_difference
FROM products p
LEFT JOIN product_variants pv ON p.id = pv.product_id
WHERE p.is_active = true;
```

### 2. 智能库存补货系统

```sql
-- 库存补货建议
CREATE OR REPLACE FUNCTION generate_restock_recommendations()
RETURNS TABLE(
    product_id INTEGER,
    variant_id INTEGER,
    product_name VARCHAR(255),
    variant_name VARCHAR(100),
    current_stock INTEGER,
    recommended_quantity INTEGER,
    recommended_date DATE,
    reason TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH demand_forecast AS (
        -- 计算过去30天的平均日销量
        SELECT
            COALESCE(oi.product_id, pv.product_id) as product_id,
            COALESCE(oi.variant_id, pv.id) as variant_id,
            AVG(oi.quantity) as daily_avg_sales,
            STDDEV(oi.quantity) as sales_volatility
        FROM product_variants pv
        LEFT JOIN order_items oi ON pv.id = oi.variant_id
        LEFT JOIN orders o ON oi.order_id = o.id AND o.created_at >= CURRENT_DATE - INTERVAL '30 days' AND o.status NOT IN ('cancelled')
        GROUP BY COALESCE(oi.product_id, pv.product_id), COALESCE(oi.variant_id, pv.id)
    ),
    lead_time_days AS (
        -- 计算供应商平均交货时间（这里假设为14天）
        SELECT 14 as avg_lead_time
    ),
    safety_stock_calculations AS (
        SELECT
            df.product_id,
            df.variant_id,
            pv.stock_quantity as current_stock,
            df.daily_avg_sales,
            df.sales_volatility,
            lt.avg_lead_time,
            -- 计算安全库存（考虑需求变异性）
            CEIL(df.daily_avg_sales * lt.avg_lead_time + (df.sales_volatility * SQRT(lt.avg_lead_time))) as safety_stock,
            -- 计算再订货点
            CEIL(df.daily_avg_sales * lt.avg_lead_time) as reorder_point
        FROM demand_forecast df
        JOIN product_variants pv ON df.product_id = pv.product_id AND (df.variant_id = pv.id OR (df.variant_id IS NULL AND pv.id IS NULL))
        CROSS JOIN lead_time_days lt
        WHERE pv.stock_quantity IS NOT NULL
    )
    SELECT
        ssc.product_id,
        ssc.variant_id,
        p.name as product_name,
        pv.variant_name,
        ssc.current_stock,
        CASE
            WHEN ssc.current_stock <= ssc.reorder_point THEN
                GREATEST(CEIL(ssc.daily_avg_sales * ssc.avg_lead_time * 2) - ssc.current_stock, 0)
            WHEN ssc.current_stock <= ssc.safety_stock THEN
                GREATEST(CEIL(ssc.safety_stock) - ssc.current_stock, 0)
            ELSE 0
        END as recommended_quantity,
        CASE
            WHEN ssc.current_stock <= ssc.reorder_point THEN
                CURRENT_DATE + (ssc.avg_lead_time::TEXT || ' days')::INTERVAL
            WHEN ssc.current_stock <= ssc.safety_stock THEN
                CURRENT_DATE + (ssc.avg_lead_time::TEXT || ' days')::INTERVAL
            ELSE NULL
        END as recommended_date,
        CASE
            WHEN ssc.current_stock <= ssc.reorder_point THEN
                'Below reorder point - immediate restock needed'
            WHEN ssc.current_stock <= ssc.safety_stock THEN
                'Below safety stock - restock recommended'
            ELSE 'Adequate stock - no action needed'
        END as reason
    FROM safety_stock_calculations ssc
    JOIN products p ON ssc.product_id = p.id
    LEFT JOIN product_variants pv ON ssc.variant_id = pv.id
    WHERE ssc.current_stock <= ssc.safety_stock
    ORDER BY ssc.current_stock ASC;
END;
$$ LANGUAGE plpgsql;

-- 获取补货建议
SELECT * FROM generate_restock_recommendations();
```

这些示例展示了 PostgreSQL 在实际应用中的强大功能，包括复杂的数据建模、高级查询和业务逻辑实现。通过这些实践示例，可以更好地理解如何在实际项目中使用 PostgreSQL。
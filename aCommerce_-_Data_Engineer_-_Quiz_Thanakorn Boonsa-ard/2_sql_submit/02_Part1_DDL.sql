CREATE TABLE shop (
    shop_id      VARCHAR(50)  PRIMARY KEY,
    shop_name    VARCHAR(255) NOT NULL,
    country      CHAR(2)      NOT NULL,
    created_time TIMESTAMPTZ  NOT NULL
);

CREATE TABLE item (
    item_id      VARCHAR(50)  PRIMARY KEY,
    item_type    VARCHAR(50)  NOT NULL,
    item_name    VARCHAR(255) NOT NULL,
    created_time TIMESTAMPTZ  NOT NULL
);

CREATE TABLE promotion (
    promotion_id   VARCHAR(100) PRIMARY KEY,
    promotion_name VARCHAR(255) NOT NULL,
    start_time     TIMESTAMPTZ  NOT NULL,
    end_time       TIMESTAMPTZ  NOT NULL
);

CREATE TABLE promotion_product (
    promotion_id VARCHAR(100) NOT NULL REFERENCES promotion(promotion_id),
    product_id   VARCHAR(100) NOT NULL,
    PRIMARY KEY (promotion_id, product_id)
);

CREATE INDEX idx_promotion_product_pid ON promotion_product(product_id);

CREATE TABLE sales_order (
    sales_order_id VARCHAR(100) PRIMARY KEY,
    shop_id        VARCHAR(50)  NOT NULL REFERENCES shop(shop_id),
    created_time   TIMESTAMPTZ  NOT NULL,
    currency_code  CHAR(3)      NOT NULL
);

CREATE INDEX idx_sales_order_created ON sales_order(created_time);
CREATE INDEX idx_sales_order_shop    ON sales_order(shop_id);

CREATE TABLE sales_order_line (
    sales_order_id        VARCHAR(100)  NOT NULL REFERENCES sales_order(sales_order_id),
    line_number           INT           NOT NULL,
    product_id            VARCHAR(100)  NOT NULL,
    quantity              INT           NOT NULL,
    gross_amount          NUMERIC(18,2) NOT NULL,
    reference_line_number INT,
    PRIMARY KEY (sales_order_id, line_number)
);

CREATE INDEX idx_sol_product ON sales_order_line(product_id);

CREATE TABLE sales_order_line_item (
    sales_order_id VARCHAR(100) NOT NULL,
    line_number    INT          NOT NULL,
    item_id        VARCHAR(50)  NOT NULL REFERENCES item(item_id),
    item_type      VARCHAR(50)  NOT NULL,
    quantity       INT          NOT NULL,
    PRIMARY KEY (sales_order_id, line_number, item_id),
    FOREIGN KEY (sales_order_id, line_number)
        REFERENCES sales_order_line(sales_order_id, line_number)
);

CREATE INDEX idx_soli_item ON sales_order_line_item(item_id);

CREATE TABLE item_receipt (
    receipt_id    VARCHAR(100) PRIMARY KEY,
    supplier_id   VARCHAR(100) NOT NULL,
    received_time TIMESTAMPTZ  NOT NULL,
    currency_code CHAR(3)      NOT NULL
);

CREATE INDEX idx_receipt_received ON item_receipt(received_time);

CREATE TABLE item_receipt_line (
    receipt_line_id  BIGSERIAL     PRIMARY KEY,
    receipt_id       VARCHAR(100)  NOT NULL REFERENCES item_receipt(receipt_id),
    line_number      INT           NOT NULL,
    item_id          VARCHAR(50)   NOT NULL REFERENCES item(item_id),
    expiry_date      DATE,
    quantity         INT           NOT NULL,
    purchased_amount NUMERIC(18,2) NOT NULL
);

CREATE INDEX idx_irl_receipt ON item_receipt_line(receipt_id);
CREATE INDEX idx_irl_item    ON item_receipt_line(item_id);

CREATE TABLE daily_usd_exchange_rate (
    rate_date     DATE          NOT NULL,
    currency_code CHAR(3)       NOT NULL,
    rate          NUMERIC(18,6) NOT NULL,
    PRIMARY KEY (rate_date, currency_code)
);
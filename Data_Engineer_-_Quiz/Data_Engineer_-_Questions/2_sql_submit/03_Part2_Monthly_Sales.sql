SELECT
    DATE_TRUNC('month', so.created_time)  AS sales_month,
    p.promotion_id,
    p.promotion_name,
    SUM(sol.gross_amount / er.rate)       AS total_sales_usd
FROM sales_order             so
JOIN sales_order_line        sol ON so.sales_order_id = sol.sales_order_id
                                AND sol.gross_amount  > 0
JOIN promotion_product       pp  ON sol.product_id    = pp.product_id
JOIN promotion               p   ON pp.promotion_id   = p.promotion_id
                                AND so.created_time BETWEEN p.start_time AND p.end_time
JOIN daily_usd_exchange_rate er  ON er.rate_date      = DATE(so.created_time AT TIME ZONE 'UTC')
                                AND er.currency_code  = so.currency_code
GROUP BY
    DATE_TRUNC('month', so.created_time),
    p.promotion_id,
    p.promotion_name
ORDER BY
    sales_month,
    p.promotion_id;
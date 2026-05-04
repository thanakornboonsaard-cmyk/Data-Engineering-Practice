WITH
receipts_cumulative AS (
    SELECT
        irl.item_id,
        irl.receipt_line_id,
        irl.purchased_amount / NULLIF(irl.quantity, 0)  AS unit_cost,
        SUM(irl.quantity) OVER w                        AS cum_received,
        SUM(irl.quantity) OVER w - irl.quantity          AS prev_cum_received
    FROM item_receipt    ir
    JOIN item_receipt_line irl ON ir.receipt_id = irl.receipt_id
    WINDOW w AS (
        PARTITION BY irl.item_id
        ORDER BY ir.received_time, ir.receipt_id, irl.receipt_line_id
    )
),
sales_cumulative AS (
    SELECT
        so.sales_order_id,
        soli.item_id,
        SUM(soli.quantity) OVER w          AS cum_sold,
        SUM(soli.quantity) OVER w
            - soli.quantity                AS prev_cum_sold
    FROM sales_order           so
    JOIN sales_order_line      sol  ON so.sales_order_id = sol.sales_order_id
    JOIN sales_order_line_item soli ON so.sales_order_id = soli.sales_order_id
                                    AND sol.line_number   = soli.line_number
    WHERE soli.item_type = 'Item'
    WINDOW w AS (
        PARTITION BY soli.item_id
        ORDER BY so.created_time, so.sales_order_id
    )
),
fifo_match AS (
    SELECT
        s.sales_order_id,
        r.unit_cost,
        LEAST(s.cum_sold, r.cum_received)
            - GREATEST(s.prev_cum_sold, r.prev_cum_received)  AS matched_qty
    FROM sales_cumulative    s
    JOIN receipts_cumulative r
      ON s.item_id = r.item_id
     AND LEAST(s.cum_sold, r.cum_received)
           > GREATEST(s.prev_cum_sold, r.prev_cum_received)
)
SELECT
    sales_order_id,
    ROUND(SUM(matched_qty * unit_cost), 2) AS cogs
FROM fifo_match
GROUP BY sales_order_id
ORDER BY sales_order_id;
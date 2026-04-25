-- Feature layer for user-level lifecycle analytics from events_staging.

CREATE OR REPLACE TABLE user_features AS
WITH event_base AS (
    SELECT
        user_id,
        LOWER(event_type) AS event_type,
        CAST(timestamp AS TIMESTAMP) AS event_timestamp
    FROM events_staging
    WHERE user_id IS NOT NULL
),
user_agg AS (
    SELECT
        user_id,
        COUNT(*) AS total_events,
        MAX(event_timestamp) AS last_event_time,
        SUM(CASE WHEN event_type = 'view_product' THEN 1 ELSE 0 END) AS product_views,
        SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
        SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases
    FROM event_base
    GROUP BY user_id
)
SELECT
    user_id,
    total_events,
    last_event_time,
    CURRENT_DATE - CAST(last_event_time AS DATE) AS days_since_last_event,
    product_views,
    add_to_cart,
    purchases,
    COALESCE(add_to_cart::DOUBLE / NULLIF(product_views, 0), 0.0) AS view_to_cart_rate,
    COALESCE(purchases::DOUBLE / NULLIF(add_to_cart, 0), 0.0) AS cart_to_purchase_rate,
    (CURRENT_DATE - CAST(last_event_time AS DATE) <= 7) AS is_active_user,
    (add_to_cart >= 2 AND purchases = 0) AS is_high_intent,
    (CURRENT_DATE - CAST(last_event_time AS DATE) > 14) AS is_churn_risk
FROM user_agg;

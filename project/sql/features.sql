-- Build user-level lifecycle features from events_staging.

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
    DATE_DIFF('day', CAST(last_event_time AS DATE), CURRENT_DATE) AS days_since_last_event,
    product_views,
    add_to_cart,
    purchases,
    CASE
        WHEN product_views > 0 THEN add_to_cart::DOUBLE / product_views
        ELSE 0.0
    END AS view_to_cart_rate,
    CASE
        WHEN add_to_cart > 0 THEN purchases::DOUBLE / add_to_cart
        ELSE 0.0
    END AS cart_to_purchase_rate,
    CASE
        WHEN DATE_DIFF('day', CAST(last_event_time AS DATE), CURRENT_DATE) <= 7 THEN TRUE
        ELSE FALSE
    END AS is_active_user,
    CASE
        WHEN add_to_cart > 2 AND purchases = 0 THEN TRUE
        ELSE FALSE
    END AS is_high_intent,
    CASE
        WHEN DATE_DIFF('day', CAST(last_event_time AS DATE), CURRENT_DATE) > 14 THEN TRUE
        ELSE FALSE
    END AS is_churn_risk
FROM user_agg;

SELECT *
FROM user_features
ORDER BY total_events DESC, user_id
LIMIT 10;

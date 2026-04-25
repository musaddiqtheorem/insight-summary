-- Build user-level lifecycle intent scores and actions from user_features.

CREATE OR REPLACE TABLE user_scores AS
WITH stats AS (
    SELECT
        MAX(product_views) AS max_product_views,
        MAX(add_to_cart) AS max_add_to_cart
    FROM user_features
),
scored AS (
    SELECT
        uf.user_id,
        uf.total_events,
        uf.product_views,
        uf.add_to_cart,
        uf.purchases,
        uf.days_since_last_event,
        COALESCE(uf.product_views::DOUBLE / NULLIF(stats.max_product_views, 0), 0.0) AS normalized_views,
        COALESCE(uf.add_to_cart::DOUBLE / NULLIF(stats.max_add_to_cart, 0), 0.0) AS normalized_cart,
        1.0 / (1.0 + uf.days_since_last_event) AS recency_score
    FROM user_features AS uf
    CROSS JOIN stats
)
SELECT
    user_id,
    total_events,
    product_views,
    add_to_cart,
    purchases,
    days_since_last_event,
    normalized_views,
    normalized_cart,
    recency_score,
    (0.4 * normalized_views) + (0.4 * normalized_cart) + (0.2 * recency_score) AS intent_score,
    CASE
        WHEN purchases > 0 THEN 'customer'
        WHEN add_to_cart >= 2 THEN 'high_intent'
        WHEN product_views >= 3 THEN 'considering'
        WHEN days_since_last_event > 14 THEN 'churn_risk'
        ELSE 'new'
    END AS lifecycle_stage,
    CASE
        WHEN purchases > 0 THEN 'cross_sell'
        WHEN add_to_cart >= 2 THEN 'send_cart_reminder'
        WHEN product_views >= 3 THEN 'product_recommendation'
        WHEN days_since_last_event > 14 THEN 'winback_campaign'
        ELSE 'onboarding_flow'
    END AS recommended_action
FROM scored;

-- Build executable marketing actions from user_scores for simulation workflows.

CREATE OR REPLACE TABLE execution_plan AS
WITH planned_actions AS (
    SELECT
        user_id,
        lifecycle_stage,
        recommended_action AS action,
        CASE
            WHEN lifecycle_stage = 'customer' THEN 'sms'
            ELSE 'email'
        END AS channel,
        CASE
            WHEN intent_score > 0.7 THEN 'high'
            WHEN intent_score BETWEEN 0.4 AND 0.7 THEN 'medium'
            ELSE 'low'
        END AS priority,
        CASE
            WHEN lifecycle_stage = 'high_intent' THEN 'immediate'
            WHEN lifecycle_stage = 'churn_risk' THEN 'next_day'
            ELSE 'scheduled'
        END AS timing
    FROM user_scores
)
SELECT
    user_id,
    lifecycle_stage,
    action,
    channel,
    priority,
    timing,
    CURRENT_TIMESTAMP AS execution_time,
    'pending' AS status,
    CASE
        WHEN action = 'send_cart_reminder' THEN 'Send cart reminder email'
        WHEN action = 'winback_campaign' THEN 'Send winback campaign'
        WHEN action = 'cross_sell' THEN 'Send cross-sell message'
        WHEN action = 'product_recommendation' THEN 'Send product recommendations'
        ELSE 'Send onboarding message'
    END AS message_preview
FROM planned_actions;

-- Build executable marketing actions from user_scores.

CREATE OR REPLACE TABLE execution_plan AS
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
FROM user_scores;

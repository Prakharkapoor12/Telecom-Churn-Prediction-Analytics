-- ============================================================
-- Telecom Customer Churn — SQL Dashboard Queries
-- Database: data/database/telco_churn.db (SQLite)
-- Connect from Power BI: Get Data → SQLite → browse to .db file
-- All queries tested against the 7,043-row IBM Telco dataset
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- 1. EXECUTIVE SUMMARY
--    One-row KPI snapshot for the dashboard header
-- ────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                             AS total_customers,
    SUM(b.churn)                                         AS churned_customers,
    COUNT(*) - SUM(b.churn)                              AS retained_customers,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct,
    ROUND(SUM(b.monthly_charges), 2)                     AS total_monthly_revenue,
    ROUND(SUM(b.monthly_charges * b.churn), 2)           AS monthly_revenue_at_risk,
    ROUND(100.0 * SUM(b.monthly_charges * b.churn)
          / SUM(b.monthly_charges), 2)                   AS pct_revenue_at_risk,
    ROUND(AVG(b.monthly_charges), 2)                     AS avg_monthly_charges,
    ROUND(AVG(CASE WHEN b.churn = 1
                   THEN b.monthly_charges END), 2)       AS avg_charges_churned,
    ROUND(AVG(c.tenure_months), 1)                       AS avg_tenure_months
FROM billing b
JOIN customers c ON b.customer_id = c.customer_id;


-- ────────────────────────────────────────────────────────────
-- 2. CHURN RATE BY CONTRACT TYPE
--    The contract cliff: 43% vs 3% — headline finding
-- ────────────────────────────────────────────────────────────
SELECT
    b.contract_type,
    COUNT(*)                                             AS customers,
    SUM(b.churn)                                         AS churned,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct,
    ROUND(AVG(b.monthly_charges), 2)                     AS avg_monthly_charges,
    ROUND(SUM(b.monthly_charges * b.churn), 2)           AS lost_monthly_revenue,
    ROUND(100.0 * SUM(b.churn) / SUM(SUM(b.churn))
          OVER (), 2)                                    AS pct_of_total_churn
FROM billing b
GROUP BY b.contract_type
ORDER BY churn_rate_pct DESC;


-- ────────────────────────────────────────────────────────────
-- 3. CHURN BY TENURE PHASE
--    5-bucket lifecycle view; feeds the retention playbook
-- ────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN c.tenure_months <= 6  THEN '1 | First 6 months'
        WHEN c.tenure_months <= 12 THEN '2 | Months 7-12'
        WHEN c.tenure_months <= 24 THEN '3 | Year 2'
        WHEN c.tenure_months <= 48 THEN '4 | Years 3-4'
        ELSE                            '5 | 4+ years'
    END                                                  AS tenure_phase,
    COUNT(*)                                             AS customers,
    SUM(b.churn)                                         AS churned,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct,
    ROUND(AVG(b.monthly_charges), 2)                     AS avg_monthly_charges
FROM customers c
JOIN billing b ON c.customer_id = b.customer_id
GROUP BY tenure_phase
ORDER BY tenure_phase;


-- ────────────────────────────────────────────────────────────
-- 4. CHURN BY INTERNET SERVICE TYPE
--    Fiber optic: 42% churn at 2× price — value perception issue
-- ────────────────────────────────────────────────────────────
SELECT
    s.internet_service,
    COUNT(*)                                             AS customers,
    SUM(b.churn)                                         AS churned,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct,
    ROUND(AVG(b.monthly_charges), 2)                     AS avg_monthly_charges,
    ROUND(SUM(b.monthly_charges * b.churn), 2)           AS lost_monthly_revenue
FROM services s
JOIN billing b ON s.customer_id = b.customer_id
GROUP BY s.internet_service
ORDER BY churn_rate_pct DESC;


-- ────────────────────────────────────────────────────────────
-- 5. CHURN BY PAYMENT METHOD
--    Electronic check: 45% churn — the friction-tolerance signal
-- ────────────────────────────────────────────────────────────
SELECT
    b.payment_method,
    COUNT(*)                                             AS customers,
    SUM(b.churn)                                         AS churned,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct,
    ROUND(AVG(b.monthly_charges), 2)                     AS avg_monthly_charges,
    CASE
        WHEN b.payment_method LIKE '%automatic%' THEN 'Auto-pay'
        ELSE 'Manual'
    END                                                  AS payment_type
FROM billing b
GROUP BY b.payment_method
ORDER BY churn_rate_pct DESC;


-- ────────────────────────────────────────────────────────────
-- 6. SERVICE STACK EFFECT
--    Churn drops linearly with each add-on service
-- ────────────────────────────────────────────────────────────
SELECT
    (CASE WHEN s.online_security    = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN s.online_backup      = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN s.device_protection  = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN s.tech_support       = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN s.streaming_tv       = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN s.streaming_movies   = 'Yes' THEN 1 ELSE 0 END) AS num_addons,
    COUNT(*)                                             AS customers,
    SUM(b.churn)                                         AS churned,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct,
    ROUND(AVG(b.monthly_charges), 2)                     AS avg_monthly_charges
FROM services s
JOIN billing b ON s.customer_id = b.customer_id
GROUP BY num_addons
ORDER BY num_addons;


-- ────────────────────────────────────────────────────────────
-- 7. HIGH-VALUE CUSTOMER CHURN RISK
--    Top-quartile customers at risk — priority for retention team
-- ────────────────────────────────────────────────────────────
SELECT
    b.customer_id,
    b.contract_type,
    b.payment_method,
    b.monthly_charges,
    b.total_charges,
    c.tenure_months,
    s.internet_service,
    b.churn,
    CASE
        WHEN b.monthly_charges > 79.65 THEN 'High value'
        WHEN b.monthly_charges > 55.00 THEN 'Mid value'
        ELSE 'Low value'
    END                                                  AS value_tier
FROM billing b
JOIN customers c ON b.customer_id = c.customer_id
JOIN services  s ON b.customer_id = s.customer_id
WHERE b.monthly_charges > 79.65   -- top quartile
  AND b.churn = 0                  -- still retained (target for proactive outreach)
  AND b.contract_type = 'Month-to-month'  -- highest churn risk contract
ORDER BY b.monthly_charges DESC;


-- ────────────────────────────────────────────────────────────
-- 8. CONTRACT × TENURE HEATMAP DATA
--    Source for the cross-tab heatmap in Power BI
-- ────────────────────────────────────────────────────────────
SELECT
    b.contract_type,
    CASE
        WHEN c.tenure_months <= 12 THEN '0-12 months'
        WHEN c.tenure_months <= 24 THEN '13-24 months'
        WHEN c.tenure_months <= 48 THEN '25-48 months'
        ELSE                            '49+ months'
    END                                                  AS tenure_bucket,
    COUNT(*)                                             AS customers,
    SUM(b.churn)                                         AS churned,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct,
    ROUND(AVG(b.monthly_charges), 2)                     AS avg_monthly_charges
FROM billing b
JOIN customers c ON b.customer_id = c.customer_id
GROUP BY b.contract_type, tenure_bucket
ORDER BY b.contract_type, tenure_bucket;


-- ────────────────────────────────────────────────────────────
-- 9. DEMOGRAPHIC RISK PROFILE
--    Gender vs senior vs family status
-- ────────────────────────────────────────────────────────────
SELECT
    c.gender,
    CASE WHEN c.senior_citizen = 1 THEN 'Senior' ELSE 'Non-senior' END AS age_group,
    c.partner,
    c.dependents,
    COUNT(*)                                             AS customers,
    SUM(b.churn)                                         AS churned,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct
FROM customers c
JOIN billing b ON c.customer_id = b.customer_id
GROUP BY c.gender, age_group, c.partner, c.dependents
ORDER BY churn_rate_pct DESC;


-- ────────────────────────────────────────────────────────────
-- 10. MONTHLY CHARGE BUCKETS — PRICE SENSITIVITY
--     The $50 pain threshold: churn spikes above it
-- ────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN b.monthly_charges < 30  THEN '1. Under $30'
        WHEN b.monthly_charges < 50  THEN '2. $30-50'
        WHEN b.monthly_charges < 70  THEN '3. $50-70'
        WHEN b.monthly_charges < 90  THEN '4. $70-90'
        WHEN b.monthly_charges < 110 THEN '5. $90-110'
        ELSE                              '6. $110+'
    END                                                  AS charge_bucket,
    COUNT(*)                                             AS customers,
    SUM(b.churn)                                         AS churned,
    ROUND(100.0 * SUM(b.churn) / COUNT(*), 2)            AS churn_rate_pct,
    ROUND(AVG(b.monthly_charges), 2)                     AS avg_charges_in_bucket
FROM billing b
GROUP BY charge_bucket
ORDER BY charge_bucket;


-- ────────────────────────────────────────────────────────────
-- 11. RETENTION OPPORTUNITY SCORE
--     Ranks retained customers by estimated churn risk factors
--     Use this to prioritize proactive outreach
-- ────────────────────────────────────────────────────────────
SELECT
    b.customer_id,
    c.tenure_months,
    b.contract_type,
    b.payment_method,
    s.internet_service,
    b.monthly_charges,
    -- Heuristic risk score (mirrors NTB-02 feature engineering)
    ROUND(
        CASE WHEN b.contract_type = 'Month-to-month' THEN 0.35
             WHEN b.contract_type = 'One year'        THEN 0.10
             ELSE 0.0 END
        + CASE WHEN s.internet_service = 'Fiber optic' THEN 0.20
               WHEN s.internet_service = 'DSL'         THEN 0.05
               ELSE 0.0 END
        + CASE WHEN b.monthly_charges > 80 THEN 0.15
               WHEN b.monthly_charges > 60 THEN 0.07
               ELSE 0.0 END
        + CASE WHEN c.tenure_months <= 6  THEN 0.20
               WHEN c.tenure_months <= 12 THEN 0.12
               WHEN c.tenure_months <= 24 THEN 0.06
               ELSE 0.0 END
        + CASE WHEN b.payment_method = 'Electronic check' THEN 0.08
               ELSE 0.0 END,
    3)                                                   AS heuristic_risk_score,
    CASE
        WHEN b.monthly_charges > 79.65 THEN 'High'
        WHEN b.monthly_charges > 55.00 THEN 'Mid'
        ELSE 'Low'
    END                                                  AS value_tier
FROM billing b
JOIN customers c ON b.customer_id = c.customer_id
JOIN services  s ON b.customer_id = s.customer_id
WHERE b.churn = 0   -- retained customers only
ORDER BY heuristic_risk_score DESC, b.monthly_charges DESC
LIMIT 200;          -- top 200 for Power BI table visual


-- ────────────────────────────────────────────────────────────
-- 12. DATA QUALITY AUDIT
--     Quick checks for any downstream reporting
-- ────────────────────────────────────────────────────────────
SELECT
    'Row count'                      AS check_name,
    COUNT(*)                         AS result,
    '7043 expected'                  AS note
FROM billing
UNION ALL
SELECT 'Null total_charges',         SUM(CASE WHEN total_charges IS NULL THEN 1 ELSE 0 END), '11 expected (tenure=0)'
FROM billing
UNION ALL
SELECT 'Churn rate %',               ROUND(100.0 * SUM(churn) / COUNT(*), 2), '26.54 expected'
FROM billing
UNION ALL
SELECT 'Distinct contracts',         COUNT(DISTINCT contract_type), '3 expected'
FROM billing
UNION ALL
SELECT 'Distinct payment methods',   COUNT(DISTINCT payment_method), '4 expected'
FROM billing
UNION ALL
SELECT 'Customers in all 3 tables',
    (SELECT COUNT(*) FROM customers) -
    (SELECT COUNT(*) FROM billing),
    '0 expected (all joined)'
FROM billing
LIMIT 1;

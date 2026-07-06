-- =====================================================================
-- Olympic Data Analytics — Analytical queries
-- These power the Power BI visuals and can also be run directly
-- in Synapse Studio for ad-hoc analysis.
-- =====================================================================

-- 1. Top 10 countries by total medals
SELECT TOP 10 country, gold, silver, bronze, total_medals, medal_rank
FROM fact_medals
ORDER BY total_medals DESC;

-- 2. Gender participation ratio by discipline
SELECT
    discipline,
    male,
    female,
    total_participants,
    CAST(female AS FLOAT) / NULLIF(total_participants, 0) * 100 AS female_pct
FROM fact_gender_participation
ORDER BY female_pct DESC;

-- 3. Athlete count by country (top 15)
SELECT
    country,
    SUM(athlete_count) AS total_athletes
FROM fact_athlete_counts
GROUP BY country
ORDER BY total_athletes DESC
OFFSET 0 ROWS FETCH NEXT 15 ROWS ONLY;

-- 4. Discipline popularity (athlete count per discipline across all countries)
SELECT
    discipline,
    SUM(athlete_count) AS total_athletes
FROM fact_athlete_counts
GROUP BY discipline
ORDER BY total_athletes DESC;

-- 5. Average athlete age at the Games, by discipline
SELECT
    discipline,
    ROUND(AVG(CAST(age_at_games AS FLOAT)), 1) AS avg_age
FROM dim_athlete
GROUP BY discipline
ORDER BY avg_age DESC;

-- 6. Medal efficiency: medals per athlete sent, by country
SELECT
    m.country,
    m.total_medals,
    a.total_athletes,
    ROUND(CAST(m.total_medals AS FLOAT) / NULLIF(a.total_athletes, 0), 3) AS medals_per_athlete
FROM fact_medals m
JOIN (
    SELECT country, SUM(athlete_count) AS total_athletes
    FROM fact_athlete_counts
    GROUP BY country
) a ON m.country = a.country
ORDER BY medals_per_athlete DESC;

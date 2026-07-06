-- =====================================================================
-- Olympic Data Analytics — Azure Synapse Analytics
-- Table creation for the curated star schema (fact + dimension tables)
-- Run in a Synapse Serverless SQL Pool or Dedicated SQL Pool
-- =====================================================================

-- ---------------------------------------------------------------------
-- Dimension: Country
-- ---------------------------------------------------------------------
CREATE TABLE dim_country (
    country_code   VARCHAR(10)   NOT NULL,
    country        VARCHAR(100)  NOT NULL
);

-- ---------------------------------------------------------------------
-- Dimension: Discipline
-- ---------------------------------------------------------------------
CREATE TABLE dim_discipline (
    discipline_name VARCHAR(100) NOT NULL
);

-- ---------------------------------------------------------------------
-- Dimension: Athlete
-- ---------------------------------------------------------------------
CREATE TABLE dim_athlete (
    athlete_id    INT          NOT NULL,
    name          VARCHAR(150) NOT NULL,
    gender        VARCHAR(10),
    country_code  VARCHAR(10),
    discipline    VARCHAR(100),
    birth_year    INT,
    age_at_games  INT
);

-- ---------------------------------------------------------------------
-- Fact: Medal counts by country
-- ---------------------------------------------------------------------
CREATE TABLE fact_medals (
    country_code  VARCHAR(10),
    country       VARCHAR(100),
    gold          INT,
    silver        INT,
    bronze        INT,
    total_medals  INT,
    medal_rank    INT
);

-- ---------------------------------------------------------------------
-- Fact: Gender participation by discipline
-- ---------------------------------------------------------------------
CREATE TABLE fact_gender_participation (
    discipline         VARCHAR(100),
    male               INT,
    female             INT,
    total_participants INT
);

-- ---------------------------------------------------------------------
-- Fact: Athlete counts by country & discipline
-- ---------------------------------------------------------------------
CREATE TABLE fact_athlete_counts (
    country_code   VARCHAR(10),
    country        VARCHAR(100),
    discipline     VARCHAR(100),
    athlete_count  INT
);

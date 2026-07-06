# Power BI Dashboard — Build Guide

> Note: A `.pbix` file can't be generated outside of Power BI Desktop itself.
> This guide gives you the exact data source, DAX measures, and visual layout
> to rebuild the dashboard in a few minutes by connecting Power BI to your
> Synapse tables (or the CSVs directly, for local testing).

## 1. Connect Power BI to your data

**Option A — Connect to Synapse (production setup):**
`Get Data → Azure → Azure Synapse Analytics SQL` → enter your Synapse SQL endpoint →
select `dim_country`, `dim_athlete`, `fact_medals`, `fact_gender_participation`,
`fact_athlete_counts`.

**Option B — Connect to local CSVs (quick local testing):**
`Get Data → Text/CSV` → import the six files from `/data/` directly.

## 2. Model relationships

| From                       | To                | Cardinality |
|----------------------------|-------------------|-------------|
| fact_medals[country]       | dim_country[country] | Many-to-one |
| fact_athlete_counts[country_code] | dim_country[country_code] | Many-to-one |
| dim_athlete[country_code]  | dim_country[country_code] | Many-to-one |

## 3. DAX Measures

```dax
Total Medals = SUM(fact_medals[total_medals])

Total Gold = SUM(fact_medals[gold])

Total Athletes = SUM(fact_athlete_counts[athlete_count])

Female Participation % =
DIVIDE(
    SUM(fact_gender_participation[female]),
    SUM(fact_gender_participation[total_participants]),
    0
)

Medals per Athlete =
DIVIDE([Total Medals], [Total Athletes], 0)

Country Medal Rank =
RANKX(ALL(fact_medals[country]), [Total Medals], , DESC)
```

## 4. Suggested visuals / dashboard layout

**Page 1 — Medal Overview**
- KPI cards: Total Medals, Total Gold, Total Athletes
- Bar chart: Top 10 countries by Total Medals (color by Gold/Silver/Bronze, stacked)
- Map visual: medal count by country (bubble size = total medals)
- Table: Country | Gold | Silver | Bronze | Total | Rank

**Page 2 — Participation & Demographics**
- Donut chart: overall Male vs Female participation
- Bar chart: Female Participation % by discipline (sorted descending)
- Line/column chart: Average athlete age by discipline
- Slicer: Discipline, Country

**Page 3 — Country Deep Dive**
- Slicer: Country (single-select)
- Card: Total Medals, Total Athletes, Medals per Athlete for selected country
- Bar chart: Athlete count by discipline for selected country
- Table: Athlete list (name, discipline, gender, age) for selected country

## 5. Formatting notes
- Use a consistent Olympic-inspired palette (blue, yellow, black, green, red accents) sparingly for medal colors (gold/silver/bronze as actual gold/silver/bronze hex codes).
- Add a title header and a "last refreshed" text box driven by a `Data Refresh Date` measure if scheduling refresh from Synapse.

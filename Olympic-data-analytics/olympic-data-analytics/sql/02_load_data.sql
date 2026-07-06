-- =====================================================================
-- Olympic Data Analytics — Load curated CSVs into Synapse tables
-- Files are the ones exported by the Databricks notebook
-- (01_transform_olympic_data.py, Step 5) to Blob/ADLS storage.
-- Replace <storage_account>, <container>, and credential name as needed.
-- =====================================================================

COPY INTO dim_country
FROM 'https://<storage_account>.blob.core.windows.net/<container>/curated/csv/dim_country/'
WITH (
    FILE_TYPE = 'CSV',
    FIRSTROW = 2,
    CREDENTIAL = (IDENTITY = 'Shared Access Signature', SECRET = '<sas_token>')
);

COPY INTO dim_discipline
FROM 'https://<storage_account>.blob.core.windows.net/<container>/curated/csv/dim_discipline/'
WITH (
    FILE_TYPE = 'CSV',
    FIRSTROW = 2,
    CREDENTIAL = (IDENTITY = 'Shared Access Signature', SECRET = '<sas_token>')
);

COPY INTO dim_athlete
FROM 'https://<storage_account>.blob.core.windows.net/<container>/curated/csv/dim_athlete/'
WITH (
    FILE_TYPE = 'CSV',
    FIRSTROW = 2,
    CREDENTIAL = (IDENTITY = 'Shared Access Signature', SECRET = '<sas_token>')
);

COPY INTO fact_medals
FROM 'https://<storage_account>.blob.core.windows.net/<container>/curated/csv/fact_medals/'
WITH (
    FILE_TYPE = 'CSV',
    FIRSTROW = 2,
    CREDENTIAL = (IDENTITY = 'Shared Access Signature', SECRET = '<sas_token>')
);

COPY INTO fact_gender_participation
FROM 'https://<storage_account>.blob.core.windows.net/<container>/curated/csv/fact_gender_participation/'
WITH (
    FILE_TYPE = 'CSV',
    FIRSTROW = 2,
    CREDENTIAL = (IDENTITY = 'Shared Access Signature', SECRET = '<sas_token>')
);

COPY INTO fact_athlete_counts
FROM 'https://<storage_account>.blob.core.windows.net/<container>/curated/csv/fact_athlete_counts/'
WITH (
    FILE_TYPE = 'CSV',
    FIRSTROW = 2,
    CREDENTIAL = (IDENTITY = 'Shared Access Signature', SECRET = '<sas_token>')
);

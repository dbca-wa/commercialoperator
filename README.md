# COLS Reporting Export DB
copies cols tables into a seperate database for reporting purposes.


# Create COLS_Reporting Database and Roles
```
psql "host=<hostname.domain> port=5432 dbname=postgres user=postgres password=<passwd> sslmode=require"


ledger_prod=> create database cols_reporting;
CREATE DATABASE
ledger_prod=> CREATE ROLE cols_rw WITH PASSWORD 'abc123';
CREATE ROLE
ledger_prod=> CREATE ROLE cols_ro WITH PASSWORD 'def123';
CREATE ROLE
ledger_prod=> 

ledger_prod=> ALTER ROLE cols_rw LOGIN;
ALTER ROLE
ledger_prod=> ALTER ROLE cols_ro LOGIN;
ALTER ROLE

ledger_prod=> GRANT ALL PRIVILEGES ON DATABASE cols_reporting to cols_rw;
GRANT
ledger_prod=> GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO cols_rw;
GRANT
ledger_prod=> GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cols_rw;

ledger_prod=> GRANT CONNECT ON DATABASE cols_reporting TO cols_ro;
GRANT
ledger_prod=> GRANT USAGE ON SCHEMA public TO cols_ro;
GRANT
ledger_prod=> GRANT SELECT ON ALL TABLES IN SCHEMA public TO cols_ro;
GRANT
ledger_prod=> GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO cols_ro;
GRANT
ledger_prod=> ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO cols_ro

# Confirm
psql "host=hostname.domain port=5432 dbname=cols_reporting user=cols_ro password=def123 sslmode=require
```

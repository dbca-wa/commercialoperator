# Database setup steps for COLS segregation work

## Download ledger prod dump without reversion tables from https://ledger-daily-db-oim01.dbca.wa.gov.au/

E.g.: ledger_prod_no_reversion.sql

## Import dump into "helper" database "ledger_prod"

`psql ledger_prod < ledger_prod_no_reversion.sql`

## Export only tables relevant to the cols app into a file, e.g. ledger_prod.sql

`pg_dump -U your_username -h your_hostname -W -t "auth_*" -t "commercialoperator_*" -t "django_*" ledger_prod > ../webdav/data/sql/ledger_prod_reduced/ledger_prod.sql`
or (chose one)
`pg_dump --column-inserts -t "auth_*" -t "commercialoperator_*" -t "django_*" -f ../webdav/data/sql/ledger_prod_reduced/ledger_prod.sql ledger_prod`

`auth_`, `django_`, and `commercialoperator_` are the tables I went with. `auth_` might not be needed, but I wasn't sure at that time.

## Postgres commands

### Connect to pg (psql) and create a segregation database, e.g. commercialoperator_segregation

`CREATE DATABASE commercialoperator_segregation;`

### Connect to the newly created database and activate the Postgis extension

`CREATE EXTENSION postgis;`

## Import the exported tables into the new ledger-less cols database from command line

`psql commercialoperator_segregation < ../webdav/data/sql/ledger_prod_reduced/ledger_prod.sql`

That is the database to work with from now on.

## Change what DATABASE_URL points to in env file

`DATABASE_URL=postgis://commercialoperator_dev:commercialoperator_dev@172.17.0.1:15432/commercialoperator_segregation`

## Possibly have to change tables ownership from e.g. postgres to database user, e.g. commercialoperator_dev, from command line

`for table in ``psql -tc "select tablename from pg_tables where schemaname = 'public';" commercialoperator_segregation`` ; do  psql -c "alter table public.${table} owner to commercialoperator_dev" commercialoperator_segregation ; done`


## Patch commercialoperator, admin and reversion migration files

### patch_admin_0001_initial.patch

`patch .venv/lib/python3.12/site-packages/django/contrib/admin/migrations/0001_initial.py patch_admin_0001_initial.patch`

### patch_reversion_0001.patch

`patch .venv/lib/python3.12/site-packages/reversion/migrations/0001_squashed_0004_auto_20160611_1202.py patch_reversion_0001.patch`

### Patch commercialoperator migration files

`git apply patch_migrations.patch`

## Run migrations in order

Some of these migrations might need to be faked

```
./manage.py migrate auth
./manage.py migrate [--fake] taggit
./manage.py migrate ledger_api_client
./manage.py migrate admin
./manage.py migrate [--fake] django_cron
./manage.py migrate [--fake] reversion
[./manage.py migrate sites]
[./manage.py migrate sessions]
```

## Reverse the patches

`git apply --reverse patch_migrations.patch`
`patch -R .venv/lib/python3.12/site-packages/reversion/migrations/0001_squashed_0004_auto_20160611_1202.py patch_reversion_0001.patch`
`patch -R .venv/lib/python3.12/site-packages/django/contrib/admin/migrations/0001_initial.py patch_admin_0001_initial.patch`

## Run cols patches starting with 131

`./manage.py migrate commercialoperator 0131_ledger_segregation_principal_changes`

## Done

:>

## Error handling

This is here to record ways I tried to resolve database related errors that came up during the segregation.
None of these errors may pop up when segregating the production app, this is purely for documentation and can otherwise be ignored.

### InconsistentMigrationHistory: Migration admin.0001_initial is applied before its dependency ledger_api_client.0001_initial

dbshell:

`SELECT * FROM django_migrations WHERE app='admin';`
id | app | name | applied
----+-------+-------------------------------+-------------------------------
12 | admin | 0001_initial | 2016-07-14 10:45:33.982686+08
13 | admin | 0002_logentry_remove_auto_add | 2016-07-14 10:45:34.034208+08

`DELETE FROM django_migrations WHERE id IN (12,13);`

### InconsistentMigrationHistory: Migration reversion.0001_squashed_0004_auto_20160611_1202 is applied before its dependency ledger_api_client.0001_initial

dbshell:

`SELECT * FROM django_migrations WHERE app='reversion';`
id | app | name | applied
-----+-----------+---------------------------------------+-------------------------------
55 | reversion | 0001_initial | 2016-07-14 10:45:55.947883+08
56 | reversion | 0002_auto_20141216_1509 | 2016-07-14 10:45:56.183265+08
275 | reversion | 0003_auto_20160601_1600 | 2018-09-25 14:57:41.26811+08
276 | reversion | 0004_auto_20160611_1202 | 2018-09-25 14:57:46.121174+08
277 | reversion | 0001_squashed_0004_auto_20160611_1202 | 2018-09-25 14:57:46.163337+08

`DELETE FROM django_migrations WHERE id IN (55,56,275,276,277);`

dbshell:

### Taggit related migration error

`SELECT * FROM django_migrations WHERE app='taggit';`
id | app | name | applied
-----+--------+-------------------------+-------------------------------
183 | taggit | 0001_initial | 2017-01-12 10:16:37.388795+08
184 | taggit | 0002_auto_20150616_2121 | 2017-01-12 10:16:37.596073+08

`DELETE FROM django_migrations WHERE id IN (183,184);`


## Setting up reversion_revision and reversion_version tables

Not sure on this one, kind of took a shortcut by copy pasting the reversion schema from another database,
thus bypassing running the migrations?

Issue:
Executing: ./manage_co.py migrate reversion
Results in: django.db.utils.ProgrammingError: relation "reversion_version" does not exist

What I did instead:
Dump both tables from an existing other db with reversion into files and set ownership to postgres:
`pg_dump leaseslicensing_dev -t reversion_revision --schema-only > reversion_revision.sql`
`pg_dump leaseslicensing_dev -t reversion_version --schema-only > reversion_version.sql`

Import from within postgres:
`\c commercialoperator_segregation`
`\i reversion_revision.sql`
`\i reversion_version.sql`

## ValueError: The field commercialoperator.Organisation.organisation was declared with a lazy reference to 'accounts.organisation', but app 'accounts' isn't installed.

@0001_initial.py:

```
@@ -1336,7 +1336,8 @@ class Migration(migrations.Migration):
         migrations.AddField(
             model_name='organisation',
             name='organisation',
-            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Organisation'),
+            # field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Organisation'),
+            field=models.IntegerField(unique=True, verbose_name='Ledger Organisation ID'),
```

@commercialoperator/components/organisations/models.py:

```
@@ -33,7 +33,10 @@ from commercialoperator.components.organisations.emails import (


 class Organisation(models.Model):
-    organisation = models.ForeignKey(ledger_organisation, on_delete=models.PROTECT)
+    # organisation = models.ForeignKey(ledger_organisation, on_delete=models.PROTECT)
+    organisation = models.IntegerField(
+        unique=True, verbose_name="Ledger Organisation ID"
+    )
```

## Change (the now integer) field name organisation to organisation_id to be in line with the database

@0001_initial.py:

```
@@ -1335,7 +1335,7 @@ class Migration(migrations.Migration):
         ),
         migrations.AddField(
             model_name='organisation',
-            name='organisation',
+            name='organisation_id',
```

@commercialoperator/components/organisations/models.py:

```
@@ -34,7 +34,7 @@ from commercialoperator.components.organisations.emails import (

 class Organisation(models.Model):
     # organisation = models.ForeignKey(ledger_organisation, on_delete=models.PROTECT)
-    organisation = models.IntegerField(
+    organisation_id = models.IntegerField(
```

## Reversion index already exists

Issue: django.db.utils.ProgrammingError: relation "reversion_v_content_f95daf_idx" already exists
Solution: Run:
`DROP INDEX reversion_v_content_f95daf_idx;`
then: `./manage_co.py migrate reversion`

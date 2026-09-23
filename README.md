[![Build
status](https://travis-ci.org/dbca-wa/commercialoperator.svg?branch=master)](https://travis-ci.org/dbca-wa/commercialoperator/builds) [![Coverage Status](https://coveralls.io/repos/github/dbca-wa/commercialoperator/badge.svg?branch=master)](https://coveralls.io/github/dbca-wa/commercialoperator?branch=master)

# Commercial Operator Licensing System

The Commercial Operator Licensing System (COLS) is used by customers applying for a licence to deliver tourist and educational services for a profit while on land managed by the Department and to pay for the access fees to access these lands. The system is used by Department staff to process the licence applications and to manage issued licences.

It is a database-backed Django application, using REST API with Vue.js as the client side app and integrates into the ledger system.

# Requirements

- Python (>=3.12, <4.0)
- PostgreSQL (>=12.20)

## Prerequisites: Installing Poetry

To avoid conflicts with your project or system Python packages, install Poetry in its own isolated environment using the official installer.

### 1. Install Poetry

Run the official installation script:

```bash
curl -sSL https://install.python-poetry.org | python3 -

### 2. Add Poetry to your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

### 3. Verify Installation
which poetry
# Expected output: /home/container/.local/bin/poetry

poetry --version

```

Poetry Basics (for more see: https://python-poetry.org/docs/)

- Manage the package versions in pyproject.toml rather than requirements.txt

- Use `poetry install` for an inital install into your active project virtualenv

- Use `poetry update` to easily pull in minor and patch releases

- Keep the poetry.lock file commited to version control

- To generate a frozen requirements file:

`poetry export -f requirements.txt --output requirements.txt --without-hashes`

This requirements file is then deterministic rather than being able to change if a hotfix is made and the container is rebuilt.

# Environment settings

A `.env` file should be created in the project root and used to set
required environment variables at run time. Example content:

    DEBUG=True
    SECRET_KEY='thisismysecret'
    DATABASE_URL='postgis://user:pw@localhost:port/db_name'
    EMAIL_HOST='SMTP_HOST'
    BPOINT_USERNAME='BPOINT_USER'
    BPOINT_PASSWORD='BPOINT_PW
    BPOINT_BILLER_CODE='1234567'
    BPOINT_MERCHANT_NUM='BPOINT_MERCHANT_NUM'
    BPAY_BILLER_CODE='987654'
    CMS_URL="CMS_URL"
    LEDGER_USER="LEDGER_USER"
    LEDGER_PASS="LEDGER_PASS"
    OSCAR_SHOP_NAME='SHOP_NAME'
    DEFAULT_COLS_EMAIL='DEFAULT_EMAIL_ADDRESS'
    DEFAULT_FROM_EMAIL='FROM_EMAIL_ADDRESS'
    NOTIFICATION_EMAIL='NOTIF_RECIPIENT_1, NOTIF_RECIPIENT_2'
    NON_PROD_EMAIL='NON_PROD_RECIPIENT_1, NON_PROD_RECIPIENT_2'
    EMAIL_INSTANCE='DEV'
    PRODUCTION_EMAIL=False
    BPAY_ALLOWED=False
    SITE_PREFIX='cols-dev'
    SITE_DOMAIN='SITE_DOMAIN'
    PS_PAYMENT_SYSTEM_ID='S123'
    DEV_APP_BUILD_URL="http://10.17.0.10:9107/static/commercialoperator_vue/js/app.js"
    ENABLE_DJANGO_LOGIN=True

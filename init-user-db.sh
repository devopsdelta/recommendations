#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER recommendations;
    CREATE DATABASE recommendations;
    GRANT ALL PRIVILEGES ON DATABASE recommendations TO recommendations;
EOSQL

# psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
#     CREATE USER recommendations_test;
#     CREATE DATABASE recommendations_test;
#     GRANT ALL PRIVILEGES ON DATABASE recommendations_test TO recommendations_test;
# EOSQL

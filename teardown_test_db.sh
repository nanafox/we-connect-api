#!/bin/bash

# Define variables for the user and database
source .env

# Terminate all connections to the database
psql -U postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '${DB_NAME}_test' AND pid <> pg_backend_pid();"

# Revoke privileges and reassign ownership of dependent objects
psql -U postgres -c "REVOKE ALL PRIVILEGES ON DATABASE ${DB_NAME}_test FROM $DB_USER;"

# Drop the database
psql -U postgres -c "DROP DATABASE IF EXISTS ${DB_NAME}_test;"

# Drop the user
psql -U postgres -c "DROP USER IF EXISTS $DB_USER;"

echo "User $DB_USER and Database ${DB_NAME}_test have been removed."

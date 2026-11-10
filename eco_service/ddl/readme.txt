sudo -u postgres bash -c '
pg_dump -d auroville_eco_service -n dicts --schema-only --clean --if-exists -f /tmp/01_dicts.sql
pg_dump -d auroville_eco_service -n infrastructure --schema-only --clean --if-exists -f /tmp/02_infrastructure.sql
pg_dump -d auroville_eco_service -n security --schema-only --clean --if-exists -f /tmp/03_security.sql
pg_dump -d auroville_eco_service -n analytics --schema-only --clean --if-exists -f /tmp/04_analytics.sql
pg_dump -d auroville_eco_service --schema-only --no-owner --no-privileges --clean --if-exists -f /tmp/full_schema_auroville_eco_service.sql
' && sudo cp /tmp/01_dicts.sql /tmp/02_infrastructure.sql /tmp/03_security.sql /tmp/04_analytics.sql /tmp/full_schema_auroville_eco_service.sql ~/Projects/eco_service/ddl/ && sudo chown $USER:$USER ~/Projects/eco_service/ddl/*.sql && ls -lh ~/Projects/eco_service/ddl/ && wc -l ~/Projects/eco_service/ddl/*.sql
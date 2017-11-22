FROM postgres:9.4
COPY init-user-db.sh /docker-entrypoint-initdb.d/

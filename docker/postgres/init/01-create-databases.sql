\getenv dev_user DEV_DB_USER
\getenv dev_password DEV_DB_PASSWORD
\getenv dev_database DEV_DB_NAME

\getenv test_user TEST_DB_USER
\getenv test_password TEST_DB_PASSWORD
\getenv test_database TEST_DB_NAME

\getenv prod_user PROD_DB_USER
\getenv prod_password PROD_DB_PASSWORD
\getenv prod_database PROD_DB_NAME

CREATE ROLE :"dev_user" LOGIN PASSWORD :'dev_password';
CREATE DATABASE :"dev_database" OWNER :"dev_user";

CREATE ROLE :"test_user" LOGIN PASSWORD :'test_password';
CREATE DATABASE :"test_database" OWNER :"test_user";

CREATE ROLE :"prod_user" LOGIN PASSWORD :'prod_password';
CREATE DATABASE :"prod_database" OWNER :"prod_user";
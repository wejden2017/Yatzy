-- =============================================================================
-- CRÉATION DU RÔLE {{ lookup('env', 'ENV') | upper }}_ROLE
-- Environnement: {{ lookup('env', 'ENV') | upper }}
-- Stratégie: DROP + CREATE (idempotent)
-- =============================================================================

SET SERVEROUTPUT ON SIZE UNLIMITED
SET HEADING OFF
SET FEEDBACK OFF
SET PAGES 0
SET VERIFY OFF
SET ECHO OFF

WHENEVER SQLERROR EXIT 1

-- =============================================================================
-- DROP + CREATE DU RÔLE
-- =============================================================================

DECLARE
    v_count NUMBER;
    v_role_name VARCHAR2(128) := '{{ lookup('env', 'ENV') | upper }}_ROLE';
BEGIN
    -- Vérifier si le rôle existe
    SELECT COUNT(*) INTO v_count
    FROM dba_roles
    WHERE role = v_role_name;
    
    -- Si le rôle existe, le dropper
    IF v_count > 0 THEN
        DBMS_OUTPUT.PUT_LINE('[DROP] Role ' || v_role_name || ' existe, suppression...');
        EXECUTE IMMEDIATE 'DROP ROLE ' || v_role_name;
        DBMS_OUTPUT.PUT_LINE('[DROP] Role ' || v_role_name || ' supprime');
    ELSE
        DBMS_OUTPUT.PUT_LINE('[INFO] Role ' || v_role_name || ' n''existe pas');
    END IF;
    
    -- Créer le rôle (toujours)
    DBMS_OUTPUT.PUT_LINE('[CREATE] Creation du role ' || v_role_name || '...');
    EXECUTE IMMEDIATE 'CREATE ROLE ' || v_role_name;
    DBMS_OUTPUT.PUT_LINE('[SUCCESS] Role ' || v_role_name || ' cree');
    
END;
/

-- =============================================================================
-- PRIVILÈGES DE BASE
-- =============================================================================

GRANT CREATE SESSION TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CONNECT TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT RESOURCE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE TABLE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE VIEW TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE PROCEDURE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE SEQUENCE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE SYNONYM TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE TRIGGER TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE TYPE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE MATERIALIZED VIEW TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT CREATE DATABASE LINK TO {{ lookup('env', 'ENV') | upper }}_ROLE;

{% if lookup('env', 'ENV') | upper in ['DEV', 'QA'] %}
-- =============================================================================
-- PRIVILÈGES DDL (DEV et QA uniquement)
-- =============================================================================

GRANT ALTER ANY TABLE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT DROP ANY TABLE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT ALTER ANY PROCEDURE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT DROP ANY PROCEDURE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT ALTER ANY SEQUENCE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT DROP ANY SEQUENCE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT DROP ANY VIEW TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT DROP ANY TYPE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT DROP ANY MATERIALIZED VIEW TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT DROP ANY TRIGGER TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT TRUNCATE ANY TABLE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
{% endif %}

-- =============================================================================
-- PRIVILÈGES DE CONSULTATION
-- =============================================================================

GRANT SELECT_CATALOG_ROLE TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT SELECT ANY DICTIONARY TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT ANALYZE ANY TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT SELECT ON V_$SESSION TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT SELECT ON V_$SQL TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT SELECT ON V_$SQL_PLAN TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT SELECT ON V_$SQLAREA TO {{ lookup('env', 'ENV') | upper }}_ROLE;
GRANT SELECT ON V_$PARAMETER TO {{ lookup('env', 'ENV') | upper }}_ROLE;

PROMPT [SUCCESS] Role {{ lookup('env', 'ENV') | upper }}_ROLE configure avec tous les privileges

COMMIT;
/

EXIT 0;

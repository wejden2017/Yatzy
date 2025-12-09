-- =============================================================================
-- PROCÉDURE CENTRALISÉE DE GRANT DANS SYS
-- Rôle: {{ lookup('env', 'ENV') | upper }}_ROLE
-- Environnement: {{ lookup('env', 'ENV') | upper }}
-- =============================================================================
-- Cette procédure unique gère les grants pour N'IMPORTE QUEL schéma
-- Utilisation: EXEC SYS.GRANT_ROLE_ACCESS_TO_SCHEMA('LUCA', 'QA_ROLE')
-- =============================================================================

SET SERVEROUTPUT ON SIZE UNLIMITED
SET HEADING OFF
SET FEEDBACK OFF
SET PAGES 0
SET VERIFY OFF
SET ECHO OFF

WHENEVER SQLERROR EXIT 1

-- =============================================================================
-- DROP DE LA PROCÉDURE SI ELLE EXISTE
-- =============================================================================

DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM dba_objects
    WHERE owner = 'SYS'
      AND object_name = 'GRANT_ROLE_ACCESS_TO_SCHEMA'
      AND object_type = 'PROCEDURE';
    
    IF v_count > 0 THEN
        DBMS_OUTPUT.PUT_LINE('[DROP] Procedure SYS.GRANT_ROLE_ACCESS_TO_SCHEMA existe, suppression...');
        EXECUTE IMMEDIATE 'DROP PROCEDURE SYS.GRANT_ROLE_ACCESS_TO_SCHEMA';
        DBMS_OUTPUT.PUT_LINE('[DROP] Procedure supprimee');
    ELSE
        DBMS_OUTPUT.PUT_LINE('[INFO] Procedure SYS.GRANT_ROLE_ACCESS_TO_SCHEMA n''existe pas');
    END IF;
END;
/

-- =============================================================================
-- CRÉATION DE LA PROCÉDURE
-- =============================================================================

PROMPT [CREATE] Creation de la procedure SYS.GRANT_ROLE_ACCESS_TO_SCHEMA...

CREATE OR REPLACE PROCEDURE SYS.GRANT_ROLE_ACCESS_TO_SCHEMA(
    p_schema_name IN VARCHAR2,
    p_role_name   IN VARCHAR2
)
AUTHID DEFINER
AS
    v_sql VARCHAR2(4000);
    v_count NUMBER;
    v_objects_count NUMBER := 0;
BEGIN
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('Schema: ' || p_schema_name);
    DBMS_OUTPUT.PUT_LINE('Role: ' || p_role_name);
    DBMS_OUTPUT.PUT_LINE('========================================');
    
    -- Vérifier que le schéma existe
    SELECT COUNT(*) INTO v_count
    FROM dba_users
    WHERE username = UPPER(p_schema_name);
    
    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Schema ' || p_schema_name || ' n''existe pas');
    END IF;
    
    -- Vérifier que le rôle existe
    SELECT COUNT(*) INTO v_count
    FROM dba_roles
    WHERE role = UPPER(p_role_name);
    
    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Role ' || p_role_name || ' n''existe pas');
    END IF;
    
    -- ==========================================================================
    -- TABLES
    -- ==========================================================================
    DBMS_OUTPUT.PUT_LINE('[TABLES]');
    FOR rec IN (
        SELECT table_name 
        FROM dba_tables 
        WHERE owner = UPPER(p_schema_name)
        ORDER BY table_name
    ) LOOP
        BEGIN
            {% if lookup('env', 'ENV') | upper in ['DEV', 'QA'] %}
            v_sql := 'GRANT ALL PRIVILEGES ON ' || p_schema_name || '.' || rec.table_name || ' TO ' || p_role_name;
            {% else %}
            v_sql := 'GRANT SELECT ON ' || p_schema_name || '.' || rec.table_name || ' TO ' || p_role_name;
            {% endif %}
            EXECUTE IMMEDIATE v_sql;
            v_objects_count := v_objects_count + 1;
            DBMS_OUTPUT.PUT_LINE('  [OK] ' || rec.table_name);
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('  [ERR] ' || rec.table_name || ': ' || SQLERRM);
        END;
    END LOOP;
    
    -- ==========================================================================
    -- VUES
    -- ==========================================================================
    DBMS_OUTPUT.PUT_LINE('[VUES]');
    FOR rec IN (
        SELECT view_name 
        FROM dba_views 
        WHERE owner = UPPER(p_schema_name)
        ORDER BY view_name
    ) LOOP
        BEGIN
            v_sql := 'GRANT SELECT ON ' || p_schema_name || '.' || rec.view_name || ' TO ' || p_role_name;
            EXECUTE IMMEDIATE v_sql;
            v_objects_count := v_objects_count + 1;
            DBMS_OUTPUT.PUT_LINE('  [OK] ' || rec.view_name);
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('  [ERR] ' || rec.view_name || ': ' || SQLERRM);
        END;
    END LOOP;
    
    -- ==========================================================================
    -- SEQUENCES
    -- ==========================================================================
    DBMS_OUTPUT.PUT_LINE('[SEQUENCES]');
    FOR rec IN (
        SELECT sequence_name 
        FROM dba_sequences 
        WHERE sequence_owner = UPPER(p_schema_name)
        ORDER BY sequence_name
    ) LOOP
        BEGIN
            {% if lookup('env', 'ENV') | upper in ['DEV', 'QA'] %}
            v_sql := 'GRANT SELECT, ALTER ON ' || p_schema_name || '.' || rec.sequence_name || ' TO ' || p_role_name;
            {% else %}
            v_sql := 'GRANT SELECT ON ' || p_schema_name || '.' || rec.sequence_name || ' TO ' || p_role_name;
            {% endif %}
            EXECUTE IMMEDIATE v_sql;
            v_objects_count := v_objects_count + 1;
            DBMS_OUTPUT.PUT_LINE('  [OK] ' || rec.sequence_name);
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('  [ERR] ' || rec.sequence_name || ': ' || SQLERRM);
        END;
    END LOOP;
    
    {% if lookup('env', 'ENV') | upper in ['DEV', 'QA'] %}
    -- ==========================================================================
    -- PROCEDURES/FUNCTIONS/PACKAGES/TYPES (DEV et QA uniquement)
    -- ==========================================================================
    DBMS_OUTPUT.PUT_LINE('[PROCEDURES/FUNCTIONS/PACKAGES/TYPES]');
    FOR rec IN (
        SELECT object_name, object_type 
        FROM dba_objects
        WHERE owner = UPPER(p_schema_name)
          AND object_type IN ('PROCEDURE', 'FUNCTION', 'PACKAGE', 'TYPE')
        ORDER BY object_type, object_name
    ) LOOP
        BEGIN
            v_sql := 'GRANT EXECUTE ON ' || p_schema_name || '.' || rec.object_name || ' TO ' || p_role_name;
            EXECUTE IMMEDIATE v_sql;
            v_objects_count := v_objects_count + 1;
            DBMS_OUTPUT.PUT_LINE('  [OK] ' || rec.object_type || ' ' || rec.object_name);
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('  [ERR] ' || rec.object_type || ' ' || rec.object_name || ': ' || SQLERRM);
        END;
    END LOOP;
    {% endif %}
    
    -- ==========================================================================
    -- MATERIALIZED VIEWS
    -- ==========================================================================
    DBMS_OUTPUT.PUT_LINE('[MATERIALIZED VIEWS]');
    FOR rec IN (
        SELECT mview_name 
        FROM dba_mviews 
        WHERE owner = UPPER(p_schema_name)
        ORDER BY mview_name
    ) LOOP
        BEGIN
            v_sql := 'GRANT SELECT ON ' || p_schema_name || '.' || rec.mview_name || ' TO ' || p_role_name;
            EXECUTE IMMEDIATE v_sql;
            v_objects_count := v_objects_count + 1;
            DBMS_OUTPUT.PUT_LINE('  [OK] ' || rec.mview_name);
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('  [ERR] ' || rec.mview_name || ': ' || SQLERRM);
        END;
    END LOOP;
    
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('[SUCCESS] ' || v_objects_count || ' objets traites sur schema ' || p_schema_name);
    DBMS_OUTPUT.PUT_LINE('========================================');
    
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[ERROR] ' || SQLERRM);
        RAISE;
END GRANT_ROLE_ACCESS_TO_SCHEMA;
/

-- Donner EXECUTE à PUBLIC pour que tous les schémas puissent l'utiliser
GRANT EXECUTE ON SYS.GRANT_ROLE_ACCESS_TO_SCHEMA TO PUBLIC;

PROMPT [SUCCESS] Procedure SYS.GRANT_ROLE_ACCESS_TO_SCHEMA creee et EXECUTE accorde a PUBLIC

COMMIT;
/

EXIT 0;

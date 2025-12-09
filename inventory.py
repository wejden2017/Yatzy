-- =============================================================================
-- TRIGGER DE SÉCURITÉ SYSTÈME - Protection des schémas système
-- Environnement: {{ lookup('env', 'ENV') | upper }}
-- =============================================================================
-- Ce trigger protège TOUTE LA BASE contre les opérations DDL sur schémas système
-- Créé dans SYS, s'applique à toute la base (ON DATABASE)
-- =============================================================================

SET SERVEROUTPUT ON SIZE UNLIMITED
SET HEADING OFF
SET FEEDBACK OFF
SET PAGES 0
SET VERIFY OFF
SET ECHO OFF
SET TERMOUT ON

WHENEVER SQLERROR EXIT 1
WHENEVER OSERROR EXIT 1

-- =============================================================================
-- NETTOYAGE DES ANCIENS TRIGGERS
-- =============================================================================

PROMPT [INFO] Nettoyage des anciens triggers...

DECLARE
    v_count NUMBER;
    TYPE t_triggers IS TABLE OF VARCHAR2(128);
    v_old_triggers t_triggers := t_triggers(
        'TRG_SECURITY_SCHEMA_ACCESS',
        'TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS',
        'TRG_BLOCK_DDL_SYSTEM_ONLY',
        'TRG_BLOCK_DROP_EXCEPT_LUCA'
    );
BEGIN
    FOR i IN 1..v_old_triggers.COUNT LOOP
        BEGIN
            SELECT COUNT(*) INTO v_count
            FROM dba_triggers
            WHERE owner = 'SYS'
              AND trigger_name = v_old_triggers(i);
            
            IF v_count > 0 THEN
                EXECUTE IMMEDIATE 'DROP TRIGGER SYS.' || v_old_triggers(i);
                DBMS_OUTPUT.PUT_LINE('[DROP] ' || v_old_triggers(i) || ' supprime');
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('[WARN] ' || v_old_triggers(i) || ': ' || SQLERRM);
        END;
    END LOOP;
END;
/

-- =============================================================================
-- CRÉATION DU TRIGGER DE SÉCURITÉ
-- =============================================================================

PROMPT [INFO] Creation du trigger TRG_BLOCK_DDL_SYSTEM_ONLY...

CREATE OR REPLACE TRIGGER SYS.TRG_BLOCK_DDL_SYSTEM_ONLY
BEFORE DROP OR ALTER OR TRUNCATE ON DATABASE
DECLARE
    v_schema   VARCHAR2(128);
    v_username VARCHAR2(128);
BEGIN
    v_schema   := ORA_DICT_OBJ_OWNER;
    v_username := ORA_LOGIN_USER;
    
    -- SYS et SYSTEM peuvent tout faire
    IF v_username IN ('SYS', 'SYSTEM') THEN
        RETURN;
    END IF;
    
    -- Bloquer les opérations sur les schémas système
    IF v_schema IN (
        'SYS', 'SYSTEM', 'DBSNMP', 'OUTLN', 'WMSYS', 'CTXSYS',
        'MDSYS', 'OLAPSYS', 'ORDSYS', 'XDB', 'APEX_PUBLIC_USER',
        'ORACLE_OCM', 'APPQOSSYS', 'FLOWS_FILES', 'APEX_040200',
        'APEX_040000', 'AUDSYS', 'GSMADMIN_INTERNAL', 'ORDPLUGINS',
        'SI_INFORMTN_SCHEMA', 'ORDDATA', 'DVSYS', 'DVF', 'OJVMSYS', 'LBACSYS'
    ) THEN
        RAISE_APPLICATION_ERROR(-20001,
            'SECURITE: Operations DDL interdites sur schema systeme ' || v_schema);
    END IF;
    
END TRG_BLOCK_DDL_SYSTEM_ONLY;
/

-- =============================================================================
-- VÉRIFICATION
-- =============================================================================

PROMPT [INFO] Verification...

DECLARE
    v_status VARCHAR2(10);
BEGIN
    SELECT status INTO v_status
    FROM dba_objects
    WHERE owner = 'SYS'
      AND object_name = 'TRG_BLOCK_DDL_SYSTEM_ONLY'
      AND object_type = 'TRIGGER';
    
    IF v_status = 'VALID' THEN
        DBMS_OUTPUT.PUT_LINE('[SUCCESS] Trigger cree avec succes');
    ELSE
        DBMS_OUTPUT.PUT_LINE('[ERROR] Trigger INVALIDE');
        FOR rec IN (SELECT text FROM dba_errors
                    WHERE owner = 'SYS' 
                      AND name = 'TRG_BLOCK_DDL_SYSTEM_ONLY'
                    ORDER BY sequence) LOOP
            DBMS_OUTPUT.PUT_LINE('[ERROR] ' || rec.text);
        END LOOP;
        RAISE_APPLICATION_ERROR(-20999, 'Echec creation trigger');
    END IF;
END;
/

COMMIT;
/

EXIT 0;

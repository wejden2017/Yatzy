-- =============================================================================
-- NETTOYAGE COMPLET DES TRIGGERS DE SÉCURITÉ
-- =============================================================================

SET SERVEROUTPUT ON SIZE UNLIMITED;
SET FEEDBACK ON;
SET VERIFY OFF;

PROMPT ========================================
PROMPT Nettoyage des anciens triggers
PROMPT ========================================

-- Dropper TRG_SECURITY_SCHEMA_ACCESS (ancien)
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM dba_triggers
    WHERE owner = 'SYS'
      AND trigger_name = 'TRG_SECURITY_SCHEMA_ACCESS';
    
    IF v_count > 0 THEN
        EXECUTE IMMEDIATE 'DROP TRIGGER SYS.TRG_SECURITY_SCHEMA_ACCESS';
        DBMS_OUTPUT.PUT_LINE('[DROP] ✓ Trigger TRG_SECURITY_SCHEMA_ACCESS dropped');
    ELSE
        DBMS_OUTPUT.PUT_LINE('[INFO] Trigger TRG_SECURITY_SCHEMA_ACCESS does not exist');
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[ERROR] Failed to drop TRG_SECURITY_SCHEMA_ACCESS: ' || SQLERRM);
END;
/

-- Dropper TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS (nouveau, si existe)
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM dba_triggers
    WHERE owner = 'SYS'
      AND trigger_name = 'TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS';
    
    IF v_count > 0 THEN
        EXECUTE IMMEDIATE 'DROP TRIGGER SYS.TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS';
        DBMS_OUTPUT.PUT_LINE('[DROP] ✓ Trigger TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS dropped');
    ELSE
        DBMS_OUTPUT.PUT_LINE('[INFO] Trigger TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS does not exist');
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[ERROR] Failed to drop TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS: ' || SQLERRM);
END;
/

-- Dropper tout autre trigger DATABASE qui pourrait poser problème
DECLARE
    CURSOR c_triggers IS
        SELECT owner, trigger_name
        FROM dba_triggers
        WHERE owner = 'SYS'
          AND base_object_type = 'DATABASE'
          AND trigger_name LIKE '%SECURITY%';
    
    v_count NUMBER := 0;
BEGIN
    FOR rec IN c_triggers LOOP
        BEGIN
            EXECUTE IMMEDIATE 'DROP TRIGGER ' || rec.owner || '.' || rec.trigger_name;
            DBMS_OUTPUT.PUT_LINE('[DROP] ✓ Trigger ' || rec.trigger_name || ' dropped');
            v_count := v_count + 1;
        EXCEPTION
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('[ERROR] Failed to drop ' || rec.trigger_name || ': ' || SQLERRM);
        END;
    END LOOP;
    
    IF v_count = 0 THEN
        DBMS_OUTPUT.PUT_LINE('[INFO] No other security triggers found');
    END IF;
END;
/

PROMPT ========================================
PROMPT Création du nouveau trigger
PROMPT ========================================

-- =============================================================================
-- TRIGGER DE SÉCURITÉ SIMPLIFIÉ
-- Objectif: Bloquer UNIQUEMENT les opérations sur les schémas système
-- =============================================================================

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
    IF v_schema IN ('SYS', 'SYSTEM', 'DBSNMP', 'OUTLN', 'WMSYS', 'CTXSYS',
                    'MDSYS', 'OLAPSYS', 'ORDSYS', 'XDB', 'APEX_PUBLIC_USER',
                    'ORACLE_OCM', 'APPQOSSYS', 'FLOWS_FILES', 'APEX_040200') THEN
        RAISE_APPLICATION_ERROR(-20001,
            'SECURITE: Operations DDL interdites sur le schema systeme ' || v_schema);
    END IF;
    
    -- Les schémas applicatifs (LUCA, LUCA2, etc.) sont gérés par les privilèges Oracle
    
END TRG_BLOCK_DDL_SYSTEM_ONLY;
/

PROMPT ========================================
PROMPT Vérification du trigger
PROMPT ========================================

-- Vérifier que le trigger est valide
DECLARE
    v_status VARCHAR2(10);
    v_count  NUMBER;
BEGIN
    -- Vérifier l'existence
    SELECT COUNT(*) INTO v_count
    FROM dba_objects
    WHERE owner = 'SYS'
      AND object_name = 'TRG_BLOCK_DDL_SYSTEM_ONLY'
      AND object_type = 'TRIGGER';
    
    IF v_count = 0 THEN
        DBMS_OUTPUT.PUT_LINE('[ERROR] ❌ Trigger not found!');
        RAISE_APPLICATION_ERROR(-20999, 'Trigger creation failed - not found');
    END IF;
    
    -- Vérifier le statut
    SELECT status INTO v_status
    FROM dba_objects
    WHERE owner = 'SYS'
      AND object_name = 'TRG_BLOCK_DDL_SYSTEM_ONLY'
      AND object_type = 'TRIGGER';
    
    IF v_status = 'VALID' THEN
        DBMS_OUTPUT.PUT_LINE('[SUCCESS] ✅ Trigger TRG_BLOCK_DDL_SYSTEM_ONLY is VALID');
    ELSE
        DBMS_OUTPUT.PUT_LINE('[ERROR] ❌ Trigger TRG_BLOCK_DDL_SYSTEM_ONLY is INVALID');
        
        -- Afficher l'erreur de compilation
        FOR rec IN (SELECT line, position, text
                    FROM dba_errors
                    WHERE owner = 'SYS'
                      AND name = 'TRG_BLOCK_DDL_SYSTEM_ONLY'
                      AND type = 'TRIGGER'
                    ORDER BY sequence) LOOP
            DBMS_OUTPUT.PUT_LINE('  Error at line ' || rec.line || ', position ' || rec.position || ': ' || rec.text);
        END LOOP;
        
        RAISE_APPLICATION_ERROR(-20999, 'Trigger is INVALID');
    END IF;
END;
/

PROMPT ========================================
PROMPT Liste des triggers DATABASE actifs
PROMPT ========================================

SET PAGESIZE 50
SET LINESIZE 150

COLUMN owner FORMAT A10
COLUMN trigger_name FORMAT A40
COLUMN status FORMAT A10
COLUMN triggering_event FORMAT A30

SELECT owner, trigger_name, status, triggering_event
FROM dba_triggers
WHERE owner = 'SYS'
  AND base_object_type = 'DATABASE'
ORDER BY trigger_name;

PROMPT ========================================
PROMPT Script terminé
PROMPT ========================================

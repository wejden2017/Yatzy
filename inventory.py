-- =============================================================================
-- TRIGGER DE SÉCURITÉ - Protection des schémas système
-- Environnement: {{ lookup('env', 'ENV') | upper }}
-- Base: {{ oracle_sid | default('UNKNOWN') }}
-- Date: {{ ansible_date_time.iso8601 }}
-- =============================================================================
-- Ce trigger est créé UNE SEULE FOIS dans SYS pour TOUTE la base de données
-- Il protège les schémas système contre les opérations DDL non autorisées
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
-- ÉTAPE 1 : SUPPRESSION DES ANCIENS TRIGGERS
-- =============================================================================

PROMPT [INFO] Nettoyage des anciens triggers de sécurité...

DECLARE
    v_count NUMBER := 0;
    
    -- Liste de tous les triggers de sécurité à supprimer
    TYPE t_trigger_names IS TABLE OF VARCHAR2(128);
    v_triggers t_trigger_names := t_trigger_names(
        'TRG_SECURITY_SCHEMA_ACCESS',
        'TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS',
        'TRG_BLOCK_DDL_SYSTEM_ONLY',
        'TRG_BLOCK_DROP_EXCEPT_LUCA'
    );
    
    v_sql VARCHAR2(1000);
BEGIN
    -- Parcourir et dropper chaque trigger s'il existe
    FOR i IN 1..v_triggers.COUNT LOOP
        BEGIN
            SELECT COUNT(*) INTO v_count
            FROM dba_triggers
            WHERE owner = 'SYS'
              AND trigger_name = v_triggers(i);
            
            IF v_count > 0 THEN
                v_sql := 'DROP TRIGGER SYS.' || v_triggers(i);
                EXECUTE IMMEDIATE v_sql;
                DBMS_OUTPUT.PUT_LINE('[DROP] Trigger ' || v_triggers(i) || ' supprime');
            END IF;
            
        EXCEPTION
            WHEN OTHERS THEN
                -- Continuer même en cas d'erreur
                DBMS_OUTPUT.PUT_LINE('[WARN] Impossible de supprimer ' || v_triggers(i) || ': ' || SQLERRM);
        END;
    END LOOP;
    
    DBMS_OUTPUT.PUT_LINE('[INFO] Nettoyage termine');
    
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('[ERROR] Erreur lors du nettoyage: ' || SQLERRM);
        RAISE;
END;
/

-- =============================================================================
-- ÉTAPE 2 : CRÉATION DU NOUVEAU TRIGGER
-- =============================================================================

PROMPT [INFO] Creation du trigger de securite...

CREATE OR REPLACE TRIGGER SYS.TRG_BLOCK_DDL_SYSTEM_ONLY
BEFORE DROP OR ALTER OR TRUNCATE ON DATABASE
DECLARE
    v_schema   VARCHAR2(128);
    v_username VARCHAR2(128);
    v_obj_type VARCHAR2(50);
BEGIN
    -- Récupérer les informations de l'opération
    v_schema   := ORA_DICT_OBJ_OWNER;
    v_username := ORA_LOGIN_USER;
    v_obj_type := ORA_DICT_OBJ_TYPE;
    
    -- ========================================================================
    -- RÈGLE 1 : SYS et SYSTEM peuvent tout faire
    -- ========================================================================
    IF v_username IN ('SYS', 'SYSTEM') THEN
        RETURN;
    END IF;
    
    -- ========================================================================
    -- RÈGLE 2 : Bloquer UNIQUEMENT les opérations sur les schémas système
    -- ========================================================================
    IF v_schema IN (
        'SYS', 'SYSTEM', 'DBSNMP', 'OUTLN', 'WMSYS', 'CTXSYS',
        'MDSYS', 'OLAPSYS', 'ORDSYS', 'XDB', 'APEX_PUBLIC_USER',
        'ORACLE_OCM', 'APPQOSSYS', 'FLOWS_FILES', 'APEX_040200',
        'APEX_040000', 'APEX_030200', 'AUDSYS', 'GSMADMIN_INTERNAL',
        'ORDPLUGINS', 'SI_INFORMTN_SCHEMA', 'ORDDATA', 'SPATIAL_CSW_ADMIN_USR',
        'SPATIAL_WFS_ADMIN_USR', 'DVSYS', 'DVF', 'OJVMSYS', 'LBACSYS'
    ) THEN
        RAISE_APPLICATION_ERROR(-20001,
            'SECURITE: Operations DDL interdites sur le schema systeme ' || v_schema);
    END IF;
    
    -- ========================================================================
    -- RÈGLE 3 : Les schémas applicatifs sont autorisés
    -- Les permissions sont contrôlées par les privilèges Oracle (rôles)
    -- ========================================================================
    -- Pas de restriction supplémentaire
    
END TRG_BLOCK_DDL_SYSTEM_ONLY;
/

-- =============================================================================
-- ÉTAPE 3 : VÉRIFICATION DU TRIGGER
-- =============================================================================

PROMPT [INFO] Verification du trigger...

DECLARE
    v_status VARCHAR2(10);
    v_count  NUMBER;
    v_error_found BOOLEAN := FALSE;
BEGIN
    -- Vérifier que le trigger existe
    SELECT COUNT(*) INTO v_count
    FROM dba_objects
    WHERE owner = 'SYS'
      AND object_name = 'TRG_BLOCK_DDL_SYSTEM_ONLY'
      AND object_type = 'TRIGGER';
    
    IF v_count = 0 THEN
        DBMS_OUTPUT.PUT_LINE('[ERROR] Le trigger n''a pas ete cree');
        RAISE_APPLICATION_ERROR(-20999, 'Trigger non cree');
    END IF;
    
    -- Vérifier le statut du trigger
    SELECT status INTO v_status
    FROM dba_objects
    WHERE owner = 'SYS'
      AND object_name = 'TRG_BLOCK_DDL_SYSTEM_ONLY'
      AND object_type = 'TRIGGER';
    
    IF v_status = 'VALID' THEN
        DBMS_OUTPUT.PUT_LINE('[SUCCESS] Trigger TRG_BLOCK_DDL_SYSTEM_ONLY cree avec succes');
    ELSE
        DBMS_OUTPUT.PUT_LINE('[ERROR] Le trigger est INVALIDE');
        
        -- Afficher les erreurs de compilation
        FOR rec IN (
            SELECT line, position, text
            FROM dba_errors
            WHERE owner = 'SYS'
              AND name = 'TRG_BLOCK_DDL_SYSTEM_ONLY'
              AND type = 'TRIGGER'
            ORDER BY sequence
        ) LOOP
            DBMS_OUTPUT.PUT_LINE('[ERROR] Ligne ' || rec.line || ': ' || rec.text);
            v_error_found := TRUE;
        END LOOP;
        
        IF v_error_found THEN
            RAISE_APPLICATION_ERROR(-20999, 'Trigger invalide - voir erreurs ci-dessus');
        END IF;
    END IF;
    
END;
/

-- =============================================================================
-- ÉTAPE 4 : AFFICHAGE DU RÉSULTAT
-- =============================================================================

PROMPT [INFO] Configuration finale:

SET PAGESIZE 50
SET LINESIZE 150
SET FEEDBACK ON
SET HEADING ON

COLUMN owner FORMAT A10
COLUMN trigger_name FORMAT A40
COLUMN status FORMAT A10
COLUMN triggering_event FORMAT A30

SELECT owner, trigger_name, status, triggering_event
FROM dba_triggers
WHERE owner = 'SYS'
  AND base_object_type = 'DATABASE'
  AND trigger_name = 'TRG_BLOCK_DDL_SYSTEM_ONLY';

PROMPT
PROMPT [SUCCESS] Script termine avec succes
PROMPT

-- =============================================================================
-- COMMIT FINAL
-- =============================================================================

COMMIT;
/
EXIT 0;

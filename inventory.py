-- =============================================================================
-- TRIGGER DE SÉCURITÉ - Bloquer DROP/ALTER/TRUNCATE sur schémas système
-- =============================================================================

DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM dba_triggers
    WHERE owner = 'SYS'
      AND trigger_name = 'TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS';
    
    IF v_count > 0 THEN
        EXECUTE IMMEDIATE 'DROP TRIGGER SYS.TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS';
        DBMS_OUTPUT.PUT_LINE('[DROP] Trigger TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS dropped');
    END IF;
END;
/

CREATE OR REPLACE TRIGGER SYS.TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS
BEFORE DROP OR ALTER OR TRUNCATE ON DATABASE
DECLARE
    v_schema      VARCHAR2(128);
    v_username    VARCHAR2(128);
    v_operation   VARCHAR2(50);
    v_object_type VARCHAR2(50);
    v_object_name VARCHAR2(128);
BEGIN
    -- Récupérer les informations sur l'opération
    v_schema      := ORA_DICT_OBJ_OWNER;
    v_username    := ORA_LOGIN_USER;
    v_object_name := ORA_DICT_OBJ_NAME;
    v_object_type := ORA_DICT_OBJ_TYPE;
    
    -- Déterminer le type d'opération
    IF ORA_SYSEVENT = 'DROP' THEN
        v_operation := 'DROP';
    ELSIF ORA_SYSEVENT = 'ALTER' THEN
        v_operation := 'ALTER';
    ELSIF ORA_SYSEVENT = 'TRUNCATE' THEN
        v_operation := 'TRUNCATE';
    ELSE
        v_operation := 'UNKNOWN';
    END IF;
    
    -- ====================================================================
    -- RÈGLE 1 : SYS et SYSTEM peuvent tout faire
    -- ====================================================================
    IF v_username IN ('SYS', 'SYSTEM') THEN
        RETURN;
    END IF;
    
    -- ====================================================================
    -- RÈGLE 2 : Bloquer les opérations sur les schémas système
    -- ====================================================================
    IF v_schema IN ('SYS', 'SYSTEM', 'DBSNMP', 'OUTLN', 'WMSYS', 'CTXSYS',
                    'MDSYS', 'OLAPSYS', 'ORDSYS', 'XDB', 'APEX_PUBLIC_USER') THEN
        RAISE_APPLICATION_ERROR(-20001,
            'SECURITE: ' || v_operation || ' interdit sur le schema systeme ' || v_schema);
    END IF;
    
    -- ====================================================================
    -- RÈGLE 3 : Les schémas {{ schemas | join(', ') }} sont autorisés
    -- ====================================================================
    -- Pas de vérification supplémentaire, on laisse passer
    
END TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS;
/

BEGIN
    DBMS_OUTPUT.PUT_LINE('[CREATE] Trigger TRG_BLOCK_DDL_ON_SYSTEM_SCHEMAS created');
    DBMS_OUTPUT.PUT_LINE('[INFO] Ce trigger bloque les operations DDL sur les schemas systeme uniquement');
END;
/

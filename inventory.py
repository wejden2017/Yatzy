-- Récupérer les informations sur l'opération
v_schema     := ORA_DICT_OBJ_OWNER;
v_username   := ORA_LOGIN_USER;
v_object_name := ORA_DICT_OBJ_NAME;
v_object_type := ORA_DICT_OBJ_TYPE;

-- Identifier l'opération
IF ORA_SYSEVENT = 'DROP' THEN
   v_operation := 'DROP';
ELSIF ORA_SYSEVENT = 'ALTER' THEN
   v_operation := 'ALTER';
ELSIF ORA_SYSEVENT = 'TRUNCATE' THEN
   v_operation := 'TRUNCATE';
ELSE
   v_operation := 'UNKNOWN';
END IF;

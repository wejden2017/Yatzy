1. Create security trigger (TRG_SECURITY_SCHEMA_ACCESS)
   → Exécuté en: SYS/SYSDBA
   → Template: security_system_object.sql.j2
   → run_once: true

2. Create roles per schema (DEV_LUCA_ROLE, DEV_LUCA2_ROLE, ...)
   → Exécuté en: SYS/SYSDBA
   → Template: create_role.sql.j2
   → run_once: true

3. Create grant procedures (one per schema)
   → Exécuté en: LUCA, LUCA2, LUCA3, etc. (loop sur schemas)
   → Template: grant_access_to_schema.sql.j2

4. Create DDL triggers (auto-grant, one per schema)
   → Exécuté en: LUCA, LUCA2, LUCA3, etc. (loop sur schemas)
   → Template: auto_grant_trigger.sql.j2

5. Manage users (create/delete/lock/unlock/reset-password)
   → Exécuté en: SYS/SYSDBA
   → Template: user_present.sql.j2
   → Loop sur: users

6. Execute grant procedures (apply grants on existing objects)
   → Exécuté en: LUCA, LUCA2, LUCA3, etc. (loop sur schemas)
   → SQL direct: EXEC GRANT_xxx_ACCESS

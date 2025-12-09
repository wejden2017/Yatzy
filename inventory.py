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

# =============================================================================
# ÉTAPE 3 : CREATE GRANT PROCEDURES (per schema)
# =============================================================================

- name: Render grant procedure script
  template:
    src: grant_access_to_schema.sql.j2
    dest: "/tmp/grant_access_procedure_{{ lookup('env', 'ENV') }}.sql"
    mode: "0640"
  tags: [setup, procedure]

- name: Create GRANT_{{ oracle_role_name }}_ACCESS_TO_SCHEMA procedure on {{ item }}
  shell: |
    set -eo pipefail
    sqlplus -s {{ item }}/{{ schema_password }}@{{ oracle_connect.host }}:{{ oracle_connect.port }}/{{ oracle_connect.service }} <<'SQL'
    WHENEVER SQLERROR EXIT 1
    WHENEVER SQLERROR EXIT SQL.SQLCODE
    SET SERVEROUTPUT ON SIZE UNLIMITED
    SET HEADING OFF FEEDBACK OFF PAGES 0 VERIFY OFF ECHO OFF TERMOUT ON
    SPOOL /tmp/grant_procedure_{{ item }}.log
    @/tmp/grant_access_procedure_{{ lookup('env', 'ENV') }}.sql
    SPOOL OFF
    EXIT
    SQL
  args:
    executable: /bin/bash
  environment:
    ORACLE_HOME: "{{ oracle_home }}"
    LD_LIBRARY_PATH: "{{ oracle_home }}/lib"
    PATH: "{{ oracle_home }}/bin:{{ ansible_env.PATH | default('') }}"
  loop: "{{ schemas }}"
  register: create_procedure
  changed_when: "create_procedure.rc == 0"
  failed_when: "create_procedure.rc != 0"
  tags: [setup, procedure]

- name: Display procedure creation result for {{ item }}
  debug:
    msg: "{{ lookup('file', '/tmp/grant_procedure_' + item + '.log') }}"
  loop: "{{ schemas }}"
  when: ansible_verbosity | int >= 1
  tags: [setup, procedure]

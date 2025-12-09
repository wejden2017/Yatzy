- name: Create GRANT_{{ oracle_role_name }}_ACCESS_TO_SCHEMA procedure
  shell: |
    set -eo pipefail
    {{ _ora_sqlplus }} << 'SQL'
    WHENEVER SQLERROR EXIT 1
    WHENEVER SQLERROR EXIT SQL.SQLCODE
    SET SERVEROUTPUT ON SIZE UNLIMITED
    SET HEADING OFF FEEDBACK OFF PAGES 0 VERIFY OFF ECHO OFF TERMOUT ON
    SPOOL /tmp/grant_procedure.log
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
  register: create_procedure
  changed_when: "create_procedure.rc == 0"
  failed_when: "create_procedure.rc != 0"
  tags: [setup, procedure]

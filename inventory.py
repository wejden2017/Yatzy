SELECT DISTINCT owner AS username, tablespace_name
FROM dba_segments
WHERE owner = 'LUCA'
ORDER BY tablespace_name;


SELECT username, tablespace_name, max_bytes,
       CASE 
         WHEN max_bytes = -1 THEN 'UNLIMITED'
         WHEN max_bytes IS NULL THEN 'NO QUOTA'
         ELSE TO_CHAR(max_bytes)
       END AS quota_status
FROM dba_ts_quotas
WHERE username = 'LUCA'
ORDER BY tablespace_name;


SELECT 
    s.tablespace_name,
    q.max_bytes,
    CASE 
        WHEN q.max_bytes = -1 THEN 'UNLIMITED'
        WHEN q.max_bytes IS NULL THEN 'NO QUOTA'
        ELSE TO_CHAR(q.max_bytes)
    END AS quota_status
FROM 
    (SELECT DISTINCT tablespace_name 
     FROM dba_segments 
     WHERE owner = 'LUCA') s
LEFT JOIN 
    dba_ts_quotas q
ON s.tablespace_name = q.tablespace_name
AND q.username = 'LUCA'
ORDER BY tablespace_name;


ALTER USER LUCA QUOTA 50G ON BATCH;
ALTER USER LUCA QUOTA 50G ON TBS_DATA_ARCH;
ALTER USER LUCA QUOTA 50G ON TBS_DATA_JOUR;
ALTER USER LUCA QUOTA 50G ON TBS_DATA_REF;
ALTER USER LUCA QUOTA 50G ON TBS_IDX_ARCH;
ALTER USER LUCA QUOTA 50G ON TBS_IDX_JOUR;
ALTER USER LUCA QUOTA 50G ON TBS_IDX_REF;
ALTER USER LUCA QUOTA 50G ON USERS;

SELECT username, tablespace_name, max_bytes
FROM dba_ts_quotas
WHERE username = 'LUCA'
ORDER BY tablespace_name;

-- 1) Voir les rôles actifs
SELECT * 
FROM session_roles
ORDER BY role;

-- 2) Voir les privilèges système actifs
SELECT privilege
FROM session_privs
ORDER BY privilege;



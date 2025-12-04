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

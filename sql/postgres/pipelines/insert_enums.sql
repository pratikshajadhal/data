INSERT INTO exec_statuses(id, status_name) VALUES
    (1, 'PENDING'),
    (2, 'RUNNING'),
    (3, 'SUCCESS'),
    (4, 'CANCELLED'),
    (5, 'FAILURE')
ON CONFLICT DO NOTHING;

INSERT INTO error_reasons(id, reason_name) VALUES
    (1, 'GENERAL'),
    (2, 'AUTH'),
    (3, 'SCHEMA_CFG')
ON CONFLICT DO NOTHING;

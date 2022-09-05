INSERT INTO pipelines(uuid, org_uuid, tpa_identifier, pipeline_number, config_yaml, status_id, started_at, ended_at, created_at, updated_at) VALUES
    ('bdb68ac8-b5b8-40bc-a2f0-aebc4e8f16cb', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'instagram', 1, '', 3, '2022-08-30 11:23:45', '2022-08-30 11:24:45', '2022-08-30 11:23:15', '2022-08-30 11:24:45'),
    ('b2c85ede-fd02-45c2-aa99-8d1065b4e1c0', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 1, '', 3, '2022-08-30 12:23:45', '2022-08-30 18:23:45', '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    ('132a13a2-e30a-4596-a910-2e918378573f', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 2, '', 5, '2022-08-30 13:23:45', '2022-08-30 19:24:45', '2022-08-30 13:23:15', '2022-08-30 19:24:45')
ON CONFLICT DO NOTHING;

INSERT INTO jobs(uuid, pipeline_id, job_identifier, status_id, error_reason_id, error_details, started_at, ended_at, created_at, updated_at) VALUES
    ('f3295e88-c206-4102-b891-aac979869b3d', 1, 'INSTAGRAM_PULL_POSTS', 3, 2, '{ "error_detail": "ABC"}', '2022-08-30 11:23:45', '2022-08-30 11:24:45', '2022-08-30 11:23:15', '2022-08-30 11:24:45'),
    ('6eef4911-1060-420b-b302-9ea8827a992f', 1, 'INSTAGRAM_PULL_AD_ACTIVITY', 3, 1, '{ "error_detail": "ABC"}',  '2022-08-30 11:23:45', '2022-08-30 11:24:45', '2022-08-30 11:23:15', '2022-08-30 11:24:45'),
    ('d30e91c5-1c2c-4458-b9b0-e15bca96fe98', 2, 'FILEVINE_HISTORICAL_PULL', 3, 1, '{ "error_detail": "ABC"}',  '2022-08-30 12:23:45', '2022-08-30 18:23:45', '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    ('c520d1e2-f0d4-4ee3-99bd-3777d0f9bb79', 3, 'FILEVINE_HISTORICAL_PULL', 3, 3, '{ "error_detail": "ABC"}',  '2022-08-30 13:23:45', '2022-08-30 19:24:45', '2022-08-30 13:23:15', '2022-08-30 19:23:45')
ON CONFLICT DO nothing;
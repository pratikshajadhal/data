INSERT INTO pipelines(id, uuid, org_uuid, tpa_identifier, pipeline_number, config_yaml, status_id, started_at, ended_at, created_at, updated_at) VALUES
    (1, 'bdb68ac8-b5b8-40bc-a2f0-aebc4e8f16cb', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'instagram', 1, '', 3, '2022-08-30 11:23:45', '2022-08-30 11:24:45', '2022-08-30 11:23:15', '2022-08-30 11:24:45'),
    (32, 'b2c85ede-fd02-45c2-aa99-8d1065b4e1c0', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 2, '', 3, '2022-08-30 12:23:45', '2022-08-30 18:23:45', '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (142, '132a13a2-e30a-4596-a910-2e918378573f', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 3, '', 5, '2022-08-30 13:23:45', '2022-08-30 19:24:45', '2022-08-30 13:23:15', '2022-08-30 19:24:45'),

    -- for testing pipeline status RUNNING
    (343, '232a13a2-e30a-4596-a910-2e918378573f', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 4, '', 1, NULL, NULL, '2022-08-30 13:23:15', '2022-08-30 19:24:45'),

    -- for testing pipeline status SUCCESS
    (344, '332a13a2-e30a-4596-a910-2e918378573f', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 5, '', 2, '2022-08-30 13:23:45', NULL, '2022-08-30 13:23:15', '2022-08-30 19:24:45'),

    -- for testing pipeline status CANCELLED
    (345, '432a13a2-e30a-4596-a910-2e918378573f', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 6, '', 2, '2022-08-30 13:23:45', NULL, '2022-08-30 13:23:15', '2022-08-30 19:24:45'),

    -- for testing pipeline status FAILED (without CANCELLED)
    (346, '532a13a2-e30a-4596-a910-2e918378573f', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 7, '', 2, '2022-08-30 13:23:45', NULL, '2022-08-30 13:23:15', '2022-08-30 19:24:45'),

    -- for testing pipeline status FAILED (wit CANCELLED)
    (347, '632a13a2-e30a-4596-a910-2e918378573f', '97b23e8a-ab86-4559-b686-09dc409f24b8', 'filevine', 8, '', 2, '2022-08-30 13:23:45', NULL, '2022-08-30 13:23:15', '2022-08-30 19:24:45')
ON CONFLICT DO NOTHING;

INSERT INTO jobs(id, uuid, pipeline_id, job_identifier, status_id, started_at, ended_at, created_at, updated_at) VALUES
    (1, 'f3295e88-c206-4102-b891-aac979869b3d', (SELECT id FROM pipelines WHERE uuid = 'bdb68ac8-b5b8-40bc-a2f0-aebc4e8f16cb'), 'INSTAGRAM_PULL_POSTS', 1, '2022-08-30 11:23:45', '2022-08-30 11:24:45', '2022-08-30 11:23:15', '2022-08-30 11:24:45'),
    (2, '6eef4911-1060-420b-b302-9ea8827a992f', (SELECT id FROM pipelines WHERE uuid = 'bdb68ac8-b5b8-40bc-a2f0-aebc4e8f16cb'), 'INSTAGRAM_PULL_AD_ACTIVITY', 1, '2022-08-30 11:23:45', '2022-08-30 11:24:45', '2022-08-30 11:23:15', '2022-08-30 11:24:45'),
    (3, 'd30e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = 'b2c85ede-fd02-45c2-aa99-8d1065b4e1c0'), 'FILEVINE_HISTORICAL_PULL', 3, '2022-08-30 12:23:45', '2022-08-30 18:23:45', '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (4, 'c520d1e2-f0d4-4ee3-99bd-3777d0f9bb79', (SELECT id FROM pipelines WHERE uuid = '132a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 3, '2022-08-30 13:23:45', '2022-08-30 19:24:45', '2022-08-30 13:23:15', '2022-08-30 19:23:45'),

    -- for testing pipeline status RUNNING
    (5, 'e30e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '232a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 1, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (6, 'f30e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '232a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 1, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (7, '130e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '232a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 1, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),

    -- for testing pipeline status SUCCESS
    (8, '230e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '332a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 3, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (9, '330e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '332a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 3, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (10, '430e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '332a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 2, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),

    -- for testing pipeline status CANCELLED
    (11, '530e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '432a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 3, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (12, '630e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '432a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 3, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (13, '730e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '432a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 2, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),

    -- for testing pipeline status FAILED (without CANCELLED)
    (14, '830e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '532a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 3, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (15, '930e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '532a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 3, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (16, '030e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '532a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 2, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),

    -- for testing pipeline status FAILED (with CANCELLED)
    (17, 'a30e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '632a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 5, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (18, 'b30e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '632a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 4, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45'),
    (19, 'c30e91c5-1c2c-4458-b9b0-e15bca96fe98', (SELECT id FROM pipelines WHERE uuid = '632a13a2-e30a-4596-a910-2e918378573f'), 'FILEVINE_HISTORICAL_PULL', 2, NULL, NULL, '2022-08-30 12:23:15', '2022-08-30 18:23:45')
ON CONFLICT DO NOTHING;

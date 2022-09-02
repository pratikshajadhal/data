from __future__ import annotations

from collections import namedtuple
from http import HTTPStatus
from uuid import UUID

import pytest

from api_server.app import app
from fastapi.testclient import TestClient

from etl.destination import get_postgres, reset_db
from models.request import ExecStatus

client = TestClient(app)


def send_job_status(pipeline: str | UUID, job: str | UUID, status: ExecStatus, http_status: int = 200, response=None):
    if response is None:
        response = {"message": "OK"}

    if isinstance(pipeline, UUID):
        pipeline = str(pipeline)

    if isinstance(job, UUID):
        job = str(job)

    res = client.put(
        f"/pipelines/{pipeline}/jobs/{job}",
        json={
            "status": status,
        },
    )

    assert res.status_code == http_status
    assert res.json() == response


def set_job_status_and_check_pipeline(pipeline: str | UUID, job: str | UUID,
                                      set_to: ExecStatus, before: ExecStatus, after: ExecStatus):
    if isinstance(pipeline, UUID):
        pipeline = str(pipeline)

    if isinstance(job, UUID):
        job = str(job)

    assert get_postgres().pipeline(pipeline).status == before
    send_job_status(pipeline, job, set_to)
    assert get_postgres().pipeline(pipeline).status == after


@pytest.fixture(scope="session", autouse=True)
def fixture():
    reset_db()


pipeline_status_test_case = namedtuple("pipeline_status_test_case", "pipeline job set_to before after")


class TestUpdateJobStatus:
    def test_running(self):
        send_job_status(
            'bdb68ac8-b5b8-40bc-a2f0-aebc4e8f16cb',
            'f3295e88-c206-4102-b891-aac979869b3d',
            ExecStatus.RUNNING,
        )

    def test_for_nonexistent_pipeline(self):
        send_job_status(
            '22222222-fd02-45c2-aa99-8d1065b4e1c0',
            '6eef4911-1060-420b-b302-9ea8827a992f',
            ExecStatus.RUNNING,
            HTTPStatus.NOT_FOUND,
            {
                "detail": "job/pipeline not found",
            }
        )

    def test_for_nonexistent_job(self):
        send_job_status(
            'b2c85ede-fd02-45c2-aa99-8d1065b4e1c0',
            '22222222-1060-420b-b302-9ea8827a992f',
            ExecStatus.RUNNING,
            HTTPStatus.NOT_FOUND,
            {
                "detail": "job/pipeline not found",
            }
        )

    ####################################################################
    # WARNING: the tests below DOES NOT handle setting status PENDING. #
    ####################################################################

    def test_anything_other_than_running_updates_ended_at(self):
        p, j = UUID('bdb68ac8-b5b8-40bc-a2f0-aebc4e8f16cb'), UUID('6eef4911-1060-420b-b302-9ea8827a992f'),
        send_job_status(p, j, ExecStatus.CANCELLED)

        assert get_postgres().job(p, j).ended_at is not None

    def test_setting_to_running_updates_started_at_and_resets_ended_at(self):
        p, j = UUID('132a13a2-e30a-4596-a910-2e918378573f'), UUID('c520d1e2-f0d4-4ee3-99bd-3777d0f9bb79')
        previous_job = get_postgres().job(p, j)

        send_job_status(p, j, ExecStatus.RUNNING)

        job = get_postgres().job(p, j)
        assert previous_job.started_at != job.started_at and job.ended_at is None

    @pytest.mark.parametrize("c", [
            pipeline_status_test_case(
                '232a13a2-e30a-4596-a910-2e918378573f', '130e91c5-1c2c-4458-b9b0-e15bca96fe98',
                ExecStatus.RUNNING, ExecStatus.PENDING, ExecStatus.RUNNING,
            ),
            pipeline_status_test_case(
                '332a13a2-e30a-4596-a910-2e918378573f', '430e91c5-1c2c-4458-b9b0-e15bca96fe98',
                ExecStatus.SUCCESS, ExecStatus.RUNNING, ExecStatus.SUCCESS,
            ),
            pipeline_status_test_case(
                '432a13a2-e30a-4596-a910-2e918378573f', '730e91c5-1c2c-4458-b9b0-e15bca96fe98',
                ExecStatus.CANCELLED, ExecStatus.RUNNING, ExecStatus.CANCELLED,
            ),
            pipeline_status_test_case(
                '532a13a2-e30a-4596-a910-2e918378573f', '030e91c5-1c2c-4458-b9b0-e15bca96fe98',
                ExecStatus.FAILURE, ExecStatus.RUNNING, ExecStatus.FAILURE,
            ),
            pipeline_status_test_case(
                '632a13a2-e30a-4596-a910-2e918378573f', 'c30e91c5-1c2c-4458-b9b0-e15bca96fe98',
                ExecStatus.FAILURE, ExecStatus.RUNNING, ExecStatus.FAILURE,
            ),
        ])
    def test_pipeline_status(self, c: pipeline_status_test_case):
        pipeline = UUID(c.pipeline)
        job = UUID(c.job)

        assert get_postgres().pipeline(pipeline).status == c.before
        send_job_status(pipeline, job, c.set_to)
        assert get_postgres().pipeline(pipeline).status == c.after

    # def test_restarting_one_job_in_non_running_pipeline_sets_pipeline_to_running_again(self):
    #     assert False

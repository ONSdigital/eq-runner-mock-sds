from datetime import datetime, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from .main import (
    app,
    encrypt_mock_data,
    get_mocked_chronological_date,
    get_version_number,
    generate_dataset_id,
    get_schema_version
)

client = TestClient(app)


def test_get_sds_unit_data_found():
    response = client.get(
        "/v1/unit_data",
        params={
            "dataset_id": "d8afa921-1305-d553-d2c6-955a6db2cc2d",
            "identifier": "12345678901",
        },
    )
    assert response.status_code == 200
    assert "data" in response.json()


def test_get_sds_unit_data_not_found():
    response = client.get(
        "/v1/unit_data",
        params={
            "dataset_id": "00000000-0000-0000-0000-000000000000",
            "identifier": "12345678901",
        },
    )
    assert response.status_code == 404


def test_get_sds_unit_data_invalid_uuid():
    response = client.get("/v1/unit_data", params={"dataset_id": "invalid_uuid"})
    assert response.status_code == 422


def test_get_sds_dataset_metadata_ids_found():
    response = client.get(
        "/v1/dataset_metadata", params={"survey_id": "123", "period_id": "202301"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_sds_dataset_metadata_ids_not_found():
    response = client.get(
        "/v1/dataset_metadata",
        params={
            "survey_id": "non_existent_survey_id",
            "period_id": "non_existent_period_id",
        },
    )
    assert response.status_code == 404


def test_encrypt_mock_data():
    mock_data = {"key": "value"}
    encrypted_data = encrypt_mock_data(mock_data)
    assert isinstance(encrypted_data, str)


@pytest.mark.parametrize(
    "dataset_id, survey_id, schema_version, dataset_version",
    (
            ("d8afa921-1305-d553-d2c6-955a6db2cc2d", "123", "v1.0.0", "v1"),
            ("f3628c40-380e-38f0-de4f-ee7f481fbede", "123", "v2.0.0", "v2"),
    )
)
def test_generate_dataset_id(dataset_id, survey_id, schema_version, dataset_version):
    expected_dataset_id = UUID(dataset_id)
    actual_dataset_id = generate_dataset_id(
        survey_id=survey_id,
        schema_version=schema_version,
        dataset_version=dataset_version,
    )
    assert actual_dataset_id == expected_dataset_id


@pytest.mark.parametrize(
    "schema_version",
    ("v1", "v2")
)
def test_get_mocked_chronological_date(schema_version):
    assert datetime.fromisoformat(get_mocked_chronological_date(schema_version)) > datetime.now(
        tz=timezone.utc
    )


@pytest.mark.parametrize(
    "dataset_version, version_number",
    (
        ("v1", 1),
        ("v2", 2),
        ("v3", 3),
        ("v4", 4)
    )
)
def test_get_version_number(dataset_version, version_number):
    assert get_version_number(dataset_version) == version_number


@pytest.mark.parametrize(
    "filepath, filename, result",
    (
            ("test", "v1.json", "v1.0.0"),
            ("test", "v2.json", "v2.0.0"),
            ("test", "v3.json", "v1.0.0")
    )
)
def test_get_schema_version(filepath, filename, result):
    assert get_schema_version(filepath, filename) == result

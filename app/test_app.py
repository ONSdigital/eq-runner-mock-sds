from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from .main import (
    app,
    encrypt_mock_data,
    get_mocked_chronological_date,
    get_version_number,
    generate_dataset_id,
)

client = TestClient(app)


def test_get_sds_unit_data_found():
    response = client.get(
        "/v1/unit_data",
        params={
            "dataset_id": "abb98e61-7631-60fa-3058-e1f59006db31",
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


def test_generate_dataset_id():
    expected_dataset_id = UUID("abb98e61-7631-60fa-3058-e1f59006db31")
    actual_dataset_id = generate_dataset_id(
        survey_id="123",
        schema_version="v1.0.0",
        dataset_version="v1",
        period_id="201605",
    )
    assert expected_dataset_id == actual_dataset_id


def test_get_mocked_chronological_date():
    assert datetime.fromisoformat(get_mocked_chronological_date("v1")) > datetime.now(
        tz=timezone.utc
    )


def test_get_version_number():
    assert get_version_number("v1") == 1

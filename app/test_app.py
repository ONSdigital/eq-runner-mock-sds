import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from .main import (
    app,
    encrypt_mock_data,
    load_mock_sds_dataset_metadata,
    load_mock_data,
)

client = TestClient(app)


def test_get_sds_data_found():
    response = client.get(
        "/v1/unit_data",
        params={
            "dataset_id": "c067f6de-6d64-42b1-8b02-431a3486c178",
            "identifier": "1234678912",
        },
    )
    assert response.status_code == 200
    assert "data" in response.json()


def test_get_sds_data_not_found():
    response = client.get(
        "/v1/unit_data",
        params={
            "dataset_id": "00000000-0000-0000-0000-000000000000",
            "identifier": "1234678912",
        },
    )
    assert response.status_code == 404


def test_get_sds_data_invalid_uuid():
    response = client.get("/v1/unit_data", params={"dataset_id": "invalid_uuid"})
    assert response.status_code == 422


def test_get_sds_dataset_ids_found():
    response = client.get(
        "/v1/dataset_metadata", params={"survey_id": "123", "period_id": "202301"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_sds_dataset_ids_not_found():
    response = client.get(
        "/v1/dataset_metadata",
        params={
            "survey_id": "non_existent_survey_id",
            "period_id": "non_existent_period_id",
        },
    )
    assert response.status_code == 404


def test_load_mock_data():
    mock_data = load_mock_data("mock_data/supplementary_data.json")
    assert isinstance(mock_data, dict)


def test_load_mock_sds_dataset_metadata_found():
    mock_data = load_mock_sds_dataset_metadata("123")
    assert isinstance(mock_data, list)


def test_load_mock_sds_dataset_metadata_not_found():
    with pytest.raises(HTTPException) as exc_info:
        load_mock_sds_dataset_metadata("non_existent_survey_id")
    assert exc_info.value.status_code == 404


def test_encrypt_mock_data():
    mock_data = {"data": {"key": "value"}}
    encrypted_data = encrypt_mock_data(mock_data)
    assert "data" in encrypted_data
    assert isinstance(encrypted_data["data"], str)

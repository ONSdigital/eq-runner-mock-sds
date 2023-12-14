import json
from typing import MutableMapping
from uuid import UUID

import uvicorn
import yaml
from fastapi import FastAPI, Query, HTTPException
from sdc.crypto.jwe_helper import JWEHelper
from sdc.crypto.key_store import KeyStore

KEY_PURPOSE_SDS = "supplementary_data"

app = FastAPI()

with open("dev-keys.yml", encoding="UTF-8") as keys_file:
    keys = KeyStore(yaml.safe_load(keys_file))


@app.get("/v1/unit_data")
def get_sds_data(
    dataset_id: UUID, identifier: str = Query(min_length=1)
) -> MutableMapping:
    mock_data = load_mock_data("mock_data/supplementary_data.json")

    data_by_id = {row["identifier"]: row["unit_data"] for row in mock_data["data"]}
    base_response = {
        "dataset_id": "c067f6de-6d64-42b1-8b02-431a3486c178",
        "survey_id": "068",
        "data": data_by_id[identifier]
    }

    return encrypt_mock_data(base_response)

@app.get("/v1/dataset_metadata")
def get_sds_dataset_ids(
    survey_id: str = Query(min_length=1), period_id: str = Query(min_length=1)
) -> list[dict]:
    # The mock current does not make use of period_id
    return load_mock_sds_dataset_metadata(survey_id)


def load_mock_data(filename: str) -> dict | list:
    with open(filename, encoding="utf-8") as mock_data_file:
        return json.load(mock_data_file)


def load_mock_sds_dataset_metadata(survey_id: str) -> list[dict]:
    survey_id_filename_map = {
        "068": "supplementary_dataset_metadata_response",
    }

    if filename := survey_id_filename_map.get(survey_id):
        return load_mock_data(f"mock_data/{filename}.json")

    raise HTTPException(status_code=404)


def encrypt_mock_data(mock_data: MutableMapping) -> MutableMapping:
    key = keys.get_key(purpose=KEY_PURPOSE_SDS, key_type="private")
    mock_data["data"] = JWEHelper.encrypt_with_key(
        json.dumps(mock_data["data"]), key.kid, key.as_jwk()
    )
    return mock_data


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5003)

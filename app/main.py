import hashlib
import json
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from pathlib import Path
from typing import MutableMapping, Optional
from uuid import UUID

import uvicorn
import yaml
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from sdc.crypto.jwe_helper import JWEHelper
from sdc.crypto.key_store import KeyStore

KEY_PURPOSE_SDS = "supplementary_data"
MOCK_DATA_PATH = Path(__file__).parent.parent / "mock_data"

app = FastAPI()

with open("dev-keys.yml", encoding="UTF-8") as keys_file:
    keys = KeyStore(yaml.safe_load(keys_file))


SURVEY_ID_TO_MOCK_DATA_FOLDER_MAPPING = {
    "221": "bres_and_brs",
    "241": "bres_and_brs",
    "014": "prodcom",
    "068": "roofing_tiles_slate_sand_and_gravel",
    "071": "roofing_tiles_slate_sand_and_gravel",
    "066": "roofing_tiles_slate_sand_and_gravel",
    "076": "roofing_tiles_slate_sand_and_gravel",
    "123": "test",
}


class Metadata(BaseModel):
    """
    Model for SDS Metadata Response
    copied from https://github.com/ONSdigital/sds/blob/main/src/app/models/dataset_models.py#L19
    """
    survey_id: str
    period_id: str
    form_types: list[str]
    sds_published_at: str
    total_reporting_units: int
    schema_version: str
    sds_dataset_version: int
    filename: str
    dataset_id: UUID
    title: str | None = None
    data: list[dict]    # additional eQ-only field for mapping the mocked unit data


@app.get("/v1/unit_data")
def get_sds_data(
    dataset_id: UUID, identifier: str = Query(min_length=1)
) -> MutableMapping:
    # The mock current does not make use of identifier

    # TODO: This map is now created earlier on
    # guid_filename_map = {
    #     "c067f6de-6d64-42b1-8b02-431a3486c178": "supplementary_data",
    #     "693dc252-2e90-4412-bd9c-c4d953e36fcd": "supplementary_data_v2",
    #     "9b418603-ba90-4c93-851a-f9cecfbda06f": "supplementary_data_v3",
    # }


    # have a dict that holds identifier and datasset_id for lookups - dynamically (either a tuple or a dict)
    # ensure that the identifier matches between launcher, runner

    if filename := guid_filename_map.get(str(dataset_id)):
        return encrypt_mock_data(load_mock_data(f"mock_data/{filename}.json"))

    raise HTTPException(status_code=404)


@app.get("/v1/dataset_metadata")
def get_sds_dataset_ids(
    survey_id: str = Query(min_length=1), period_id: str = Query(min_length=1)
) -> list[dict]:
    # The mock currently does not make use of period_id
    return load_mock_sds_dataset_metadata(survey_id)


def get_mocked_chronological_date(schema_version: str) -> str:
    """Using the schema version, we can ensure mocked dates appear 'chronological'"""
    base_date = "2021-01-01T00:00:00Z"

    chronological_date = datetime.fromisoformat(base_date) + timedelta(weeks=get_version_number(schema_version))
    return chronological_date.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_version_number(dataset_version: str) -> int:
    return int(dataset_version[1:])


def get_json_file_count_from_path(path: Path) -> int:
    return sum(1 for _ in path.glob("*.json"))


def build_sds_data(*, survey_id: str, period_id: str, dataset_id: UUID, path: Path) -> Metadata:
    """
    Add docstring here
    """

    metadata = {
        "survey_id": survey_id,
        "period_id": period_id,
        "form_types": ['001', '002'], # TODO: generate dynamically eventually
        "sds_published_at": get_mocked_chronological_date(path.name),
        "total_reporting_units": get_json_file_count_from_path(path),
        "schema_version": "v1.0.0",
        "sds_dataset_version": get_version_number(path.name),
        # "sds_schema_version": 1, # TODO: No longer needed? Not in official data model for SDS
        "filename": "",
        "dataset_id": dataset_id,
        "title": f"{path.name} (survey_id: {survey_id}) supplementary data",
    }

    unit_data: list[dict] = []
    for json_file in path.glob("*.json"):
        json_data = json.loads(json_file.read_text())
        unit_data.append(json_data)

    metadata['data'] = unit_data

    return Metadata.model_validate(
        {**metadata}, from_attributes=True
    )


def generate_dataset_id(*, survey_id: str, schema_version: str, dataset_version: str, period_id: str) -> UUID:
    """deterministically a generate dataset_id"""
    combined_hash = hashlib.sha256(
        f"{survey_id}_{schema_version}_{dataset_version}_{period_id}".encode("utf-8")
    ).hexdigest()
    return UUID(combined_hash[:32])


@lru_cache(maxsize=1)
def load_mock_data(survey_id: str, folder_name: str) -> dict | list:

    metadata_collection: list[Metadata] = []
    mock_data_survey_path = MOCK_DATA_PATH / folder_name

    for path in mock_data_survey_path.iterdir():
        dataset_id = generate_dataset_id(
            survey_id=survey_id,
            schema_version="v1.0.0",  # TODO: Hardcoded for now
            dataset_version=path.name,
            period_id="202312"
        )
        metadata_collection.append(build_sds_data(
            survey_id=survey_id,
            period_id="202312",   # TODO: Can get this from the request if needed?
            dataset_id=dataset_id,
            path=path,
        ))
    print(metadata_collection)


        # unit_data = "REMOVE BEFORE RESPONSE IS SENT unit_data" : {"value of identifier 123455 etc": "the actual data from the mocked file json"} # TODO: Add unit data

    # metadata: list[MetadataResponse] = []
    # mock_data_survey_path = MOCK_DATA_PATH / folder_name
    #
    # for schema_path in mock_data_survey_path.rglob("*.json"):
    #     json_data = json.loads(schema_path.read_text())
    #     metadata.append(build_sds_data(
    #         survey_id,
    #         "202312",   # TODO: Can get this from the request if needed?
    #         schema_path
    #     ))
    #     # unit_data = "REMOVE BEFORE RESPONSE IS SENT unit_data" : {"value of identifier 123455 etc": "the actual data from the mocked file json"} # TODO: Add unit data


    # with open(MOCK_DATA_PATH / filename, encoding="utf-8") as mock_data_file:
    #     return json.load(mock_data_file)


def load_mock_sds_dataset_metadata(survey_id: str) -> list[dict]:
    if folder_name := SURVEY_ID_TO_MOCK_DATA_FOLDER_MAPPING.get(survey_id):
        return load_mock_data(survey_id, folder_name)

    raise HTTPException(status_code=404)





    # survey_id_filename_map = {
    #     "123": "supplementary_dataset_metadata_response",
    # }
    #
    # if filename := survey_id_filename_map.get(survey_id):
    #     return load_mock_data(f"mock_data/{filename}.json")
    #
    # raise HTTPException(status_code=404)


def encrypt_mock_data(mock_data: MutableMapping) -> MutableMapping:
    key = keys.get_key(purpose=KEY_PURPOSE_SDS, key_type="private")
    mock_data["data"] = JWEHelper.encrypt_with_key(
        json.dumps(mock_data["data"]), key.kid, key.as_jwk()
    )
    return mock_data


if __name__ == "__main__":
    # uvicorn.run(app, host="localhost", port=5003)
    get_sds_dataset_ids("221")

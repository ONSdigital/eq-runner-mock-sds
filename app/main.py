import hashlib
import json
from copy import deepcopy
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


app = FastAPI()

with open("dev-keys.yml", encoding="UTF-8") as keys_file:
    keys = KeyStore(yaml.safe_load(keys_file))

KEY_PURPOSE_SDS = "supplementary_data"
MOCK_DATA_ROOT_PATH = Path(__file__).parent.parent / "mock_data"
PERIOD_ID = "201605"  # matches Launcher period_id

MOCK_DATA_PATHS_BY_SURVEY_ID = {
    "bres_and_brs": ["221", "241"],
    "prodcom": ["014"],
    "roofing_tiles_slate_sand": ["068", "076", "077", "076"],
    "test": "123",
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
    data: dict  # additional eQ-only field for mapping the mocked unit data


@app.get("/v1/unit_data")
def get_sds_data(dataset_id: UUID, identifier: str = Query(min_length=1)) -> dict:
    # The mock current does not make use of identifier
    metadata_collection = load_mock_data()

    for metadata in metadata_collection:
        if metadata.dataset_id == dataset_id:
            if unit_data := metadata.data.get(identifier):
                return unit_data
    raise HTTPException(status_code=404)


@app.get("/v1/dataset_metadata")
def get_sds_dataset_ids(
    survey_id: str = Query(min_length=1), period_id: str = Query(min_length=1)
) -> list[Metadata]:
    # The mock currently does not make use of period_id
    metadata_collection = (
        load_mock_data()
    )  # TODO: As we're modifying the object, make a deepcopy first??

    if filtered_metadata_by_survey_id := [
        metadata
        for metadata in metadata_collection
        if metadata.survey_id == survey_id and not delattr(metadata, "data")
    ]:
        return filtered_metadata_by_survey_id
    raise HTTPException(status_code=404)


def get_mocked_chronological_date(schema_version: str) -> str:
    """Using the schema version, we can ensure mocked dates appear 'chronological'"""
    base_date = "2021-01-01T00:00:00Z"
    chronological_date = datetime.fromisoformat(base_date) + timedelta(
        weeks=get_version_number(schema_version)
    )
    return chronological_date.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_version_number(dataset_version: str) -> int:
    return int(dataset_version[1:])


def get_json_file_count_from_path(path: Path) -> int:
    return sum(1 for _ in path.glob("*.json"))


def build_sds_data(
    *, survey_id: str, period_id: str, dataset_id: UUID, path: Path
) -> Metadata:
    """
    Add docstring here
    """

    metadata = {
        "survey_id": survey_id,
        "period_id": period_id,
        "form_types": ["001", "002"],  # TODO: generate dynamically
        "sds_published_at": get_mocked_chronological_date(path.name),
        "total_reporting_units": get_json_file_count_from_path(path),
        "schema_version": "v1.0.0",
        "sds_dataset_version": get_version_number(path.name),
        # "sds_schema_version": 1, # TODO: No longer needed? Not in official data model for SDS
        "filename": "",
        "dataset_id": dataset_id,
        "title": f"{path.parent.name} {path.name} supplementary data (survey_id: {survey_id})",
    }

    units = {
        json_file.stem: json.loads(json_file.read_text())
        for json_file in path.glob("*.json")
    }
    metadata["data"] = units
    return Metadata.model_validate({**metadata}, from_attributes=True)


def generate_dataset_id(
    *, survey_id: str, schema_version: str, dataset_version: str, period_id: str
) -> UUID:
    """deterministically a generate dataset_id"""
    combined_hash = hashlib.sha256(
        f"{survey_id}_{schema_version}_{dataset_version}_{period_id}".encode("utf-8")
    ).hexdigest()
    return UUID(combined_hash[:32])


@lru_cache(maxsize=1)
def load_mock_data() -> list[Metadata]:
    metadata_collection: list[Metadata] = []

    def process_path(survey_id, path):
        dataset_id = generate_dataset_id(
            survey_id=survey_id,
            schema_version="v1.0.0",
            dataset_version=path.name,
            period_id=PERIOD_ID,
        )
        metadata_collection.append(
            build_sds_data(
                survey_id=survey_id,
                period_id=PERIOD_ID,
                dataset_id=dataset_id,
                path=path,
            )
        )

    for survey_mock_path in MOCK_DATA_ROOT_PATH.rglob("*"):
        if survey_ids := MOCK_DATA_PATHS_BY_SURVEY_ID.get(survey_mock_path.name):
            if not isinstance(survey_ids, list):
                survey_ids = [survey_ids]
            for survey_id in survey_ids:
                for path in survey_mock_path.iterdir():
                    process_path(survey_id, path)

    return metadata_collection


def encrypt_mock_data(mock_data: MutableMapping) -> MutableMapping:
    key = keys.get_key(purpose=KEY_PURPOSE_SDS, key_type="private")
    mock_data["data"] = JWEHelper.encrypt_with_key(
        json.dumps(mock_data["data"]), key.kid, key.as_jwk()
    )
    return mock_data


if __name__ == "__main__":
    # uvicorn.run(app, host="localhost", port=5003)
    # metadata = get_sds_dataset_ids("221")
    # print(metadata)
    data = get_sds_data(UUID("7b049fcb-aec7-83c6-375d-5f166b5f5005"), "34942807969")
    print(data)

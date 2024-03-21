import hashlib
import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import MutableMapping
from uuid import UUID

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

PERIOD_ID = "201605"  # matches Launcher
SCHEMA_VERSION = "v1.0.0"
FORM_TYPES = ["001"]

# TODO: Hardcoded paths for now - update if any changes are made to https://github.com/ONSdigital/sds-schema-definitions/tree/main/examples
MOCK_DATA_PATHS_BY_SURVEY_ID = {
    "test": ["123"],
    "prodcom": ["014"],
    "bres_and_brs": [
        "221",  # BRES
        "241",  # BRS
    ],
    "roofing_tiles_slate_sand_and_gravel": [
        "068",  # Roofling tiles
        "071",  # Slate
        "066",  # Sand and & Gravel (Land Won) - TODO: will need a PR to separate into 066 and 076 folder
        "076",  # "Sand & Gravel (Marine Dredged)"
    ],
}


class DatasetMetadata(BaseModel):
    """
    Model for SDS Metadata Response
    copied from https://github.com/ONSdigital/sds/blob/main/src/app/models/dataset_models.py#L19
    """

    # Required fields
    survey_id: str
    period_id: str
    form_types: list[str]
    sds_published_at: str
    total_reporting_units: int
    schema_version: str
    sds_dataset_version: int
    filename: str
    dataset_id: UUID

    # Optional fields
    title: str | None = None


class UnitData(BaseModel):
    """
    Model for SDS Unit Data Response
    copied from https://github.com/ONSdigital/sds/blob/main/src/app/models/dataset_models.py#L53
    """

    dataset_id: UUID
    survey_id: str
    period_id: str
    form_types: list[str]
    schema_version: str
    data: object


@app.get("/v1/unit_data")
def get_unit_data(dataset_id: UUID, identifier: str = Query(min_length=1)) -> UnitData:
    # The mock current does not make use of identifier
    """Return an encrypted map of mocked unit data for the given dataset_id and identifier"""
    _, dataset_to_unit_data_map = load_mock_data()

    if unit_data := dataset_to_unit_data_map.get(dataset_id):
        return unit_data

    raise HTTPException(status_code=404)


@app.get("/v1/dataset_metadata")
def get_dataset_metadata(
    survey_id: str = Query(min_length=1), period_id: str = Query(min_length=1)
) -> list[DatasetMetadata]:
    """Return a list of dataset metadata for the given survey_id"""
    # The mock currently does not make use of period_id
    dataset_metadata_collection, _ = load_mock_data()

    if filtered_dataset_metadata_by_survey_id := [
        dataset_metadata
        for dataset_metadata in dataset_metadata_collection
        if dataset_metadata.survey_id == survey_id
    ]:
        return filtered_dataset_metadata_by_survey_id
    raise HTTPException(status_code=404)


def get_mocked_chronological_date(schema_version: str) -> str:
    """Using the schema version, we can ensure mocked dates appear 'chronological'"""
    chronological_date = datetime.now(timezone.utc) + timedelta(
        weeks=get_version_number(schema_version)
    )
    return chronological_date.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_version_number(dataset_version: str) -> int:
    return int(dataset_version[1:])


def get_json_file_count_from_path(path: Path) -> int:
    return sum(1 for _ in path.glob("*.json"))


def build_dataset_metadata(
    *, survey_id: str, period_id: str, dataset_id: UUID, path: Path
) -> DatasetMetadata:
    dataset_metadata = {
        "survey_id": survey_id,
        "period_id": period_id,
        "form_types": FORM_TYPES,
        "sds_published_at": get_mocked_chronological_date(path.name),
        "total_reporting_units": get_json_file_count_from_path(path),
        "schema_version": SCHEMA_VERSION,
        "sds_dataset_version": get_version_number(path.name),
        "filename": "",
        "dataset_id": dataset_id,
        "title": f"{path.parent.name} {path.name} supplementary data (survey_id: {survey_id})",
    }

    return DatasetMetadata.model_validate({**dataset_metadata}, from_attributes=True)


def build_unit_data(
    *, survey_id: str, period_id: str, dataset_id: UUID, path: Path
) -> UnitData:
    json_data = {
        json_file.stem: json.loads(json_file.read_text())
        for json_file in path.glob("*.json")
    }

    unit_data = {
        "dataset_id": dataset_id,
        "survey_id": survey_id,
        "period_id": period_id,
        "form_types": FORM_TYPES,
        "schema_version": SCHEMA_VERSION,
        "data": encrypt_mock_data(json_data),
    }

    return UnitData.model_validate({**unit_data}, from_attributes=True)


def generate_dataset_id(
    *, survey_id: str, schema_version: str, dataset_version: str, period_id: str
) -> UUID:
    """deterministically a generate dataset_id"""
    combined_hash = hashlib.sha256(
        f"{survey_id}_{schema_version}_{dataset_version}_{period_id}".encode("utf-8")
    ).hexdigest()
    return UUID(combined_hash[:32])


@lru_cache(maxsize=1)
def load_mock_data() -> tuple[list[DatasetMetadata], dict[UUID, UnitData]]:
    dataset_metadata_collection: list[DatasetMetadata] = []
    dataset_id_unit_data_map: dict[UUID, UnitData] = {}

    for survey_mock_data_path in MOCK_DATA_ROOT_PATH.rglob("*"):
        survey_ids = MOCK_DATA_PATHS_BY_SURVEY_ID.get(survey_mock_data_path.name, [])
        for survey_id in survey_ids:
            for path in survey_mock_data_path.iterdir():
                dataset_id = generate_dataset_id(
                    survey_id=survey_id,
                    schema_version=SCHEMA_VERSION,
                    dataset_version=path.name,
                    period_id=PERIOD_ID,
                )
                dataset_metadata_collection.append(
                    build_dataset_metadata(
                        survey_id=survey_id,
                        period_id=PERIOD_ID,
                        dataset_id=dataset_id,
                        path=path,
                    )
                )
                dataset_id_unit_data_map[dataset_id] = build_unit_data(
                    survey_id=survey_id,
                    period_id=PERIOD_ID,
                    dataset_id=dataset_id,
                    path=path,
                )

    return dataset_metadata_collection, dataset_id_unit_data_map


def encrypt_mock_data(mock_data: MutableMapping) -> str:
    key = keys.get_key(purpose=KEY_PURPOSE_SDS, key_type="private")
    mock_data = JWEHelper.encrypt_with_key(json.dumps(mock_data), key.kid, key.as_jwk())
    return mock_data


if __name__ == "__main__":
    # uvicorn.run(app, host="localhost", port=5003)
    # metadata = get_dataset_metadata("123")
    # print(metadata)
    data = get_unit_data(UUID("7b049fcb-aec7-83c6-375d-5f166b5f5005"), "34942807969")
    print(data)

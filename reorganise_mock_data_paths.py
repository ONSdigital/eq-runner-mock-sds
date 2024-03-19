import json
import os
import shutil
from pathlib import Path

MOCK_DATA_PATH = Path(__file__).parent / "mock_data"
EXCLUDED_FOLDER = MOCK_DATA_PATH / "test"


MOCK_DATA_FOLDER_NAME_TO_SURVEY_MAP = {
    "bres_and_brs": ["221", "241"],
    "prodcom": "014",
    "roofing_tiles_slate_sand_and_gravel": [
        "068", # roofling tiles
        "071", # slate
        "066", # Sand and & Gravel (Land Won) - TODO: will need a PR to separate into 066 and 076 folder
        "076", # Sand & Gravel (Marine Dredged)
    ],
    "test": "123"
}


def reorganise_mock_data():

    # TODO: For testing
    json_files = list(MOCK_DATA_PATH.rglob("*.json"))

    for folder in EXCLUDED_FOLDER.iterdir():
        print(folder)

    # TODO: The below works great, uncomment when ready
    # # Create a predefined list of files so that newly created ones aren't picked up again in loop
    # json_files = list(MOCK_DATA_PATH.rglob("*.json"))
    #
    # for schema_path in json_files:
    #     if EXCLUDED_FOLDER not in schema_path.parents:
    #         json_data = json.loads(schema_path.read_text())
    #
    #         # Create a folder and move the json file there with the identifier as its name
    #         new_destination_path = schema_path.parent / schema_path.stem
    #         new_destination_path.mkdir()
    #         new_file_name = new_destination_path / json_data["identifier"]
    #         schema_path.replace(new_file_name.with_suffix(".json"))


if __name__ == '__main__':
    reorganise_mock_data()
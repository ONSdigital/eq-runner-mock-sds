import json
from pathlib import Path

MOCK_DATA_PATH = Path(__file__).parent / "mock_data"
EXCLUDED_FOLDER = MOCK_DATA_PATH / "test"


def reorganise_mock_data():
    # Create a predefined list of files so that newly created ones aren't picked up again in loop
    json_files = list(MOCK_DATA_PATH.rglob("*.json"))

    for schema_path in json_files:
        if EXCLUDED_FOLDER not in schema_path.parents:
            json_data = json.loads(schema_path.read_text())

            # Create a folder and move the json file there with the identifier as its name
            new_destination_path = schema_path.parent / schema_path.stem
            new_destination_path.mkdir()
            new_file_name = new_destination_path / json_data["identifier"]
            schema_path.replace(new_file_name.with_suffix(".json"))


if __name__ == "__main__":
    reorganise_mock_data()

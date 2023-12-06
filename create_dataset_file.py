import json
import os
from pprint import pprint

from sdc.crypto.jwe_helper import JWEHelper

from app.main import encrypt_mock_data


def main():
    # For each folder in mock_data
    for folder in os.listdir("mock_data"):
        if ".json" in folder:
            continue

        survey_id = folder.split("_")[-1]
        for version_folder in os.listdir(f"mock_data/{folder}"):
            # For each file in the folder

            datas = []

            for file in os.listdir(f"mock_data/{folder}/{version_folder}"):
                if "dataset" in file:
                    continue

                # Read the content of the mock data file
                with open(f"mock_data/{folder}/{version_folder}/{file}", "r") as mock_file:
                    mock_data = json.load(mock_file)

                # Extract information from the mock data file
                identifier = mock_data["identifier"]
                encrypted_data = encrypt_mock_data(mock_data)
                datas.append({"identifier": identifier, "unit_data": encrypted_data})

            # Create a new data structure
            new_data = {
                "title": folder.replace("_", " ").upper(),
                "survey_id": survey_id,
                "period_id": "202403",
                "schema_version": version_folder,
                "form_types": ["0001"],
                "data": datas,
            }

            new_data_path = f"dataset_{folder}_{version_folder}.json"

            with open(new_data_path, "w") as new_file:
                json.dump(new_data, new_file, indent=4)

            print(f"Dataset JSON file '{new_data_path}' created successfully!")

        # # Initialize a list to store extracted data
        # extracted_data = []
        # survey_id = None
        #
        # # Loop through the list of file paths
        # for mock_data_path in mock_data_paths:
        #     # Read the content of the mock data file
        #     with open(mock_data_path, "r") as mock_file:
        #         mock_data = json.load(mock_file)
        #
        #     # Extract information from the mock data file
        #     identifier = mock_data["data"]["identifier"]
        #     survey_id = mock_data["survey_id"]
        #
        #     encrypted_data = encrypt_mock_data(mock_data)["data"]
        #
        #     # Append extracted data to the list
        #     extracted_data.append(
        #         {"identifier": identifier, "unit_data": encrypted_data}
        #     )
        #
        # # Create a new data structure
        # new_data = {
        #     "title": f"Dummy prepop data {idx}",
        #     "survey_id": survey_id,
        #     "period_id": "201605",
        #     "schema_version": "v1",
        #     "form_types": ["0001"],
        #     "encryption_key_id": "123",
        #     "data": extracted_data,
        # }
        #
        # new_data_path = f"dataset_{idx}.json"
        #
        # with open(new_data_path, "w") as new_file:
        #     json.dump(new_data, new_file, indent=4)
        #
        # print(f"Dataset JSON file '{new_data_path}' created successfully!")



if __name__ == "__main__":
    main()

run:
	poetry run python app/main.py

format:
	poetry run black .

lint:
	poetry run black --check .

test:
	poetry run pytest .

build: load-example-data reorganise-example-data-paths

load-example-data:
	# TODO: move to python script?
	./scripts/load_mock_data.sh

reorganise-example-data-paths:
	poetry run python reorganise_mock_data_paths.py

run:
	poetry run python app/main.py

format:
	poetry run black .

lint:
	poetry run black --check .

test:
	poetry run pytest .

build: load-example-data

load-example-data:
	./scripts/load_mock_data.sh


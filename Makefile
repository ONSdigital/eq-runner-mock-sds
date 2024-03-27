run:
	poetry run python app/main.py

format:
	poetry run black .

lint:
	poetry run black --check .

test:
	poetry run pytest .

load-mock-unit-data:
	./scripts/load_mock_data.sh


# eq-runner-mock-sds

A simple FastAPI to mock the SDS service required by eq-runner.


## Pre-requisites

1. Python installed using [Pyenv](https://github.com/pyenv/pyenv). Version is specified in `.python-version` file.
2. [Poetry Package Manager](https://python-poetry.org/)

## Install Dependencies

To install dependencies using poetry, run the following command:

```bash
poetry install
```

## Running Locally

### Prerequisites
To launch business surveys that make use of supplementary data, you'll first need to pull down example unit data from 
the [sds-schema-definitions](https://github.com/ONSdigital/sds-schema-definitions/tree/main/examples) examples. To do 
this, run the following command:

```bash
make build
```

**IMPORTANT:** The hardcoded `MOCK_DATA_PATHS_BY_SURVEY_ID` in `app/main.py` will need to be updated if **any** of the 
`sds-schema-definitions` example folders change

## Running 
To run the FastAPI application locally using `uvicorn`, use the following command:

```bash
make run
```

The application will be accessible at `http://localhost:5003`.

## Docker

You can also containerize the application using Docker.

1. Build the Docker image:

```bash
docker build -t eq-runner-mock-sds .
```

1. Run the Docker container:

```bash
docker run -d -p 5003:5003 eq-runner-mock-sds
```

The FastAPI app will be available at `http://localhost:5003`.

## Development

### Code Formatting

To format the code using black, run the following command:

```bash
make format
```

### Code Linting

To lint the code using black, run the following command:

```bash
make lint
```

### Testing

To run the unit tests, run the following command:

```bash
make test
```

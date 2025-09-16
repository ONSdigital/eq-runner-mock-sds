#!/usr/bin/env bash

set -e

REPO_NAME="sds-schema-definitions"

DOWNLOAD_URL="https://github.com/onsdigital/${REPO_NAME}/archive/refs/heads/ashe-schema-definition.zip"
DOWNLOAD_NAME="${REPO_NAME}-ashe-schema-definition"

echo "Fetching ${DOWNLOAD_URL}"

TEMP_DIR=$(mktemp -d)

curl -L --url "${DOWNLOAD_URL}" --output "${TEMP_DIR}/${DOWNLOAD_NAME}"

unzip -o "${TEMP_DIR}/${DOWNLOAD_NAME}" "${DOWNLOAD_NAME}/examples/*" -d .

# idempotent - replace all mock data examples
for path in "${DOWNLOAD_NAME}"/examples/*; do
  folder=$(basename "$path")
  rm -rf ./mock_data/"${folder}"
  mv -f "${path}" ./mock_data/
done

rm -rf "${DOWNLOAD_NAME}"
rm -rf "${TEMP_DIR}"

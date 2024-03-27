#!/usr/bin/env bash

set -e

# TODO: For PR testing convenience - revert when PR in sds-schema-definitions repo is merged
# PR CONVENIENCE BLOCK START
mkdir temp_sds_schema
git clone -b update-example-file-names-with-test-identifier https://github.com/ONSdigital/sds-schema-definitions temp_sds_schema

for path in temp_sds_schema/examples/*; do
  folder=$(basename "$path")
  rm -rf ./mock_data/"${folder}"
  mv -f "${path}" ./mock_data/
done

rm -rf temp_sds_schema
# PR CONVENIENCE BLOCK END


# TODO: Below lines to be reverted when update-example-file-names-with-test-identifier branch is merged in sds-schema-definitions repo
#REPO_NAME="sds-schema-definitions"
#SDS_SCHEMA_DEFINITIONS_REPO="onsdigital/${REPO_NAME}"
#
#DOWNLOAD_URL="https://github.com/${SDS_SCHEMA_DEFINITIONS_REPO}/archive/refs/heads/main.zip"
#DOWNLOAD_NAME="${REPO_NAME}-main"
#
#echo "Fetching ${DOWNLOAD_URL}"
#
#TEMP_DIR=$(mktemp -d)
#
#curl -L --url "${DOWNLOAD_URL}" --output "${TEMP_DIR}/${DOWNLOAD_NAME}"
#
#unzip -o "${TEMP_DIR}/${DOWNLOAD_NAME}" "${DOWNLOAD_NAME}/examples/*" -d .
#
## idempotent - replace all mock data examples
#for path in "${DOWNLOAD_NAME}"/examples/*; do
#  folder=$(basename "$path")
#  rm -rf ./mock_data/"${folder}"
#  mv -f "${path}" ./mock_data/
#done
#
#rm -rf "${DOWNLOAD_NAME}"
#rm -rf "${TEMP_DIR}"

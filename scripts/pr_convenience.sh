#!/usr/bin/env bash

set -e

mkdir temp_sds_schema
git clone -b update-example-file-names-with-test-identifier https://github.com/ONSdigital/sds-schema-definitions temp_sds_schema

for path in temp_sds_schema/examples/*; do
  folder=$(basename "$path")
  rm -rf ./mock_data/"${folder}"
  mv -f "${path}" ./mock_data/
done

rm -rf temp_sds_schema
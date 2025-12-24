#!/bin/bash

find cache -type f -name "*.parquet" \
  ! -name "$(date +%Y-%m-%d).parquet" \
  -regex '.*/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\.parquet$' \
  -delete

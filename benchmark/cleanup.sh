#!/bin/bash

rm -rf test_data_dir
curl -X DELETE -u elastic:elastic -v http://localhost:9200/idx-articles

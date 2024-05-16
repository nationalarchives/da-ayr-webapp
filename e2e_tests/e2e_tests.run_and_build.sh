#!/bin/bash
docker build -t e2e_tests . && docker run --rm --env-file "$(dirname `pwd`)"/.env.e2e_tests --network=host -v "$(dirname `pwd`)"/e2e_tests:/e2e_tests e2e_tests 
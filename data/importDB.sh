#!/bin/bash

tar -xzvf census.tar.gz

docker exec -i apexsql mysql -uroot -prootPass  < census.sql


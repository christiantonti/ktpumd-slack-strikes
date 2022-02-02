#!/bin/bash
zip code.zip lambda_function.py
aws lambda update-function-code --function-name ktpSlackStrikes --zip-file fileb://code.zip
rm code.zip
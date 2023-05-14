#!/bin/bash 

TIME=`date`
APIGW="https://n7redw9zh3.execute-api.eu-west-1.amazonaws.com/Prod/"
message="Hello World, the time is: ${TIME}"

echo sending message: $message
echo

curl --location --request POST ${APIGW}/inbox \
  --header 'Content-Type: application/json' \
  --data-raw '{ "message": $message }'

echo
echo "sleeping for a sec..."
echo

sleep 1

echo
echo "retriving message from output Queue"
echo

curl ${APIGW}/outbox



#!/bin/bash

./publish.sh
cd  ../../
echo -e '\nRunning cdk synth\n'
cdk synth

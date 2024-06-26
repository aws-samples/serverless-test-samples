##usage: .\deploy.sh yourprefix
#!/bin/bash
prefix=${1:-""}

./publish.sh
cd  ../../
echo -e '\nRunning cdk deploy for BedrockAgentStack\n'
cdk deploy "BedrockAgentStack" -c prefix="$prefix" --require-approval never

echo -e '\nRunning cdk deploy for BedrockGuardrailStack\n'
cdk deploy "BedrockGuardrailStack" -c prefix="$prefix" --require-approval never

#echo -e '\nRunning cdk deploy for WebSocketStack\n'
#cdk deploy "WebSocketStack" -c prefix="$prefix" --require-approval never

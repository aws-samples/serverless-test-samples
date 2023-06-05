import { SNSClient, PublishCommand } from '@aws-sdk/client-sns'
import { APIGatewayProxyEvent, APIGatewayProxyResult } from "aws-lambda";
import axios from 'axios';
import delay from './delay';
const snsClient = new SNSClient({ region: process.env.AWS_REGION })
const topicArn = process.env.SNS_TOPIC_ARN

exports.main = async function(event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> {
  if (event.body) {

    for (let i=0; i < 3; i++) {
      await axios.get('https://datadoghq.com')
      await delay(15)
    }
    const command = new PublishCommand({
      TopicArn: topicArn,
      Message: event.body
    })
    await snsClient.send(command)
    console.log('published a message to SNS')
    const response: APIGatewayProxyResult = {
      statusCode: 200,
      body: JSON.stringify({
        status: 'pushed'
      })
    }
    return response
  }
  const response: APIGatewayProxyResult = {
    statusCode: 422,
    body: JSON.stringify({
      status: 'Body required'
    })
  }
  return response
}


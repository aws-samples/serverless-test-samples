import { SQSEvent } from "aws-lambda";
import axios from 'axios';
import delay from './delay';

exports.main = async function(event: SQSEvent): Promise<void> {
  for (let i=0; i < 5; i++) {
      await axios.get('https://datadoghq.com');
      await delay(15);
    }
  console.log('SQS worker successfully received event:', event)
}


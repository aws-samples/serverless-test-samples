import { S3Event } from 'aws-lambda';
import { S3Client, GetObjectCommand, GetObjectCommandInput } from '@aws-sdk/client-s3';
const client = new S3Client({ region: process.env.AWS_REGION });
import { DynamoDBClient, PutItemCommand, PutItemCommandInput, PutItemCommandOutput } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';

export const handler = async (event: S3Event): Promise<string> => {
    const bucket = event.Records[0].s3.bucket.name;
    const key = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));
    try {
        const data = await getObjectFromBucket(bucket, key);
        console.log(`Successfully retrieved data from bucket - ${bucket}`);
        await putDataInDynamoTable(key, data);
        console.log(`Successfully put item in table`);
        return `'Success'`;
    } catch (err) {
        console.log(err);
        const message = `Error processing object ${key} from bucket ${bucket}. Make sure they exist and your bucket is in the same region as this function.`;
        console.log(message);
        throw new Error(message);
    }
};

const getObjectFromBucket = async (bucket: string, key: string): Promise<string | undefined> => {
    const getParams: GetObjectCommandInput = {
        Bucket: bucket,
        Key: key,
    };
    const getCommand = new GetObjectCommand(getParams);
    const { Body } = await client.send(getCommand);
    return Body?.transformToString();
};

const putDataInDynamoTable = (key: string, data: string | undefined): Promise<PutItemCommandOutput> => {
    const dynamodb = new DynamoDBClient({});
    const ddb = DynamoDBDocumentClient.from(dynamodb);
    const item: PutItemCommandInput = {
        TableName: process.env.RESULTS_TABLE,
        Item: {
            id: {
                S: key,
            },
            message: {
                S: data || '',
            },
        },
    };
    return ddb.send(new PutItemCommand(item));
};

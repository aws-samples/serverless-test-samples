/**
 * Integration Tests
 * Before running this we need the stack already deployed
 * Set the environment variable AWS_SAM_STACK_NAME to match the name of the stack you will test
 *
 */
import {
    S3Client,
    GetObjectCommand,
    GetObjectCommandInput,
    PutObjectCommand,
    PutObjectCommandInput,
    PutObjectCommandOutput,
    DeleteObjectCommand,
    DeleteObjectCommandInput,
    DeleteObjectCommandOutput,
} from '@aws-sdk/client-s3';
import {
    DynamoDBClient,
    GetItemCommand,
    GetItemCommandInput,
    GetItemCommandOutput,
    DeleteItemCommand,
    DeleteItemCommandInput,
    DeleteItemCommandOutput,
} from '@aws-sdk/client-dynamodb';
import {
    CloudFormationClient,
    DescribeStacksCommand,
    DescribeStacksCommandInput,
} from '@aws-sdk/client-cloudformation';

import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
const s3Client = new S3Client({ region: process.env.AWS_REGION });
const dynamodb = new DynamoDBClient({});
const ddbClient = DynamoDBDocumentClient.from(dynamodb);
const cfClient = new CloudFormationClient({ region: process.env.AWS_REGION });
import { v4 as uuidv4 } from 'uuid';

const timeOut = 15 * 1000; //15 seconds
let test_filename: string;
let unmodified_message: string;
let modified_message: string;
let sourceBucket: string | undefined;
let destinationBucket: string | undefined;
let dynamoDbTable: string | undefined;

function setUpTestData() {
    test_filename = uuidv4() + '.txt';
    unmodified_message = 'this message was created during an integration test';
    modified_message = 'THIS MESSAGE WAS CREATED DURING AN INTEGRATION TEST';
}

async function cleanUp() {
    console.log('Cleanup started for the test data created');
    const promises: Promise<any>[] = [];
    if (sourceBucket) promises.push(deleteObjectFromBucket(sourceBucket, test_filename));
    if (destinationBucket) promises.push(deleteObjectFromBucket(destinationBucket, test_filename));
    if (dynamoDbTable) promises.push(deleteItemFromTable(dynamoDbTable, test_filename));
    await Promise.all(promises);
}

const getObjectFromBucket = async (bucket: string, key: string): Promise<string | undefined> => {
    const getParams: GetObjectCommandInput = {
        Bucket: bucket,
        Key: key,
    };
    const getCommand = new GetObjectCommand(getParams);
    try {
        const { Body } = await s3Client.send(getCommand);
        return Body?.transformToString();
    } catch (err) {
        console.log(`${key} not found in bucket ${bucket}`);
        return;
    }
};

const deleteObjectFromBucket = async (bucket: string, key: string): Promise<DeleteObjectCommandOutput> => {
    const params: DeleteObjectCommandInput = {
        Bucket: bucket,
        Key: key,
    };
    const delCommand = new DeleteObjectCommand(params);
    try {
        return s3Client.send(delCommand);
    } catch (err) {
        console.log(`${key} not found in bucket ${bucket}`);
        throw err;
    }
};
const getItemFromTable = async (tableName, key): Promise<string | undefined> => {
    const input: GetItemCommandInput = {
        Key: {
            id: {
                S: key,
            },
        },
        TableName: tableName,
    };
    const command = new GetItemCommand(input);
    const result: GetItemCommandOutput = await ddbClient.send(command);
    console.log(result?.Item?.message?.S);
    return result?.Item?.message?.S;
};
const deleteItemFromTable = (tableName, key): Promise<DeleteItemCommandOutput> => {
    const input: DeleteItemCommandInput = {
        Key: {
            id: {
                S: key,
            },
        },
        TableName: tableName,
    };
    const command = new DeleteItemCommand(input);
    return ddbClient.send(command);
};
const putObjectInBucket = (
    bucket: string | undefined,
    key: string,
    data: string | undefined,
): Promise<PutObjectCommandOutput> => {
    const params: PutObjectCommandInput = {
        Bucket: bucket,
        Key: key,
        Body: data,
    };
    const getCommand = new PutObjectCommand(params);
    return s3Client.send(getCommand);
};

const getStackDetails = async (stackName: string) => {
    const input: DescribeStacksCommandInput = {
        StackName: stackName,
    };
    const command = new DescribeStacksCommand(input);
    const stackObj = await cfClient.send(command);
    sourceBucket = stackObj?.Stacks?.[0]?.Outputs?.find((item) => item.OutputKey === 'SourceBucketName')?.OutputValue;
    destinationBucket = stackObj?.Stacks?.[0]?.Outputs?.find(
        (item) => item.OutputKey === 'DestinationBucketName',
    )?.OutputValue;
    dynamoDbTable = stackObj?.Stacks?.[0]?.Outputs?.find(
        (item) => item.OutputKey === 'AsyncTransformTestResultsTable',
    )?.OutputValue;
    if (!sourceBucket || !destinationBucket) {
        throw new Error('Missing required resources');
    }
};

const pollDynamoDbTable = async (tableName, key): Promise<string> => {
    const validateFn = (result: string) => (result ? true : false);
    const result: string = await poll(() => getItemFromTable(tableName, key), validateFn, 5 * 1000, 3);
    console.log(result);
    return result;
};
const pollDestinationBucket = async (bucketName, key): Promise<string> => {
    const validateFn = (result: string | undefined) => (result ? true : false);
    const result: string = await poll(() => getObjectFromBucket(bucketName, key), validateFn, 5 * 1000, 3);
    console.log(result);
    return result;
};

const poll = async (fn, validate, interval, maxAttempts): Promise<any> => {
    let attempts = 0;
    const executePoll = async (resolve, reject) => {
        console.log('polling started - ', attempts);
        try {
            const result = await fn();
            console.log(result);
            attempts++;

            if (validate(result)) {
                return resolve(result);
            } else if (maxAttempts && attempts === maxAttempts) {
                return reject(new Error('Exceeded max attempts'));
            } else {
                setTimeout(executePoll, interval, resolve, reject);
            }
        } catch (err) {
            console.log('polling error - ', JSON.stringify(err));
            attempts++;
            setTimeout(executePoll, interval, resolve, reject);
        }
    };
    return new Promise(executePoll);
};

describe('Upload file to source S3 bucket', () => {
    beforeAll(() => {
        if (!process.env.AWS_SAM_STACK_NAME) {
            throw new Error('Missing required environment variable AWS_SAM_STACK_NAME');
        }
        setUpTestData();
    });

    afterAll(() => {
        cleanUp();
    });

    /**
     * Get stack resources from cloud formation using stack name used in SAM
     * Create a test file and upload it to source s3 bucket
     * If test resources were created, poll dynamo db table and match the expected result
     * Otherwise, poll destination bucket and read the tranformed object and match it with expected result
     */
    test(
        'System should transform the data to upper case and upload it to destination bucket',
        async () => {
            try {
                await getStackDetails(process.env.AWS_SAM_STACK_NAME);
                await putObjectInBucket(sourceBucket, test_filename, unmodified_message);
                console.log('put object success');
                let result;
                if (dynamoDbTable) {
                    result = await pollDynamoDbTable(dynamoDbTable, test_filename);
                    console.log('dynamo db polling done');
                } else {
                    result = await pollDestinationBucket(destinationBucket, test_filename);
                    console.log('bucket polling done');
                }
                expect(result).toEqual(modified_message);
            } catch (err) {
                console.log(err);
                throw err;
            }
        },
        timeOut,
    );
});

import { S3Event } from 'aws-lambda';
import {
    S3Client,
    GetObjectCommand,
    GetObjectCommandInput,
    PutObjectCommand,
    PutObjectCommandInput,
    PutObjectCommandOutput,
} from '@aws-sdk/client-s3';
const client = new S3Client({ region: process.env.AWS_REGION });

export const handler = async (event: S3Event): Promise<string> => {
    const sourceBucket = event.Records[0].s3.bucket.name;
    const key = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));
    const destinationBucket = process.env.DESTINATION_BUCKET;
    try {
        const data = await getObjectFromBucket(sourceBucket, key);
        console.log(`Successfully fetched object ${key} from bucket ${sourceBucket}`);
        await putObjectInBucket(destinationBucket, key, data?.toUpperCase());
        console.log(`Successfully put object ${key} in bucket ${destinationBucket}`);
        return `'Success'`;
    } catch (err) {
        console.log(err);
        const message = `Error prcocessing object ${key} from bucket ${sourceBucket} to bucket ${destinationBucket}. Make sure they exist and your buckets are in the same region as this function.`;
        console.log(message);
        throw new Error(message);
    }
};

const getObjectFromBucket = async (bucket: string, key: string): Promise<string | undefined> => {
    const params: GetObjectCommandInput = {
        Bucket: bucket,
        Key: key,
    };
    const getCommand = new GetObjectCommand(params);
    const { Body } = await client.send(getCommand);
    return Body?.transformToString();
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
    return client.send(getCommand);
};

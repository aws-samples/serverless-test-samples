package com.example.fixtures

import software.amazon.awssdk.services.s3.model.Bucket
import software.amazon.awssdk.services.s3.model.ListBucketsResponse

class BucketFixtures {
    public static final String TEST_BUCKET_NAME = "demo-bucket"

    static listWithBucket(String bucketName = TEST_BUCKET_NAME) {
        def bucket = makeBucket(TEST_BUCKET_NAME)

        return ListBucketsResponse.builder()
            .buckets(bucket)
            .build()
    }

    static Bucket makeBucket(String bucketName) {
        Bucket.builder()
            .name(bucketName)
            .build()
    }
}

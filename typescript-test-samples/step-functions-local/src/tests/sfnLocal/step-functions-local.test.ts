// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * step-functions-local.test.ts
 *
 * Unit tests for the lead generation Step Function locally.
 *
 */

/**
 * Import Modules
 *
 * Standard practice to put imports at the top of a module definition.
 */
import { beforeAll, beforeEach, afterAll, describe, it, expect, jest } from '@jest/globals';
import { GenericContainer, Wait, StartedTestContainer }  from 'testcontainers';
import { 
    SFNClient, 
    StartExecutionCommand, 
    StartExecutionCommandOutput, 
    CreateStateMachineCommand, 
    CreateStateMachineCommandOutput, 
    GetExecutionHistoryCommand, 
    HistoryEvent 
} from "@aws-sdk/client-sfn";
import { StepFunctionsConstants } from './step-functions-constants';

jest.setTimeout(10000);
// console.log(`constants: ${JSON.stringify(StepFunctionsConstants)}`);

/**
 * Unit Tests
 *
 * This is the set of unit tests focused on the list-buckets service, testing
 * the lambdaHandler function. We're using `describe` blocks to keep the tests
 * organized both in code and in test output. This also gives us a chance to run
 * subsets of tests easily.
 */

describe('lead-generation', () => {
    describe('step-function-local', () => {
        // let inputEvent: StepFunctionInputEvent;
        let container: StartedTestContainer;
        let sfnClient: SFNClient;
        let createStateMachineResponse: CreateStateMachineCommandOutput;
        let stateMachineArn: string;

        beforeAll(async () => {

            // Launch StepFunctionLocal with testcontainers
            container = await new GenericContainer('amazon/aws-stepfunctions-local')
                .withExposedPorts(8083)
                .withCopyFilesToContainer([{ 
                    source: StepFunctionsConstants.mockFileHostPath, 
                    target: StepFunctionsConstants.mockFileContainerPath
                  }])
                .withEnvironment({ SFN_MOCK_CONFIG: StepFunctionsConstants.mockFileContainerPath })
                .withDefaultLogDriver()
                // .withLogConsumer()
                .withWaitStrategy(Wait.forLogMessage("Starting server on port 8083"))
                .start();

            // setup Step Function client with test container URL
            const url = `http://${container.getHost()}:${container.getMappedPort(8083)}` ;

            try {
                sfnClient = new SFNClient({ 
                    endpoint: url
                });                

                // Important to avoid non-deterministic behavior
                await sleep(2);
            } catch (error) {
                console.log(`sfnClient error: ${error}`)
            }
            

            // create state machine
            try {
                createStateMachineResponse = await sfnClient.send(new CreateStateMachineCommand({
                    name: StepFunctionsConstants.STATE_MACHINE_NAME,
                    definition: StepFunctionsConstants.STATE_MACHINE_ASL,
                    roleArn: StepFunctionsConstants.DUMMY_ROLE
                }))
                stateMachineArn = createStateMachineResponse.stateMachineArn as string;
            } catch (error) {
                console.log(`stateMachine error: ${error}`)
            }
        });
        
        /**
         * Shared test setup
         *
         * We're using a `beforeEach` block that runs setup prior to each unit test
         * in this `describe` block. This lets us pull noise out of the test bodies
         * and ensures that setup is consistent.
         *
         */
        beforeEach(() => {

        });

        afterAll(async () => {
            // stop the SFN client
            await container.stop();
        });

        /**
         * Unit tests.
         *
         * Now we come to the unit tests themselves. Each test checks a single
         * scenario, with specific responses configured on the S3 client mock.
         *
         * The unit tests use the "Arrange, Act, Assert" pattern, setting up the
         * data (Arrange), executing the handler function (Act), then checking that
         * the result matches the inferface contract we expect (Assert).
         */

        // Check container is running
        it('Check Container is running', () => {
            expect(container.getId()).toBeDefined();
        })

        // Test Happy Path Scenario
        it('Test Happy Path Scenario', async () => {
            const executionName: string = "happyPathExecution";
            const executionResponse: StartExecutionCommandOutput = await sfnClient.send(new StartExecutionCommand({
                name: executionName,
                stateMachineArn: `${stateMachineArn}#HappyPathTest`,
                input: StepFunctionsConstants.EVENT_JSON_STRING
            }))
            
            expect(executionResponse.executionArn).not.toBeNull();
            
            // IMP: Wait until above execution completes in docker
            await sleep(2);

            const historyResponse = await sfnClient.send(new GetExecutionHistoryCommand({
                executionArn: executionResponse.executionArn
            }))

            const results = historyResponse.events?.filter((event) => {
                return ((event.type == "TaskStateExited") && (event.stateExitedEventDetails?.name == "CustomerAddedToFollowup"))
            })

            expect(results?.length).toBe(1);

        })

        // Test Negative Sentiment Scenario
        it('Test Negative Sentiment Scenario', async () => {
            const executionName: string = "negativeSentimentExecution";
            const executionResponse: StartExecutionCommandOutput = await sfnClient.send(new StartExecutionCommand({
                name: executionName,
                stateMachineArn: `${stateMachineArn}#NegativeSentimentTest`,
                input: StepFunctionsConstants.EVENT_JSON_STRING
            }))
            
            expect(executionResponse.executionArn).not.toBeNull();
            
            // IMP: Wait until above execution completes in docker
            await sleep(2);

            const historyResponse = await sfnClient.send(new GetExecutionHistoryCommand({
                executionArn: executionResponse.executionArn
            }))

            const results = historyResponse.events?.filter((event) => {
                return ((event.type == "TaskStateExited") && (event.stateExitedEventDetails?.name == "NegativeSentimentDetected"))
            })

            expect(results?.length).toBe(1);

        })

        // Test Retry on Service Exception
        it('Test Retry on Service Exception', async () => {
            const executionName: string = "retryExecution";
            const executionResponse: StartExecutionCommandOutput = await sfnClient.send(new StartExecutionCommand({
                name: executionName,
                stateMachineArn: `${stateMachineArn}#RetryOnServiceExceptionTest`,
                input: StepFunctionsConstants.EVENT_JSON_STRING
            }))
            
            expect(executionResponse.executionArn).not.toBeNull();
            
            // IMP: State Machine has retries with exponential backoff, therefore 4 seconds
            await sleep(4);

            const historyResponse = await sfnClient.send(new GetExecutionHistoryCommand({
                executionArn: executionResponse.executionArn
            }))

            const results: HistoryEvent[] | undefined = historyResponse.events?.filter((event) => {
                return (
                    (event.type == "TaskFailed") && (event.taskFailedEventDetails?.error == "InternalServerException")
                    || ((event.type == "TaskSucceeded") && (event.taskSucceededEventDetails?.resource == "comprehend:detectSentiment"))
                )
            });

            expect(results?.length).toBe(4);

            const firstThreeEventsAreInternalErrors = results?.slice(0,2).every(event => event?.taskFailedEventDetails?.error === "InternalServerException");
            expect(firstThreeEventsAreInternalErrors).toBeTruthy();

            const lastEvent = results ? results[3] as HistoryEvent : undefined;
            expect(lastEvent?.taskSucceededEventDetails?.resource).toBe("comprehend:detectSentiment");

        })


        
    });
});

function sleep(seconds) {
    return new Promise((resolve) => {
        setTimeout(() => { resolve('') }, seconds*1000)
    })
}
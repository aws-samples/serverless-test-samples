// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/**
 * step-functions-local.test.ts
 *
 * Unit tests for the lead generation Step Function leveraging the Step Functions Local docker image.
 *
 */

import { beforeAll, afterAll, describe, it, expect, jest } from '@jest/globals';
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

// Modify if default timeout isn't enough
// jest.setTimeout(10000);

/**
 * Unit Tests
 *
 * This is the set of unit tests focused on the lead generation system, testing
 * the step function state machine. 
 * 
 */

describe('lead-generation', () => {
    describe('step-function-local', () => {

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
                .withWaitStrategy(Wait.forLogMessage("Starting server on port 8083"))
                .start();

            // Set up Step Function client with test container URL
            sfnClient = new SFNClient({ 
                endpoint: `http://${container.getHost()}:${container.getMappedPort(8083)}`
            });                

            // Important to avoid non-deterministic behavior
            await sleep(2);         

            // Create state machine
            createStateMachineResponse = await sfnClient.send(new CreateStateMachineCommand({
                name: StepFunctionsConstants.STATE_MACHINE_NAME,
                definition: StepFunctionsConstants.STATE_MACHINE_ASL,
                roleArn: StepFunctionsConstants.DUMMY_ROLE
            }));

            stateMachineArn = createStateMachineResponse.stateMachineArn as string;

        });
        
        afterAll(async () => {
            // stop the SFN client
            await container.stop();
        });

        /**
         * Unit tests.
         *
         * Now we come to the unit tests themselves. Each test checks a single
         * scenario, with a new state machine execution.
         *
         */

        it('Check Container is running', () => {
            expect(container.getId()).toBeDefined();
        });

        it('Test Happy Path Scenario', async () => {
            const executionName: string = "happyPathExecution";
            const executionResponse: StartExecutionCommandOutput = await sfnClient.send(new StartExecutionCommand({
                name: executionName,
                stateMachineArn: `${stateMachineArn}#HappyPathTest`,
                input: StepFunctionsConstants.EVENT_JSON_STRING
            }));
            
            expect(executionResponse.executionArn).not.toBeNull();
            
            // IMP: Wait until above execution completes in docker
            await sleep(2);

            const historyResponse = await sfnClient.send(new GetExecutionHistoryCommand({
                executionArn: executionResponse.executionArn
            }));

            const results = historyResponse.events?.filter((event) => {
                return ((event.type == "TaskStateExited") && (event.stateExitedEventDetails?.name == "CustomerAddedToFollowup"))
            });

            expect(results?.length).toBe(1);

        });

        it('Test Negative Sentiment Scenario', async () => {
            const executionName: string = "negativeSentimentExecution";
            const executionResponse: StartExecutionCommandOutput = await sfnClient.send(new StartExecutionCommand({
                name: executionName,
                stateMachineArn: `${stateMachineArn}#NegativeSentimentTest`,
                input: StepFunctionsConstants.EVENT_JSON_STRING
            }));
            
            expect(executionResponse.executionArn).not.toBeNull();
            
            // IMP: Wait until above execution completes in docker
            await sleep(2);

            const historyResponse = await sfnClient.send(new GetExecutionHistoryCommand({
                executionArn: executionResponse.executionArn
            }));

            const results = historyResponse.events?.filter((event) => {
                return ((event.type == "TaskStateExited") && (event.stateExitedEventDetails?.name == "NegativeSentimentDetected"))
            });

            expect(results?.length).toBe(1);

        });

        it('Test Retry on Service Exception', async () => {
            const executionName: string = "retryExecution";
            const executionResponse: StartExecutionCommandOutput = await sfnClient.send(new StartExecutionCommand({
                name: executionName,
                stateMachineArn: `${stateMachineArn}#RetryOnServiceExceptionTest`,
                input: StepFunctionsConstants.EVENT_JSON_STRING
            }));
            
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

        });
    });
});

function sleep(seconds) {
    return new Promise((resolve) => {
        setTimeout(() => { resolve('') }, seconds*1000)
    })
}
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
    GetExecutionHistoryCommandOutput, 
    HistoryEvent 
} from "@aws-sdk/client-sfn";
import { StepFunctionsConstants } from './step-functions-constants';

// Modify if default timeout isn't enough
jest.setTimeout(20000);

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
        let stateMachineArn: string;

        beforeAll(async () => {
            ({ container, sfnClient, stateMachineArn } = await setupStepFunctionsLocal());
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

            const historyResponse: GetExecutionHistoryCommandOutput = await manageExecution(sfnClient, stateMachineArn, "happyPathExecution", "HappyPathTest");
            expect(historyResponse).toBeDefined();

            const results = historyResponse.events?.filter((event) => {
                return ((event.type == "TaskStateExited") && (event.stateExitedEventDetails?.name == "CustomerAddedToFollowup"))
            });
            expect(results?.length).toBe(1);

        });

        it('Test Negative Sentiment Scenario', async () => {

            const historyResponse: GetExecutionHistoryCommandOutput = await manageExecution(sfnClient, stateMachineArn, "negativeSentimentExecution", "NegativeSentimentTest");
            expect(historyResponse).toBeDefined();

            const results = historyResponse.events?.filter((event) => {
                return ((event.type == "TaskStateExited") && (event.stateExitedEventDetails?.name == "NegativeSentimentDetected"))
            });

            expect(results?.length).toBe(1);

        });

        it('Test Retry on Service Exception', async () => {

            const historyResponse: GetExecutionHistoryCommandOutput = await manageExecution(sfnClient, stateMachineArn, "retryExecution", "RetryOnServiceExceptionTest");
            expect(historyResponse).toBeDefined();

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

async function setupStepFunctionsLocal() {

    // Launch StepFunctionLocal with testcontainers
    const container: StartedTestContainer = await createTestContainer();       

    // Set up Step Function client with test container URL
    const sfnClient: SFNClient = new SFNClient({ 
        endpoint: `http://${container.getHost()}:${container.getMappedPort(8083)}`
    });                

    // Create state machine
    const createStateMachineResponse: CreateStateMachineCommandOutput = await sfnClient.send(new CreateStateMachineCommand({
        name: StepFunctionsConstants.STATE_MACHINE_NAME,
        definition: StepFunctionsConstants.STATE_MACHINE_ASL,
        roleArn: StepFunctionsConstants.DUMMY_ROLE
    }));

    const stateMachineArn: string = createStateMachineResponse.stateMachineArn as string;

    return { container, sfnClient, stateMachineArn }

}

async function createTestContainer(): Promise<StartedTestContainer> {

    const container: StartedTestContainer = await new GenericContainer('amazon/aws-stepfunctions-local')
    .withExposedPorts(8083)
    .withCopyFilesToContainer([{ 
        source: StepFunctionsConstants.mockFileHostPath, 
        target: StepFunctionsConstants.mockFileContainerPath
      }])
    .withEnvironment({ SFN_MOCK_CONFIG: StepFunctionsConstants.mockFileContainerPath })
    .withDefaultLogDriver()
    .withWaitStrategy(Wait.forLogMessage("Starting server on port 8083"))
    .start();

    // Important to avoid non-deterministic behavior, waiting for container to spin up
    await sleep(2000);

    return container;

}

async function manageExecution(sfnClient: SFNClient, stateMachineArn: string, executionName: string, test: string): Promise<GetExecutionHistoryCommandOutput> {

    const executionResponse = await sfnClient.send(new StartExecutionCommand({
        name: executionName,
        stateMachineArn: `${stateMachineArn}#${test}`,
        input: StepFunctionsConstants.EVENT_JSON_STRING
    }));

    return await untilExecutionCompletes(sfnClient, executionResponse);
}

async function untilExecutionCompletes(sfnClient: SFNClient, executionResponse: StartExecutionCommandOutput): Promise<GetExecutionHistoryCommandOutput> {

    let historyResponse: GetExecutionHistoryCommandOutput;

    do {
        // IMP: allow some time for the execution to complete in docker
        await sleep(1000);

        historyResponse = await sfnClient.send(new GetExecutionHistoryCommand({
            executionArn: executionResponse.executionArn
        }));

    // cycle back if not yet completed
    } while (!executionSucceeded(historyResponse));

    return historyResponse;
}

function executionSucceeded(historyResponse: any): boolean {
    const succeeded = historyResponse.events.filter(event => event.type == 'ExecutionSucceeded');
    return succeeded.length == 1;
}

function sleep(milliseconds: number) {
    return new Promise((resolve) => {
        setTimeout(() => { resolve('') }, milliseconds)
    })
}


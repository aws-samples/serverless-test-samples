package com.amazon.aws.sample.lambda;


import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.SQSEvent;
import com.amazonaws.services.stepfunctions.AWSStepFunctions;
import com.amazonaws.services.stepfunctions.AWSStepFunctionsClientBuilder;
import com.amazonaws.services.stepfunctions.model.StartExecutionRequest;
import com.amazonaws.services.stepfunctions.model.StartExecutionResult;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.UUID;

public class SqsLambdaStepFunctionHandler implements RequestHandler<SQSEvent, StartExecutionResult> {
    private static final AWSStepFunctions client = AWSStepFunctionsClientBuilder.defaultClient();

    /**
     * @param
     * @return: Reads properties from config.
     */
    public String getProperties() {
        Properties prop = null;
        try (InputStream input = SqsLambdaStepFunctionHandler.class.getClassLoader().getResourceAsStream("config.properties")) {
            prop = new Properties();

            if (input == null) {
                System.out.println("Sorry, unable to find config.properties");
                return "";
            }
            //load a properties file from class path, inside static method
            prop.load(input);

            //get the property value and print it out
            System.out.println(prop.getProperty("cloud.aws.statemachine.arn"));
        } catch (IOException ex) {
            ex.printStackTrace();
        }
        return prop.getProperty("cloud.aws.statemachine.arn");
    }

    /**
     * @param event, context
     * @return: Starts step function
     */
    public StartExecutionResult handleRequest(SQSEvent event, Context context)  {
        String transactionId = UUID.randomUUID().toString();

        StartExecutionRequest request = null;
        for(SQSEvent.SQSMessage msg : event.getRecords()) {
            if (msg != null) {
                System.out.println(new String(msg.getBody()));
                request = new StartExecutionRequest()
                        .withStateMachineArn(getProperties())
                .withInput(msg.getBody());
            }
        }

        StartExecutionResult result = client.startExecution(request);

        return result;
    }
}

/**
 * Integration Tests
 * Before running this we would deploy the stack 
 * 
*/

import axios from "axios";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
    PutCommand,
    DynamoDBDocumentClient,
    QueryCommand,
    DeleteCommand
} from "@aws-sdk/lib-dynamodb";
import {v4 as uuidv4} from 'uuid';


let dynamoDBTableName : string;
let validId = 'TEST001_'+uuidv4();
let invalidId = 'TEST002_'+uuidv4();

const dynamodb = new DynamoDBClient({});
const ddb = DynamoDBDocumentClient.from(dynamodb);

async function setUpIds(){
    const param = { Item: {'PK': validId,'SK': 'NAME#'}, TableName: dynamoDBTableName};
    const result = await ddb.send(new PutCommand(param));
}

async function cleanUp(){
    let ids = [invalidId,validId];
    for (var id of ids){
        // Scan and get Items
        const params = {
                KeyConditionExpression: "#PK = :PK ",
                ExpressionAttributeNames: {"#PK": "PK"},
                ExpressionAttributeValues: {":PK": id},
                TableName: process.env.DYNAMODB_TABLE_NAME
            };
                          
        let items = await ddb.send(new QueryCommand(params));
        for(var item of items.Items){
            let deleteParam = {Key: {'PK': item.PK, 'SK':item.SK}, TableName: dynamoDBTableName};
            await ddb.send(new DeleteCommand(deleteParam));
        }
    }
}

describe('API Integration tests', () => {
    /**
     * Shared test setup
     *
     * In this case, we're using a beforeAll block to pull configuration from
     * our environment. These tests need a base URL to make HTTP requests against and DynamoDB table name to populate the database.
     * We don't want to commit this URL into our source code beacuse it may change
     * as we develop code, and between different environments like QA and Production.
     */
    let baseApiUrl: string;
    

    beforeAll( () => {
        if (process.env.API_URL) {
            baseApiUrl = process.env.API_URL;
            // Seed initial data
        } else {
            throw new Error('API_URL environment variable is not set');
        }
        if (process.env.DYNAMODB_TABLE_NAME) {
            dynamoDBTableName = process.env.DYNAMODB_TABLE_NAME;
            // Seed initial data
        } else {
            throw new Error('DYNAMODB_TABLE_NAME environment variable is not set');
        }
        // Add an entry in database and use that id for GET API
        setUpIds();    
    });

    afterAll(() =>{
       cleanUp();
    })
    
    /**
     * Calling the URL with a invalid id (not present in db)
     * This should return a 404
    */
    describe('GET /hello/{invalidId}', () => {   
        it('should return not found code for http get', async () => {
            // Check in database that the ID does not exist
            const url = `${baseApiUrl}/hello/${invalidId}`;
            let response = null;
            try{
                response = await axios.get(url);
            }catch(err){
                expect(err.message).toBe("Request failed with status code 404");
                expect(err.response.status).toBe(404);
            }            
        });
    });

    /**
     * Calling the URL with a valid id.
     * Note have an entry in the database with id 1. 
     * If the entry is not there the test case would fail for the first time.
     */
    describe('GET /hello/{id}', () => {
        it('should return success code for http get', async () => {
            const response = await axios.get(`${baseApiUrl}/hello/${validId}`);
            expect(response.status).toBe(200);
        });
    });
});
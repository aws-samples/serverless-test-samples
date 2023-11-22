import { APIGatewayProxyEvent } from 'aws-lambda';
import axios from 'axios';

export const lambdaHandler = async (event: APIGatewayProxyEvent) => {
    // Getting the weather api from environment variable
    const weatherApi = process.env.WEATHER_API;

    const city = event.pathParameters.city;

    try {
        const { status: statusCode, data: weatherResponse } = await axios.get(`${weatherApi}/${city}`);

        return {
            statusCode,
            body: JSON.stringify(weatherResponse),
        };
    } catch (err: unknown) {
        console.error(err);
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: err instanceof Error ? err.message : 'Oh no! Something went wrong!',
            }),
        };
    }
};

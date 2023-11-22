import { lambdaHandler } from '../../app';
import { eventJSON } from '../../events/event-data';
import axios from 'axios';

jest.mock('axios');

afterEach(() => {
    jest.clearAllMocks();
});

describe('Unit test for app handler', function () {
    it('verify happy path 200', async () => {
        process.env.WEATHER_API = 'https://www.test.com/';

        const mockResponse = {
            temperature: '+8 °C',
            wind: '15 km/h',
            description: 'Partly cloudy',
            forecast: [
                { day: '1', temperature: '+7 °C', wind: '25 km/h' },
                { day: '2', temperature: '7 °C', wind: '13 km/h' },
                { day: '3', temperature: ' °C', wind: '25 km/h' },
            ],
        };

        (axios.get as jest.Mock).mockResolvedValue({ status: 200, data: mockResponse });
        const result = await lambdaHandler(eventJSON);
        expect(result.statusCode).toEqual(200);
        expect(result.body).toEqual(JSON.stringify(mockResponse));
    });

    it('verify incorrect city', async () => {
        process.env.WEATHER_API = 'https://www.test.com/';

        const mockResponse = {
            message: 'NOT_FOUND',
        };

        (axios.get as jest.Mock).mockResolvedValue({ status: 404, data: mockResponse });
        const result = await lambdaHandler(eventJSON);
        expect(result.statusCode).toEqual(404);
        expect(result.body).toEqual(JSON.stringify(mockResponse));
    });

    it('verify error thrown', async () => {
        process.env.WEATHER_API = 'https://www.test.com/';

        (axios.get as jest.Mock).mockImplementationOnce(() => Promise.reject(new Error('Oops!')));

        const result = await lambdaHandler(eventJSON);
        expect(result.statusCode).toEqual(500);
        expect(result.body).toEqual(JSON.stringify({ message: 'Oops!' }));
    });
});

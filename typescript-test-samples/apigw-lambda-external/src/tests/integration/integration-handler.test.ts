/**
 * Integration Tests
 * Before running this we would deploy the stack as Volatile
 *
 */

import axios from 'axios';

const validCity = 'London';
const invalidCity = 'Springfield';

describe('API Integration tests', () => {
    let baseApiUrl: string;

    beforeAll(() => {
        if (process.env.API_URL) {
            baseApiUrl = process.env.API_URL;
        } else {
            throw new Error('API_URL environment variable is not set');
        }
    });

    /**
     * Calling the URL with a invalid city
     * This should return a 404
     */
    describe('GET /{invalidCity}', () => {
        it('should return not found code for http get', async () => {
            const url = `${baseApiUrl}/${invalidCity}`;
            try {
                await axios.get(url);
            } catch (err) {
                expect(err.message).toBe('Request failed with status code 404');
                expect(err.response.status).toBe(404);
            }
        });
    });

    /**
     * Calling the URL with a valid city.
     */
    describe('GET /{id}', () => {
        it('should return success code for http get', async () => {
            const response = await axios.get(`${baseApiUrl}/${validCity}`);
            expect(response.status).toBe(200);
        });
    });
});

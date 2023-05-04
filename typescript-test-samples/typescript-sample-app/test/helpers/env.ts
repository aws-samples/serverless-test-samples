import { beforeAll, afterAll } from '@jest/globals';

/* Fake environment variables by temporarily setting them before all tests and then resetting them
after all tests to avoid unwanted side-effects in the production code. */

let env: any;

beforeAll(() => {
  env = process.env;
  process.env = { ...env };
});

afterAll(() => {
  process.env = env;
});

export const mockVariable = (name: string, value: any) => {
  process.env[name] = value;
};

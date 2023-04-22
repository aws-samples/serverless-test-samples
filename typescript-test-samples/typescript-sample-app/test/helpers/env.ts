import { beforeAll, afterAll } from '@jest/globals';

let env: any;

beforeAll(() => {
  jest.resetModules();
  env = process.env;
  process.env = { ...env };
});

afterAll(() => {
  process.env = env;
});

export const mockVariable = (name: string, value: any) => {
  process.env[name] = value;
};

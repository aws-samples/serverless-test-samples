/*
 * For a detailed explanation regarding each configuration property and type check, visit:
 * https://jestjs.io/docs/configuration
 */

export default {
    testEnvironment: 'node',
    roots: ['<rootDir>','<rootDir>/test'],
    testMatch: ['**/test/**/*.test.ts'],
    transform: {
      '^.+\\.tsx?$': 'ts-jest'
    },

    projects: ["<rootDir>/jest.integration.config.ts","<rootDir>/jest.unit.config.ts"],

    clearMocks: true,
    collectCoverage: true,
    coverageDirectory: 'coverage',
    coverageProvider: 'v8',
    verbose: true,
};


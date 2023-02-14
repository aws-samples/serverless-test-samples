/*
 * For a detailed explanation regarding each configuration property and type check, visit:
 * https://jestjs.io/docs/configuration
 */

export default {
    projects: ["<rootDir>/jest.integration.config.ts","<rootDir>/jest.unit.config.ts"],
    transform: {
        '^.+\\.ts?$': 'esbuild-jest',
    },
    clearMocks: true,
    collectCoverage: true,
    coverageDirectory: 'coverage',
    coverageProvider: 'v8',
    verbose: true,
    testMatch: ['**/tests/**/*.test.ts']
};


module.exports = {
    displayName: "integration",
    testMatch: ['**/test/integration/**/*.test.ts'],
    transform: {
        '^.+\\.ts?$': 'ts-jest',
    },
};
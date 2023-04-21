module.exports = {
    displayName: "unit",
    testMatch: ['**/test/unit/**/*.test.ts'],
    transform: {
        '^.+\\.ts?$': 'ts-jest',
    },
};
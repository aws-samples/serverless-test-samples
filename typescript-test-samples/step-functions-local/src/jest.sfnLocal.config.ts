module.exports = {
    displayName: 'unit',
    testMatch: ['**/tests/sfnLocal/*.test.ts'],
    transform: {
        '^.+\\.ts?$': 'esbuild-jest',
    },
};

module.exports = {
    displayName: 'unit',
    testMatch: ['**/tests/unit/*.test.ts'],
    transform: {
        '^.+\\.ts?$': 'esbuild-jest',
    },
};

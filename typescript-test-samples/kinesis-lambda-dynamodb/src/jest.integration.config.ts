module.exports = {
  displayName: "integration",
  testMatch: ['**/tests/integration/*.test.ts'],
  transform: {
      '^.+\\.ts?$': 'esbuild-jest',
  },
};
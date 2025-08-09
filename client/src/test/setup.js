import '@testing-library/jest-dom'

// Polyfill fetch for tests if needed
if (!globalThis.fetch) {
  globalThis.fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args))
}

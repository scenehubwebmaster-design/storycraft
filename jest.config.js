/**
 * Jest configuration
 * - Ignore local SQLite DB files from watch mode (anchored to rootDir)
 * - Disable watchman to force NodeWatcher behavior that respects watchPathIgnorePatterns
 *   more consistently on some Windows setups.
 */
module.exports = {
  // Some environments may have trouble with watchman; turning it off can avoid
  // spurious watcher errors on Windows (EPERM while lstat-ing DB journal files).
  watchman: false,

  // Ignore the SQLite DB and its journal/wal files. Anchor to <rootDir> to make
  // the pattern deterministic regardless of current working directory.
  watchPathIgnorePatterns: [
    "<rootDir>/storycraft\\.db$",
    "<rootDir>/storycraft\\.db-journal$",
    "<rootDir>/storycraft\\.db-wal$",
    // also ignore common noisy folders
    "<rootDir>/node_modules/",
    "<rootDir>/.git/",
  ],

  // Do not run tests that belong to the frontend workspace (Vitest) or
  // Playwright; the frontend uses Vitest and Playwright has its own runner.
  testPathIgnorePatterns: [
    "<rootDir>/frontend/",
    "<rootDir>/scripts/.*playwright.*\\.spec\\.(js|ts|jsx|tsx)$",
    "<rootDir>/scripts/.*\\.spec\\.(js|ts|jsx|tsx)$",
  ],
  // When the root workspace legitimately has no tests, exit with success
  // so the editor integration doesn't treat that as a failure.
  passWithNoTests: true,

  // Do not force a testEnvironment here: the frontend workspace has its own
  // dependencies (jsdom) and runner; leaving this unset avoids requiring
  // additional root-level packages.
};

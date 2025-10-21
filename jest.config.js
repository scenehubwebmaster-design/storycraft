/**
 * Jest configuration to ignore local SQLite DB files from watch mode.
 */
module.exports = {
  watchPathIgnorePatterns: [
    "storycraft\\.db$",
    "storycraft\\.db-journal$",
    "storycraft\\.db-wal$",
  ],
};

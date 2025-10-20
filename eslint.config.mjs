import { dirname, resolve } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// If ESLint is invoked from the frontend workspace, return an empty flat
// config so the frontend's classic `.eslintrc.cjs` can be used instead.
const cwd = process.cwd();
const frontendPath = resolve(__dirname, "frontend");

// Determine config at runtime; export a single default value.
const eslintConfig = cwd.startsWith(frontendPath)
  ? [{}]
  : [
      {
        languageOptions: {
          parserOptions: {
            ecmaVersion: 2022,
            sourceType: "module",
            ecmaFeatures: { jsx: true },
          },
        },
        ignores: [
          "node_modules/**",
          ".next/**",
          "out/**",
          "build/**",
          "next-env.d.ts",
        ],
      },
    ];

export default eslintConfig;

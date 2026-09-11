import tnaEslintConfig from "@nationalarchives/eslint-config";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    ignores: [
      "dist/",
      "build/",
      "coverage/",
      "storybook-static/",
      "storybook/stories/",
      "configs/pa11y_ci_precommit.js",
      "accessibility_tests/**",
      "configs/**",
      "lighthouserc.js",
    ],
  },
  ...tnaEslintConfig,
  {
    files: [".storybook/**/*.js", "accessibility_tests/**/*.js", "*.js"],
    languageOptions: {
      globals: {
        module: "readonly",
        require: "readonly",
        process: "readonly",
        __dirname: "readonly",
      },
    },
  },
  {
    files: ["**/*.test.js", "**/*.test-helpers.js"],
    languageOptions: {
      globals: {
        require: "readonly",
        module: "readonly",
        global: "writable",
        describe: "readonly",
        it: "readonly",
        test: "readonly",
        expect: "readonly",
        jest: "readonly",
        beforeEach: "readonly",
        afterEach: "readonly",
        beforeAll: "readonly",
        afterAll: "readonly",
      },
    },
    rules: {
      "id-length": ["error", { properties: "never" }],
    },
  },
]);

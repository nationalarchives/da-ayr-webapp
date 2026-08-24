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
      "app/static/init.uv.test.js",
      "configs/pa11y_ci_precommit.js",
      "app/static/init.uv.js",
      "accessibility_tests/**",
      "configs/**",
      "lighthouserc.js",
      "app/static/init.uv*.js",
    ],
  },
  ...tnaEslintConfig,
  {
    // Override rules for CommonJS / configuration / script files / story files
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
]);

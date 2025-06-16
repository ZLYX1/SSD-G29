// ESLint core and configuration.
import {defineConfig} from "eslint/config";

// Built-in ESLint language plugins.
import js from "@eslint/js";
import json from "@eslint/json";
import markdown from "@eslint/markdown";
import css from "@eslint/css";

// External plugins
import security from "eslint-plugin-security";
import noUnsanitized from "eslint-plugin-no-unsanitized"
import html from "eslint-plugin-html"

// Global variables (browser, node, etc.)
import globals from "globals";

const commonParserOptions = {
    ecmaVersion: 2021,
    sourceType: "module",
}
const commonGlobals = globals.browser

export default defineConfig([
        // Ignore override applies globally with no files/globs specified
        {
            ignores: ["certbot/"],
        },
        {
            files: ["**/*.{js,mjs,cjs}"],
            plugins: {
                security,
                "no-unsanitized": noUnsanitized,
            },
            rules: {
                ...js.configs.recommended.rules,
                ...security.configs.recommended.rules,
                ...noUnsanitized.configs.recommended.rules,
                "security/detect-eval-with-expression": "error",
            },
            languageOptions: {
                parserOptions: commonParserOptions,
                globals: commonGlobals,
            },
        },
        {
            files: ["**/*.json"],
            plugins: {json},
            language: "json/json",
            extends: ["json/recommended"]
        },
        {
            files: ["**/*.md"],
            plugins: {markdown},
            language: "markdown/gfm",
            extends: ["markdown/recommended"]
        },
        {
            files: ["**/*.css"],
            plugins: {css},
            language: "css/css",
            extends: ["css/recommended"]
        },
        {
            files: ["**/*.html"],
            plugins: {html},
            languageOptions: {
                parserOptions: commonParserOptions,
                globals: commonGlobals,
            },
            settings: {},
            rules: {},
        },
    ],
);

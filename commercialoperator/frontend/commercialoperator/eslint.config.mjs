import globals from 'globals';
import jsLint from '@eslint/js';
import pluginVue from 'eslint-plugin-vue';
import vueEslintParser from 'vue-eslint-parser';
import pluginPrettierRecommended from 'eslint-plugin-prettier/recommended';
import eslintConfigPrettier from 'eslint-config-prettier';

const projectGlobals = {
    ...globals.browser,
    ...globals.node,
    ...globals.jquery,
    es6: true,
    moment: true,
    swal: true,
    bootstrap: true,
    env: true,
    _: true, // Lodash
};

export default [
    jsLint.configs.recommended,
    pluginPrettierRecommended,
    ...pluginVue.configs['flat/vue2-recommended'],
    eslintConfigPrettier,
    {
        ignores: ['node_modules/', 'build/*.js', 'config/*.js'],
    },
    {
        files: ['**/*.{js,mjs,cjs,ts,mts,jsx,tsx}'],
        languageOptions: {
            parserOptions: {
                sourceType: 'module',
            },
            globals: projectGlobals,
        },
    },
    {
        files: ['src/**/*.vue'],
        plugins: {
            vue: pluginVue,
        },
        languageOptions: {
            sourceType: 'module',
            ecmaVersion: 11,
            parser: vueEslintParser,
            parserOptions: {
                sourceType: 'module',
                ecmaVersion: 11,
            },
            globals: projectGlobals,
        },
        rules: {
            'prettier/prettier': 'error',
        },
    },
];

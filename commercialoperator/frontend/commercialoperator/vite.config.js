import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import svgLoader from 'vite-svg-loader';
import { viteStaticCopy } from 'vite-plugin-static-copy';

const applicationNameShort = 'commercialoperator';
const port = process.env.PORT ? parseInt(process.env.PORT) : 5173;
const host = process.env.HOST || '0.0.0.0';

export default defineConfig({
    base: `/static/${applicationNameShort}_vue/`,
    server: {
        host: host,
        port: port,
        strictPort: true,
        open: false,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers':
                'Origin, X-Requested-With, Content-Type, Accept',
        },
        hmr: {
            protocol: 'ws',
            host: 'localhost', // You can use host if not using a dev container
            port: port,
        },
    },
    plugins: [
        vue(),
        svgLoader({
            defaultImport: 'url',
        }),
        viteStaticCopy({
            // Had to do this to get the relative paths to work
            // Probably a better way but I couldn't figure it out
            targets: [
                {
                    src: 'node_modules/@fortawesome/fontawesome-free/webfonts',
                    dest: 'node_modules/@fortawesome/fontawesome-free/',
                },
            ],
        }),
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
            '@common-utils': path.resolve(__dirname, 'src/components/common/'),
            '@assets': path.resolve(__dirname, 'src/assets'),
            vue: '@vue/compat',
        },
    },
    build: {
        manifest: 'manifest.json',
        commonjsOptions: { transformMixedEsModules: true },
        root: path.resolve(__dirname, './src'),
        outDir: path.resolve(
            __dirname,
            `../../static/${applicationNameShort}_vue`
        ),
        sourcemap: false,
        rollupOptions: {
            input: {
                main: path.resolve(__dirname, 'src/main.js'),
            },
        },
        exclude: ['jquery', 'bootstrap'],
        emptyOutDir: true,
    },
});

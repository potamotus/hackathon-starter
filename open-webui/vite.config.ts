import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
	plugins: [
		sveltekit(),
		viteStaticCopy({
			targets: [
				{
					src: 'node_modules/onnxruntime-web/dist/*.jsep.*',

					dest: 'wasm'
				}
			]
		})
	],
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
	},
	build: {
		// В Docker меньше RAM/диска: DISABLE_SVELTE_SOURCEMAP=1 (см. Dockerfile стадия build).
		sourcemap: process.env.DISABLE_SVELTE_SOURCEMAP === '1' ? false : true,
		// На машинах с малым лимитом памяти Docker: VITE_LOW_MEM_BUILD=1 снижает пик RAM при rollup.
		rollupOptions:
			process.env.VITE_LOW_MEM_BUILD === '1'
				? { maxParallelFileOps: 1 }
				: {}
	},
	worker: {
		format: 'es'
	},
	esbuild: {
		pure: process.env.ENV === 'dev' ? [] : ['console.log', 'console.debug', 'console.error']
	}
});

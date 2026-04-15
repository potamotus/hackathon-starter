<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { CT_API_BASE_URL } from '$lib/constants';

	let terminalEl: HTMLDivElement;
	let statusText = 'connecting...';
	let statusClass = '';

	let term: any;
	let ws: WebSocket | null = null;
	let fitAddon: any;

	onMount(async () => {
		const { Terminal } = await import('@xterm/xterm');
		const { FitAddon } = await import('@xterm/addon-fit');
		const { WebLinksAddon } = await import('@xterm/addon-web-links');

		// @ts-ignore - CSS import for xterm
		await import('@xterm/xterm/css/xterm.css');

		term = new Terminal({
			cursorBlink: true,
			fontSize: 14,
			fontFamily: '"JetBrains Mono", "Fira Code", "SF Mono", Menlo, monospace',
			theme: {
				background: '#0f172a',
				foreground: '#e2e8f0',
				cursor: '#ff002d',
				selectionBackground: '#334155',
				black: '#1e293b',
				red: '#ff002d',
				green: '#22c55e',
				yellow: '#eab308',
				blue: '#3b82f6',
				magenta: '#a855f7',
				cyan: '#06b6d4',
				white: '#e2e8f0',
				brightBlack: '#475569',
				brightRed: '#ff4d6a',
				brightGreen: '#4ade80',
				brightYellow: '#facc15',
				brightBlue: '#60a5fa',
				brightMagenta: '#c084fc',
				brightCyan: '#22d3ee',
				brightWhite: '#f8fafc'
			}
		});

		fitAddon = new FitAddon();
		term.loadAddon(fitAddon);
		term.loadAddon(new WebLinksAddon());
		term.open(terminalEl);
		fitAddon.fit();

		// WebSocket connection to CT API
		const proto = CT_API_BASE_URL.startsWith('https') ? 'wss:' : 'ws:';
		const host = CT_API_BASE_URL.replace(/^https?:\/\//, '');
		ws = new WebSocket(`${proto}//${host}/ws/terminal?session=gpthub`);

		ws.onopen = () => {
			statusText = 'connected';
			statusClass = 'connected';
			sendResize(term.cols, term.rows);
			term.focus();
		};

		ws.onmessage = (e: MessageEvent) => {
			term.write(e.data);
		};

		ws.onclose = () => {
			statusText = 'disconnected';
			statusClass = 'error';
			term.write('\r\n\x1b[31m[session ended]\x1b[0m\r\n');
		};

		ws.onerror = () => {
			statusText = 'error';
			statusClass = 'error';
		};

		term.onData((data: string) => {
			if (ws?.readyState === WebSocket.OPEN) {
				ws.send(data);
			}
		});

		term.onResize(({ cols, rows }: { cols: number; rows: number }) => sendResize(cols, rows));

		const onResize = () => fitAddon.fit();
		window.addEventListener('resize', onResize);

		setTimeout(() => fitAddon.fit(), 100);

		return () => {
			window.removeEventListener('resize', onResize);
		};
	});

	onDestroy(() => {
		if (ws) {
			ws.close();
			ws = null;
		}
		if (term) {
			term.dispose();
		}
	});

	function sendResize(cols: number, rows: number) {
		if (ws?.readyState === WebSocket.OPEN) {
			const buf = new ArrayBuffer(5);
			const view = new DataView(buf);
			view.setUint8(0, 0x72); // 'r'
			view.setUint16(1, cols);
			view.setUint16(3, rows);
			ws.send(buf);
		}
	}
</script>

<div class="terminal-wrapper">
	<div class="terminal-status {statusClass}">{statusText}</div>
	<div class="terminal-container" bind:this={terminalEl}></div>
</div>

<style>
	.terminal-wrapper {
		width: 100%;
		height: 100%;
		background: #0f172a;
		position: relative;
	}

	.terminal-status {
		position: absolute;
		top: 8px;
		right: 12px;
		font: 12px system-ui;
		color: #64748b;
		z-index: 10;
	}

	.terminal-status.connected {
		color: #22c55e;
	}

	.terminal-status.error {
		color: #ef4444;
	}

	.terminal-container {
		width: 100%;
		height: 100%;
	}
</style>

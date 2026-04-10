import { WebSocketServer, WebSocket } from 'ws'
import * as Y from 'yjs'

// Store documents in memory (use Redis/DB for production)
const documents = new Map<string, Y.Doc>()
const connections = new Map<string, Set<WebSocket>>()

export function setupYjsServer(wss: WebSocketServer) {
  wss.on('connection', (ws: WebSocket, req) => {
    // Extract document ID from URL query
    const url = new URL(req.url || '', 'http://localhost')
    const docId = url.searchParams.get('doc') || 'default'

    console.log(`Client connected to document: ${docId}`)

    // Get or create document
    let doc = documents.get(docId)
    if (!doc) {
      doc = new Y.Doc()
      documents.set(docId, doc)
    }

    // Track connection
    if (!connections.has(docId)) {
      connections.set(docId, new Set())
    }
    connections.get(docId)!.add(ws)

    // Send initial state
    const state = Y.encodeStateAsUpdate(doc)
    ws.send(JSON.stringify({ type: 'sync', data: Array.from(state) }))

    // Handle incoming messages
    ws.on('message', (message: Buffer) => {
      try {
        const parsed = JSON.parse(message.toString())

        if (parsed.type === 'update') {
          const update = new Uint8Array(parsed.data)
          Y.applyUpdate(doc!, update)

          // Broadcast to other clients
          const docConnections = connections.get(docId)
          docConnections?.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({ type: 'update', data: parsed.data }))
            }
          })
        }

        if (parsed.type === 'awareness') {
          // Broadcast awareness (cursor positions, etc.)
          const docConnections = connections.get(docId)
          docConnections?.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({ type: 'awareness', data: parsed.data }))
            }
          })
        }
      } catch (err) {
        console.error('Error processing message:', err)
      }
    })

    // Handle disconnect
    ws.on('close', () => {
      console.log(`Client disconnected from document: ${docId}`)
      connections.get(docId)?.delete(ws)

      // Clean up empty document
      if (connections.get(docId)?.size === 0) {
        // Keep document in memory for a while before cleanup
        setTimeout(() => {
          if (connections.get(docId)?.size === 0) {
            connections.delete(docId)
            // Optionally persist document before deletion
          }
        }, 60000) // 1 minute
      }
    })

    ws.on('error', (err) => {
      console.error('WebSocket error:', err)
    })
  })

  console.log('Yjs WebSocket server initialized')
}

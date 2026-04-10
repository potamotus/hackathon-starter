import { WebSocketServer, WebSocket } from 'ws'
import * as Y from 'yjs'
import * as syncProtocol from 'y-protocols/sync'
import * as awarenessProtocol from 'y-protocols/awareness'
import * as encoding from 'lib0/encoding'
import * as decoding from 'lib0/decoding'

const messageSync = 0
const messageAwareness = 1

// Store documents in memory (use Redis/DB for production)
const documents = new Map<string, { doc: Y.Doc; awareness: awarenessProtocol.Awareness }>()
const connections = new Map<string, Map<WebSocket, { clientId: number }>>()

function getYDoc(docName: string): { doc: Y.Doc; awareness: awarenessProtocol.Awareness } {
  let docData = documents.get(docName)
  if (!docData) {
    const doc = new Y.Doc()
    const awareness = new awarenessProtocol.Awareness(doc)
    docData = { doc, awareness }
    documents.set(docName, docData)

    // Broadcast awareness changes
    awareness.on('update', ({ added, updated, removed }: { added: number[], updated: number[], removed: number[] }) => {
      const changedClients = added.concat(updated).concat(removed)
      const encoder = encoding.createEncoder()
      encoding.writeVarUint(encoder, messageAwareness)
      encoding.writeVarUint8Array(encoder, awarenessProtocol.encodeAwarenessUpdate(awareness, changedClients))
      const message = encoding.toUint8Array(encoder)

      const conns = connections.get(docName)
      conns?.forEach((_, ws) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(message)
        }
      })
    })
  }
  return docData
}

function send(ws: WebSocket, message: Uint8Array) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(message)
  }
}

export function setupYjsServer(wss: WebSocketServer) {
  wss.on('connection', (ws: WebSocket, req) => {
    // Extract document ID from URL query
    const url = new URL(req.url || '', 'http://localhost')
    const docName = url.searchParams.get('doc') || 'default'

    console.log(`Yjs client connected to document: ${docName}`)

    const { doc, awareness } = getYDoc(docName)

    // Track connection
    if (!connections.has(docName)) {
      connections.set(docName, new Map())
    }
    const conns = connections.get(docName)!
    conns.set(ws, { clientId: doc.clientID })

    // Send sync step 1
    const encoder = encoding.createEncoder()
    encoding.writeVarUint(encoder, messageSync)
    syncProtocol.writeSyncStep1(encoder, doc)
    send(ws, encoding.toUint8Array(encoder))

    // Send current awareness state
    const awarenessStates = awareness.getStates()
    if (awarenessStates.size > 0) {
      const encoder = encoding.createEncoder()
      encoding.writeVarUint(encoder, messageAwareness)
      encoding.writeVarUint8Array(encoder, awarenessProtocol.encodeAwarenessUpdate(awareness, Array.from(awarenessStates.keys())))
      send(ws, encoding.toUint8Array(encoder))
    }

    // Handle incoming messages
    ws.on('message', (message: Buffer) => {
      try {
        const data = new Uint8Array(message)
        const decoder = decoding.createDecoder(data)
        const messageType = decoding.readVarUint(decoder)

        switch (messageType) {
          case messageSync: {
            const encoder = encoding.createEncoder()
            encoding.writeVarUint(encoder, messageSync)
            const syncMessageType = syncProtocol.readSyncMessage(decoder, encoder, doc, null)

            if (encoding.length(encoder) > 1) {
              send(ws, encoding.toUint8Array(encoder))
            }

            // Broadcast updates to other clients
            if (syncMessageType === syncProtocol.messageYjsUpdate) {
              const updateEncoder = encoding.createEncoder()
              encoding.writeVarUint(updateEncoder, messageSync)
              syncProtocol.writeUpdate(updateEncoder, decoding.readVarUint8Array(decoding.createDecoder(data.slice(1))))
              const updateMessage = encoding.toUint8Array(updateEncoder)

              conns.forEach((_, client) => {
                if (client !== ws && client.readyState === WebSocket.OPEN) {
                  client.send(updateMessage)
                }
              })
            }
            break
          }
          case messageAwareness: {
            awarenessProtocol.applyAwarenessUpdate(awareness, decoding.readVarUint8Array(decoder), ws)
            break
          }
        }
      } catch (err) {
        console.error('Error processing Yjs message:', err)
      }
    })

    // Handle disconnect
    ws.on('close', () => {
      console.log(`Yjs client disconnected from document: ${docName}`)
      conns.delete(ws)

      // Remove awareness state for this client
      awarenessProtocol.removeAwarenessStates(awareness, [doc.clientID], 'connection closed')

      // Clean up empty documents after delay
      if (conns.size === 0) {
        setTimeout(() => {
          if (connections.get(docName)?.size === 0) {
            connections.delete(docName)
            // Optionally persist or delete document
          }
        }, 60000)
      }
    })

    ws.on('error', (err) => {
      console.error('WebSocket error:', err)
    })
  })

  console.log('Yjs WebSocket server initialized')
}

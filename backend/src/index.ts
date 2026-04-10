import express from 'express'
import cors from 'cors'
import { createServer } from 'http'
import { WebSocketServer } from 'ws'
import { setupYjsServer } from './websocket/yjs-server.js'
import { mwsRouter } from './routes/mws.js'
import { aiRouter } from './routes/ai.js'

const app = express()
const PORT = process.env.PORT || 4000

// Middleware
app.use(cors())
app.use(express.json())

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// API Routes
app.use('/api/mws', mwsRouter)
app.use('/api/ai', aiRouter)

// Create HTTP server
const server = createServer(app)

// Setup WebSocket for Yjs collaboration
const wss = new WebSocketServer({ server, path: '/ws' })
setupYjsServer(wss)

// Start server
server.listen(PORT, () => {
  console.log(`🚀 WikiLive Backend running on port ${PORT}`)
  console.log(`   - REST API: http://localhost:${PORT}/api`)
  console.log(`   - WebSocket: ws://localhost:${PORT}/ws`)
})

import { Router, Request, Response } from 'express'

const router = Router()

const MWS_API_URL = process.env.MWS_API_URL || 'https://tables.mws.ru/fusion/v1'
const MWS_API_KEY = process.env.MWS_API_KEY || ''

// Proxy all requests to MWS Tables API
router.all('/*', async (req: Request, res: Response) => {
  const path = req.params[0] || ''
  const url = `${MWS_API_URL}/${path}${req.url.includes('?') ? req.url.substring(req.url.indexOf('?')) : ''}`

  try {
    const response = await fetch(url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers.authorization || `Bearer ${MWS_API_KEY}`,
      },
      body: ['GET', 'HEAD'].includes(req.method) ? undefined : JSON.stringify(req.body),
    })

    const contentType = response.headers.get('content-type')

    if (contentType?.includes('application/json')) {
      const data = await response.json()
      res.status(response.status).json(data)
    } else {
      const buffer = await response.arrayBuffer()
      res.status(response.status)
        .set('Content-Type', contentType || 'application/octet-stream')
        .send(Buffer.from(buffer))
    }
  } catch (error) {
    console.error('MWS API Error:', error)
    res.status(500).json({
      success: false,
      message: error instanceof Error ? error.message : 'Unknown error',
    })
  }
})

export { router as mwsRouter }

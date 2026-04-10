import { Router, Request, Response } from 'express'

const router = Router()

const MWS_GPT_API_KEY = process.env.MWS_GPT_API_KEY || ''
const MWS_GPT_URL = 'https://api.mws.ru/v1/chat/completions' // Adjust URL as needed

interface ChatRequest {
  message: string
  context?: string
}

// AI completion endpoint
router.post('/complete', async (req: Request, res: Response) => {
  const { message, context } = req.body as ChatRequest

  if (!message) {
    return res.status(400).json({ success: false, message: 'Message is required' })
  }

  try {
    const response = await fetch(MWS_GPT_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${MWS_GPT_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'Ты - AI-помощник для wiki-редактора. Помогай пользователям с написанием и редактированием текста. Отвечай кратко и по делу.',
          },
          ...(context ? [{ role: 'user', content: `Контекст: ${context}` }] : []),
          { role: 'user', content: message },
        ],
        max_tokens: 1000,
        temperature: 0.7,
      }),
    })

    if (!response.ok) {
      throw new Error(`AI API Error: ${response.status}`)
    }

    const data = await response.json()
    const aiMessage = data.choices?.[0]?.message?.content || ''

    res.json({
      success: true,
      data: { message: aiMessage },
    })
  } catch (error) {
    console.error('AI API Error:', error)
    res.status(500).json({
      success: false,
      message: error instanceof Error ? error.message : 'AI request failed',
    })
  }
})

// Summarize text
router.post('/summarize', async (req: Request, res: Response) => {
  const { text } = req.body

  if (!text) {
    return res.status(400).json({ success: false, message: 'Text is required' })
  }

  // For now, return a placeholder. Integrate with MWS GPT API
  res.json({
    success: true,
    data: {
      summary: `Краткое содержание: ${text.substring(0, 100)}...`,
    },
  })
})

// Translate text
router.post('/translate', async (req: Request, res: Response) => {
  const { text, targetLang = 'en' } = req.body

  if (!text) {
    return res.status(400).json({ success: false, message: 'Text is required' })
  }

  // For now, return a placeholder
  res.json({
    success: true,
    data: {
      translation: text, // Placeholder
      targetLang,
    },
  })
})

export { router as aiRouter }

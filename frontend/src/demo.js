export const demoModels = [
  { id: 'demo-gpt-4o', provider_id: 'openai', provider: 'OpenAI', name: 'gpt-4o', context_window: 128000, quality: 0.94, latency: 900, cost: 0.00305, error_rate: 0.9, capabilities: { vision: true, tools: true, json: true } },
  { id: 'demo-gpt-4o-mini', provider_id: 'openai', provider: 'OpenAI', name: 'gpt-4o-mini', context_window: 128000, quality: 0.82, latency: 450, cost: 0.00075, error_rate: 0.7, capabilities: { vision: true, tools: true, json: true } },
  { id: 'demo-claude-sonnet', provider_id: 'anthropic', provider: 'Anthropic', name: 'claude-3-5-sonnet-20241022', context_window: 200000, quality: 0.95, latency: 1100, cost: 0.018, error_rate: 0.8, capabilities: { vision: true, tools: true, json: true } },
  { id: 'demo-claude-haiku', provider_id: 'anthropic', provider: 'Anthropic', name: 'claude-3-5-haiku-20241022', context_window: 200000, quality: 0.84, latency: 550, cost: 0.0048, error_rate: 0.9, capabilities: { vision: true, tools: true, json: true } },
  { id: 'demo-llama-70b', provider_id: 'groq', provider: 'Groq', name: 'llama-3.3-70b-versatile', context_window: 32768, quality: 0.88, latency: 500, cost: 0.00138, error_rate: 1.1, capabilities: { vision: false, tools: true, json: true } },
]

export const demoProjects = [{ id: 'demo-project', user_id: 'demo-user', name: 'TrailBack Demo', retention: 30, policy_id: null }]

export const demoProviders = [
  { id: 'openai', name: 'OpenAI', slug: 'openai' },
  { id: 'anthropic', name: 'Anthropic', slug: 'anthropic' },
  { id: 'groq', name: 'Groq', slug: 'groq' },
]

export const seedRequests = [
  { id: 'req_demo_001', model: 'gpt-4o-mini', provider: 'OpenAI', status: 'completed', input_tokens: 382, output_tokens: 216, total_tokens: 598, cost: 0.00071, latency: 0.71, created_at: new Date(Date.now() - 6 * 60000).toISOString(), fallback_used: false },
  { id: 'req_demo_002', model: 'llama-3.3-70b-versatile', provider: 'Groq', status: 'completed', input_tokens: 601, output_tokens: 180, total_tokens: 781, cost: 0.00050, latency: 0.54, created_at: new Date(Date.now() - 12 * 60000).toISOString(), fallback_used: false },
  { id: 'req_demo_003', model: 'claude-3-5-haiku-20241022', provider: 'Anthropic', status: 'completed', input_tokens: 290, output_tokens: 140, total_tokens: 430, cost: 0.00079, latency: 0.62, created_at: new Date(Date.now() - 21 * 60000).toISOString(), fallback_used: true },
  { id: 'req_demo_004', model: 'gpt-4o', provider: 'OpenAI', status: 'completed', input_tokens: 742, output_tokens: 310, total_tokens: 1052, cost: 0.00500, latency: 1.03, created_at: new Date(Date.now() - 34 * 60000).toISOString(), fallback_used: false },
  { id: 'req_demo_005', model: 'llama-3.3-70b-versatile', provider: 'Groq', status: 'failed', input_tokens: 488, output_tokens: 0, total_tokens: 488, cost: 0, latency: 0.92, created_at: new Date(Date.now() - 49 * 60000).toISOString(), fallback_used: false },
]

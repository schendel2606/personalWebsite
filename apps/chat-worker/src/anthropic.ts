import Anthropic from '@anthropic-ai/sdk';
import type { SystemPromptBlock } from './prompts';

export const MODEL = 'claude-haiku-4-5-20251001';

export interface AskClaudeInput {
  systemBlocks: SystemPromptBlock[];
  messages: Array<{ role: 'user' | 'assistant'; content: string }>;
  maxTokens: number;
}

export async function askClaude(
  client: Anthropic,
  input: AskClaudeInput,
): Promise<string> {
  const response = await client.messages.create({
    model: MODEL,
    max_tokens: input.maxTokens,
    temperature: 0.7,
    system: input.systemBlocks,
    messages: input.messages,
  });
  return response.content
    .filter((b) => b.type === 'text')
    .map((b) => (b as { type: 'text'; text: string }).text)
    .join('');
}

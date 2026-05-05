import { describe, it, expect, vi } from 'vitest';
import { askClaude } from '../src/anthropic';

describe('askClaude', () => {
  it('calls Anthropic with correct model and params', async () => {
    const mockClient = {
      messages: {
        create: vi.fn().mockResolvedValue({
          content: [{ type: 'text', text: 'Niv built X.' }],
        }),
      },
    };
    const result = await askClaude(mockClient as any, {
      systemBlocks: [{ type: 'text', text: 'sys', cache_control: { type: 'ephemeral' } }],
      messages: [{ role: 'user', content: 'tell me about him' }],
      maxTokens: 400,
    });
    expect(result).toBe('Niv built X.');
    expect(mockClient.messages.create).toHaveBeenCalledWith(
      expect.objectContaining({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 400,
        temperature: 0.7,
      }),
    );
  });

  it('returns concatenated text if model returns multiple text blocks', async () => {
    const mockClient = {
      messages: {
        create: vi.fn().mockResolvedValue({
          content: [
            { type: 'text', text: 'Part one. ' },
            { type: 'text', text: 'Part two.' },
          ],
        }),
      },
    };
    const result = await askClaude(mockClient as any, {
      systemBlocks: [{ type: 'text', text: 'sys', cache_control: { type: 'ephemeral' } }],
      messages: [{ role: 'user', content: 'q' }],
      maxTokens: 400,
    });
    expect(result).toBe('Part one. Part two.');
  });
});

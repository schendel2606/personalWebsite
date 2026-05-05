import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import ExperienceTimeline from './ExperienceTimeline.astro';

describe('ExperienceTimeline', () => {
  it('renders all experience entries with role and dates', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(ExperienceTimeline);
    expect(html).toContain('Inspiria LTD');
    expect(html).toContain('Solutions Engineer');
    expect(html).toContain('SAP Business One Implementer');
    // Date formatting check (e.g. "2024-03" → "Mar 2024")
    expect(html).toMatch(/Mar 2024/);
  });
});

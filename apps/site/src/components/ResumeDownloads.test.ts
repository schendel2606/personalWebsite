import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import ResumeDownloads from './ResumeDownloads.astro';

describe('ResumeDownloads', () => {
  it('renders 3 download buttons matching variant labels', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(ResumeDownloads);
    expect(html).toContain('Backend Engineer');
    expect(html).toContain('Data Engineer');
    expect(html).toContain('Solutions Engineer');
    expect(html).toContain('/resumes/');
    expect(html).toContain('Pick the variant');
  });
});

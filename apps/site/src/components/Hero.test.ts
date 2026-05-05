import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import Hero from './Hero.astro';

describe('Hero', () => {
  it('renders name, headline, and social links from facts', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(Hero);

    expect(html).toContain('Niv Schendel');
    expect(html).toContain('Backend engineer building agent-coordinated systems');
    expect(html).toContain('linkedin.com/in/niv-schendel');
    expect(html).toContain('github.com/schendel2606');
  });
});

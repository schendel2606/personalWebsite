import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import ProjectCard from './ProjectCard.astro';
import type { Project } from '../lib/content';

const fixture: Project = {
  id: 'test',
  title: 'TestProject',
  tagline: 'A test project',
  stack: ['Foo', 'Bar'],
  links: { repo: 'https://example.com/repo', live: 'https://example.com' },
  order: 1,
  body: '<p>Body text here.</p>',
};

describe('ProjectCard', () => {
  it('renders title, tagline, and stack pills', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(ProjectCard, {
      props: { project: fixture },
    });
    expect(html).toContain('TestProject');
    expect(html).toContain('A test project');
    expect(html).toContain('Foo');
    expect(html).toContain('Bar');
    expect(html).toContain('https://example.com/repo');
  });

  it('hides "live" link when not provided', async () => {
    const container = await AstroContainer.create();
    const noLive = { ...fixture, links: { repo: fixture.links.repo } };
    const html = await container.renderToString(ProjectCard, {
      props: { project: noLive },
    });
    expect(html).not.toContain('aria-label="Live demo"');
  });
});

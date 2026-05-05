import { describe, it, expect } from 'vitest';
import { loadFacts, loadProjects } from './content';

describe('content loader', () => {
  it('loads facts.yaml with required top-level keys', () => {
    const facts = loadFacts();
    expect(facts.person.name).toBe('Niv Schendel');
    expect(facts.person.email).toContain('@');
    expect(Array.isArray(facts.experience)).toBe(true);
    expect(facts.experience.length).toBeGreaterThan(0);
    expect(Array.isArray(facts.positioning.variants)).toBe(true);
    expect(facts.positioning.variants.length).toBe(3);
  });

  it('loads projects sorted by frontmatter `order`', () => {
    const projects = loadProjects();
    expect(projects.length).toBeGreaterThanOrEqual(2);
    expect(projects[0].id).toBe('taskmanagement');
    expect(projects[0].order).toBe(1);
    expect(projects[0].stack).toContain('React 19');
  });
});

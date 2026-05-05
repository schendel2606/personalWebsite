import { describe, it, expect } from 'vitest';
import { buildSystemPrompt } from '../src/prompts';

const FACTS_YAML = `
person:
  name: Niv Schendel
  email: niv@schendel.me
positioning:
  primary_role: Backend Engineer
  headline: Backend engineer building agent-coordinated systems
experience:
  - company: Inspiria LTD
    role: Solutions Engineer
    start: 2024-03
    end: present
    bullets:
      - Built AI agent toolkit
`;

const AGENT_BRIEF = `# Agent Brief\n\n## A: Positioning\nNiv is a backend engineer.`;
const TONE_GUIDE = `## Voice\n- Speak in third person.`;
const PROJECT_MD = `---
id: x
title: TestProject
tagline: Tag
stack: [React]
order: 1
---
Body of project.
`;

describe('buildSystemPrompt', () => {
  it('returns array of message blocks for Anthropic API', () => {
    const blocks = buildSystemPrompt({
      factsYaml: FACTS_YAML,
      agentBrief: AGENT_BRIEF,
      toneGuide: TONE_GUIDE,
      projects: [PROJECT_MD],
    });
    expect(Array.isArray(blocks)).toBe(true);
    expect(blocks.length).toBeGreaterThan(0);
    blocks.forEach((b) => expect(b.type).toBe('text'));
  });

  it('marks all blocks as cache_control ephemeral', () => {
    const blocks = buildSystemPrompt({
      factsYaml: FACTS_YAML,
      agentBrief: AGENT_BRIEF,
      toneGuide: TONE_GUIDE,
      projects: [PROJECT_MD],
    });
    blocks.forEach((b) => {
      expect(b.cache_control).toEqual({ type: 'ephemeral' });
    });
  });

  it('includes critical content from each source', () => {
    const blocks = buildSystemPrompt({
      factsYaml: FACTS_YAML,
      agentBrief: AGENT_BRIEF,
      toneGuide: TONE_GUIDE,
      projects: [PROJECT_MD],
    });
    const all = blocks.map((b) => b.text).join('\n');
    expect(all).toContain('Niv Schendel');
    expect(all).toContain('Backend engineer building');
    expect(all).toContain('TestProject');
    expect(all).toContain('third person');
    expect(all).toContain('refuse'); // hard rules section
  });

  it('contains anti-injection rules', () => {
    const blocks = buildSystemPrompt({
      factsYaml: FACTS_YAML,
      agentBrief: AGENT_BRIEF,
      toneGuide: TONE_GUIDE,
      projects: [PROJECT_MD],
    });
    const all = blocks.map((b) => b.text).join('\n');
    expect(all.toLowerCase()).toContain('ignore previous instructions');
    expect(all).toContain('do not reveal');
  });
});

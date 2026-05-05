#!/usr/bin/env node
import { readFileSync, readdirSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const CONTENT = join(HERE, '..', '..', '..', 'content');
const OUT = join(HERE, '..', 'src', 'content.json');

mkdirSync(dirname(OUT), { recursive: true });

const factsYaml = readFileSync(join(CONTENT, 'facts.yaml'), 'utf-8');
const agentBrief = readFileSync(join(CONTENT, 'agent-brief.md'), 'utf-8');
const toneGuide = readFileSync(join(CONTENT, 'tone-guide.md'), 'utf-8');

const projectsDir = join(CONTENT, 'projects');
const projects = readdirSync(projectsDir)
  .filter((f) => f.endsWith('.md'))
  .sort()
  .map((f) => readFileSync(join(projectsDir, f), 'utf-8'));

writeFileSync(OUT, JSON.stringify({ factsYaml, agentBrief, toneGuide, projects }, null, 2));
console.log(`✓ Bundled ${projects.length + 3} content files → ${OUT}`);

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';

const HERE = dirname(fileURLToPath(import.meta.url));
const CONTENT_ROOT = join(HERE, '..', '..', '..', '..', 'content');

export interface Facts {
  person: {
    name: string; email: string; phone: string; location: string;
    socials: { linkedin: string; github: string; site: string };
  };
  positioning: {
    primary_role: string;
    headline: string;
    variants: Array<{ id: string; label: string; file: string }>;
  };
  experience: Array<{
    company: string; role: string; start: string; end: string; bullets: string[];
  }>;
  education: Array<{
    school: string; degree: string; start: string; end: string; notes?: string;
  }>;
  skills: Record<string, string[]>;
  achievements: string[];
}

export interface Project {
  id: string;
  title: string;
  tagline: string;
  stack: string[];
  links: { repo?: string; live?: string };
  order: number;
  body: string; // markdown body after frontmatter
}

export function loadFacts(): Facts {
  const raw = readFileSync(join(CONTENT_ROOT, 'facts.yaml'), 'utf-8');
  return yaml.load(raw) as Facts;
}

export function loadProjects(): Project[] {
  const dir = join(CONTENT_ROOT, 'projects');
  const files = readdirSync(dir).filter((f) => f.endsWith('.md'));
  const projects = files.map((f) => parseProject(join(dir, f)));
  return projects.sort((a, b) => a.order - b.order);
}

function parseProject(path: string): Project {
  const raw = readFileSync(path, 'utf-8');
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!m) throw new Error(`Invalid frontmatter in ${path}`);
  const fm = yaml.load(m[1]) as Omit<Project, 'body'>;
  return { ...fm, body: m[2].trim() };
}

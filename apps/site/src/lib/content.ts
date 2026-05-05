import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import yaml from 'js-yaml';
import { marked } from 'marked';

// process.cwd() is the apps/site package root (where npm run build/test runs).
// The monorepo content/ directory is two levels up from apps/site/.
const CONTENT_ROOT = join(process.cwd(), '..', '..', 'content');

export interface Facts {
  person: {
    name: string;
    birthdate?: string; // YYYY-MM-DD
    email: string; phone: string; location: string;
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
  body: string; // HTML rendered from the markdown body after frontmatter
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

/**
 * Compute age (in whole years) from a YYYY-MM-DD birthdate string,
 * relative to `now` (defaults to today). Build-time computation, so the
 * age refreshes on each site rebuild rather than every visitor request.
 */
export function computeAge(birthdate: string, now: Date = new Date()): number {
  const birth = new Date(birthdate);
  let age = now.getFullYear() - birth.getFullYear();
  const m = now.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < birth.getDate())) age--;
  return age;
}

function parseProject(path: string): Project {
  const raw = readFileSync(path, 'utf-8');
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!m) throw new Error(`Invalid frontmatter in ${path}`);
  const fm = yaml.load(m[1]) as Omit<Project, 'body'>;
  // Render markdown body to HTML at build time so ProjectCard can set:html safely.
  // Plain prose passes through unchanged; <!-- TODO --> comments stay as comments (invisible).
  const body = marked.parse(m[2].trim(), { async: false }) as string;
  return { ...fm, body };
}

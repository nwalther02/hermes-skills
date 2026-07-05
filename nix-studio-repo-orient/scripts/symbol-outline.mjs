#!/usr/bin/env node
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { extname, join, relative } from 'node:path';

const targets = process.argv.slice(2);
const roots = targets.length > 0 ? targets : ['apps', 'packages'];
const exts = new Set(['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs']);
const skipDirs = new Set([
  '.git',
  '.wrangler',
  'coverage',
  'dist',
  'node_modules',
  'playwright-report',
  'test-results',
]);
const maxFiles = Number(process.env.SYMBOL_OUTLINE_MAX_FILES || '120');

function walk(path, files = []) {
  if (files.length >= maxFiles) return files;

  let stats;
  try {
    stats = statSync(path);
  } catch {
    return files;
  }

  if (stats.isDirectory()) {
    for (const entry of readdirSync(path)) {
      if (skipDirs.has(entry)) continue;
      walk(join(path, entry), files);
      if (files.length >= maxFiles) break;
    }
    return files;
  }

  if (stats.isFile() && exts.has(extname(path))) {
    files.push(path);
  }
  return files;
}

function matchSymbol(line) {
  const patterns = [
    ['function', /^(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)/],
    ['class', /^(?:export\s+)?class\s+([A-Za-z_$][\w$]*)/],
    ['interface', /^(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)/],
    ['type', /^(?:export\s+)?type\s+([A-Za-z_$][\w$]*)/],
    ['enum', /^(?:export\s+)?enum\s+([A-Za-z_$][\w$]*)/],
    ['const', /^(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*[:=]/],
  ];

  for (const [kind, pattern] of patterns) {
    const match = line.match(pattern);
    if (match) return { kind, name: match[1] };
  }

  const method = line.match(
    /^\s{2,}(?:public\s+|private\s+|protected\s+)?(?:async\s+)?([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*[:{]/,
  );
  if (method && !['if', 'for', 'while', 'switch', 'catch'].includes(method[1])) {
    return { kind: 'method', name: method[1] };
  }

  return null;
}

function outline(file) {
  const text = readFileSync(file, 'utf8');
  const lines = text.split(/\r?\n/);
  const imports = [];
  const symbols = [];

  lines.forEach((line, index) => {
    const importMatch = line.match(/^\s*import\b.*?\sfrom\s['"]([^'"]+)['"]/);
    if (importMatch) imports.push(importMatch[1]);

    const symbol = matchSymbol(line);
    if (symbol) {
      symbols.push({
        line: index + 1,
        signature: line.trim().slice(0, 140),
        ...symbol,
      });
    }
  });

  const display = relative(process.cwd(), file) || file;
  console.log(`\n${display}`);
  if (imports.length > 0) {
    console.log(`  imports: ${[...new Set(imports)].slice(0, 12).join(', ')}`);
  }
  if (symbols.length === 0) {
    console.log('  symbols: none found by heuristic outline');
    return;
  }
  for (const symbol of symbols) {
    console.log(
      `  ${String(symbol.line).padStart(4, ' ')} ${symbol.kind.padEnd(9, ' ')} ${symbol.name} :: ${symbol.signature}`,
    );
  }
}

const files = roots.flatMap((root) => walk(root)).slice(0, maxFiles);
if (files.length === 0) {
  console.error('No JS/TS files found. Pass files or directories to outline.');
  process.exit(1);
}

for (const file of files) {
  outline(file);
}

if (files.length >= maxFiles) {
  console.error(`\nStopped at ${maxFiles} files. Set SYMBOL_OUTLINE_MAX_FILES to raise the cap.`);
}

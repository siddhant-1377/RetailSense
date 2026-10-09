import { spawn, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const pythonPath = process.platform === 'win32'
  ? join(root, 'backend', '.venv', 'Scripts', 'python.exe')
  : join(root, 'backend', '.venv', 'bin', 'python');
const vitePath = join(root, 'node_modules', 'vite', 'bin', 'vite.js');

function fallbackPython() {
  const candidates = process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
  for (const command of candidates) {
    const check = spawnSync(command, ['--version'], { stdio: 'ignore', shell: false });
    if (check.status === 0) return command;
  }
  return null;
}

const python = existsSync(pythonPath) ? pythonPath : fallbackPython();
if (!python) {
  console.error('[RetailSense] Python was not found. Run npm install first.');
  process.exit(1);
}
if (!existsSync(vitePath)) {
  console.error('[RetailSense] Vite is not installed. Run npm install first.');
  process.exit(1);
}

const children = [];
let shuttingDown = false;

function start(label, command, args, cwd = root) {
  const child = spawn(command, args, { cwd, stdio: 'inherit', shell: false });
  children.push({ label, child });
  child.on('exit', (code, signal) => {
    if (shuttingDown) return;
    console.error(`[RetailSense] ${label} stopped${signal ? ` by ${signal}` : ''}.`);
    shutdown(signal ? 1 : (code ?? 0));
  });
  child.on('error', (error) => {
    console.error(`[RetailSense] ${label} failed to start: ${error.message}`);
    shutdown(1);
  });
  return child;
}

function shutdown(code = 0) {
  if (shuttingDown) return;
  shuttingDown = true;
  for (const { child } of children) {
    try { child.kill('SIGTERM'); } catch {}
  }
  setTimeout(() => process.exit(code), 300);
}

process.on('SIGINT', () => shutdown(0));
process.on('SIGTERM', () => shutdown(0));
process.on('exit', () => {
  for (const { child } of children) {
    try { child.kill('SIGTERM'); } catch {}
  }
});

console.log('[RetailSense] Starting backend + frontend...');
start('backend', python, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], join(root, 'backend'));
start('frontend', process.execPath, [vitePath, '--config', 'frontend/vite.config.ts']);

import { existsSync } from 'node:fs';
import { spawnSync, spawn } from 'node:child_process';
import { join } from 'node:path';

const root = process.cwd();
const venvDir = join(root, 'backend', '.venv');
const venvPython = process.platform === 'win32'
  ? join(venvDir, 'Scripts', 'python.exe')
  : join(venvDir, 'bin', 'python');

function findFallbackPython() {
  const candidates = process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
  for (const command of candidates) {
    const result = spawnSync(command, ['--version'], { stdio: 'ignore', shell: false });
    if (result.status === 0) return command;
  }
  return null;
}

const python = existsSync(venvPython) ? venvPython : findFallbackPython();
if (!python) {
  console.error('[RetailSense] Python was not found. Run npm install first, then npm run dev.');
  process.exit(1);
}

const child = spawn(python, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], {
  cwd: join(root, 'backend'),
  stdio: 'inherit',
  shell: false,
});

child.on('error', (error) => {
  console.error(`[RetailSense] Backend failed to start: ${error.message}`);
  process.exitCode = 1;
});
child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exitCode = code ?? 1;
});

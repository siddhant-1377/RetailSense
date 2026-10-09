import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join } from 'node:path';

const root = process.cwd();
const venvDir = join(root, 'backend', '.venv');
const pythonCandidates = process.platform === 'win32'
  ? ['py -3.15', 'py -3.14', 'py -3.13', 'py -3.12', 'py -3.11', 'python', 'py']
  : ['python3', 'python'];

function splitCommand(command) {
  return command.includes(' ') ? command.split(/\s+/) : [command];
}

function run(command, args, cwd = root) {
  const parts = splitCommand(command);
  const result = spawnSync(parts[0], [...parts.slice(1), ...args], { cwd, stdio: 'inherit', shell: false });
  return result.status === 0;
}

function capture(command, args) {
  const parts = splitCommand(command);
  return spawnSync(parts[0], [...parts.slice(1), ...args], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    shell: false,
  });
}

function resolvePython() {
  for (const command of pythonCandidates) {
    const result = capture(command, ['--version']);
    if (result.status === 0) return command;
  }
  return null;
}

const existingPython = join(venvDir, process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const python = resolvePython();

if (!python) {
  console.error('[RetailSense] Python 3.11+ was not found. Install Python and run npm install again.');
  process.exit(1);
}

const version = capture(python, ['-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")']);
const [major, minor] = (version.stdout || '').trim().split('.').map(Number);
if (major !== 3 || Number.isNaN(minor) || minor < 11) {
  console.error('[RetailSense] Python 3.11 or newer is required.');
  process.exit(1);
}
console.log(`[RetailSense] Using Python ${major}.${minor}.`);

let venvPython = existingPython;
if (!existsSync(existingPython)) {
  console.log('[RetailSense] Creating backend Python virtual environment...');
  if (!run(python, ['-m', 'venv', venvDir])) {
    console.error('[RetailSense] Could not create backend/.venv.');
    process.exit(1);
  }
  venvPython = process.platform === 'win32'
    ? join(venvDir, 'Scripts', 'python.exe')
    : join(venvDir, 'bin', 'python');
} else {
  console.log('[RetailSense] Backend Python virtual environment already exists.');
}

console.log('[RetailSense] Updating pip/setuptools/wheel...');
run(venvPython, ['-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel']);

console.log('[RetailSense] Installing backend dependencies from wheel-compatible versions...');
// --only-binary prevents an accidental C/C++ source build on Windows.
// The requirements file uses Python-version markers so CPython 3.11 and newer
// receive a compatible pandas/NumPy wheel instead of trying to compile locally.
if (!run(venvPython, ['-m', 'pip', 'install', '--only-binary=:all:', '-r', 'backend/requirements.txt'])) {
  console.error('[RetailSense] Backend dependency installation failed.');
  console.error('[RetailSense] No Visual Studio build tools are required by this setup; check your Python architecture and internet connection.');
  process.exit(1);
}
console.log('[RetailSense] Backend dependencies ready.');

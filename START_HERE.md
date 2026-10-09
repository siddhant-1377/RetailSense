# RetailSense — Start Here

## One-command startup

From the `RetailSense` folder:

```bash
npm install
npm run dev
```

This starts both the FastAPI backend (`127.0.0.1:8000`) and the React/Vite frontend (`127.0.0.1:5173`).

### Windows shortcut

Double-click `start.bat` to run the same `npm run dev` flow.

## Python note

The installer automatically creates `backend/.venv` and installs wheel-based Python dependencies. It uses Python-version-specific NumPy/Pandas versions so Windows does not try to compile pandas from source. Python 3.11–3.15 are supported by the bundled dependency setup.

## If you previously ran an older ZIP

Delete the old extracted `RetailSense` folder (or at least `backend/.venv`) before using this version, then run `npm install` again.

## Open

http://127.0.0.1:5173

## Main DWM features

- Dashboard
- Dataset upload / management
- Data preprocessing
- Apriori association rules
- J48 / C4.5-style classification
- Naive Bayes classification
- Linear regression
- K-Means clustering
- Algorithm comparison
- Insights & reports
- DWM concepts / assignment mapping

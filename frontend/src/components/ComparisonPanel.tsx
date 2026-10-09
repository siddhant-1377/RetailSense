import { useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { CheckCircle2, GitCompare, Play, Timer, Trophy } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { ComparisonResponse } from '../types';
import { api } from '../api';
import { Badge, Button, Card, CardBody, CardHeader, Loading, Notice, Table } from './UI';

const fmt = (n: number) => new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(n);
const pct = (n: number) => `${(n * 100).toFixed(1)}%`;

export function ComparisonPanel({ sessionId }: { sessionId: string }) {
  const [result, setResult] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runComparison = async () => {
    setLoading(true);
    setError('');
    try {
      setResult(await api.comparison(sessionId));
    } catch (e: any) {
      setError(e.message || 'Could not compare algorithms.');
    } finally {
      setLoading(false);
    }
  };

  const readyRows = result?.rows.filter((row) => row.status === 'ready' && row.score !== null) ?? [];
  const fastest = useMemo(
    () => readyRows.length ? readyRows.reduce((a, b) => a.runtime_ms <= b.runtime_ms ? a : b) : null,
    [readyRows],
  );
  const displayRows = readyRows.map((row) => ({
    name: row.algorithm,
    score: row.score ?? 0,
    task: row.task,
  }));

  return <div>
    <div className="mb-4 flex items-center gap-2">
      <Badge tone="indigo">Model comparison</Badge>
      <span className="text-sm text-slate-500">Compare every algorithm used in the RetailSense DWM workflow.</span>
    </div>

    <Card>
      <CardHeader
        title="Algorithm comparison"
        description="One-click benchmark on the active dataset using sensible default parameters."
        right={<Button onClick={runComparison} disabled={loading}><Play size={15}/> {result ? 'Run again' : 'Run comparison'}</Button>}
      />
      <CardBody>
        <div className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="rounded-2xl border border-indigo-100 bg-indigo-50 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-indigo-800"><GitCompare size={17}/> Task-aware scoring</div>
            <p className="mt-2 text-xs leading-5 text-indigo-700">
              Classification uses weighted F1, regression uses R², clustering uses silhouette score, and Apriori uses best rule confidence.
              The normalized bars are for visual comparison only; different task types are not interchangeable.
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm">
            <div className="font-semibold text-slate-800">Active dataset</div>
            <div className="mt-1 text-xs text-slate-500">Session: <span className="font-mono">{sessionId}</span></div>
            <div className="mt-3 inline-flex items-center gap-2 text-xs font-semibold text-slate-600"><CheckCircle2 size={14} className="text-emerald-600"/> Uses the same dataset as Analytics</div>
          </div>
        </div>
      </CardBody>
    </Card>

    {error && <div className="mt-4"><Notice kind="error">{error}</Notice></div>}
    {loading && <Loading label="Running Apriori, J48, Naive Bayes, Regression and K-Means..."/>}

    {!loading && result && <>
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <MetricSmall label="Algorithms ready" value={`${result.ready_count}/${result.algorithm_count}`} icon={<CheckCircle2 size={17}/>} />
        <MetricSmall label="Classification winner" value={result.classification_winner || '—'} icon={<Trophy size={17}/>} />
        <MetricSmall label="Fastest run" value={fastest ? `${fmt(fastest.runtime_ms)} ms` : '—'} icon={<Timer size={17}/>} helper={fastest?.algorithm} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader title="Performance comparison" description="Higher display score is better within the relevant task."/>
          <CardBody>
            <div className="h-[420px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={displayRows} layout="vertical" margin={{ left: 12, right: 18, top: 12, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false}/>
                  <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}`}/>
                  <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }}/>
                  <Tooltip formatter={(v: any) => [`${Number(v).toFixed(1)}/100`, 'Display score']} />
                  <Bar dataKey="score" radius={[0, 6, 6, 0]}>
                    {displayRows.map((entry) => <Cell key={entry.name} fill="#4f46e5" />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Detailed results" description="Supporting metrics and configuration details."/>
          <CardBody>
            <Table
              columns={[
                { key: 'algorithm', label: 'Algorithm' },
                { key: 'task', label: 'Task' },
                { key: 'metric', label: 'Metric' },
                { key: 'value', label: 'Value' },
                { key: 'runtime', label: 'Time' },
              ]}
              rows={result.rows.map((row) => ({
                algorithm: <div><div className="font-semibold">{row.algorithm}</div><div className="mt-0.5 max-w-[260px] text-[11px] text-slate-400">{row.detail || row.status}</div></div>,
                task: <Badge tone="slate">{row.task}</Badge>,
                metric: row.metric,
                value: row.value === null ? <Badge tone="red">Unavailable</Badge> : row.metric === 'Silhouette' ? row.value.toFixed(3) : (row.metric === 'Best confidence' || row.metric === 'Weighted F1') ? pct(row.value) : row.value.toFixed(3),
                runtime: `${fmt(row.runtime_ms)} ms`,
              }))}
            />
          </CardBody>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="What the comparison means" description="Useful explanation for your DWM practical / viva."/>
          <CardBody className="space-y-3 text-sm leading-6 text-slate-600">
            <p><span className="font-semibold text-slate-800">J48 vs Naive Bayes:</span> compare weighted F1 on the same target and test split. The higher F1 is the better classifier for this run.</p>
            <p><span className="font-semibold text-slate-800">Regression:</span> R² shows how much variation in the numerical target is explained by the model; MAE and RMSE are shown as supporting error metrics.</p>
            <p><span className="font-semibold text-slate-800">Clustering:</span> silhouette closer to 1 generally indicates better separated clusters; the displayed 0–100 score is only a normalized visual.</p>
            <p><span className="font-semibold text-slate-800">Apriori:</span> confidence and lift describe rule strength, while rule count tells how many rules passed the chosen thresholds.</p>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Run configuration" description="Defaults selected automatically from the active dataset."/>
          <CardBody>
            <div className="space-y-3 text-sm text-slate-600">
              {result.notes.map((note) => <div key={note} className="rounded-xl border border-slate-200 bg-white p-3">{note}</div>)}
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs leading-5 text-slate-500">{result.methodology.cross_task}</div>
            </div>
          </CardBody>
        </Card>
      </div>
    </>}

    {!loading && !result && <div className="mt-6"><Notice kind="info">Click “Run comparison” to benchmark all available algorithms on the current dataset.</Notice></div>}
  </div>;
}

function MetricSmall({ label, value, icon, helper }: { label: string; value: string; icon: ReactNode; helper?: string }) {
  return <Card><CardBody><div className="flex items-start justify-between gap-3"><div><div className="text-sm text-slate-500">{label}</div><div className="mt-2 text-xl font-bold tracking-tight">{value}</div>{helper && <div className="mt-1 text-xs text-slate-400">{helper}</div>}</div><div className="rounded-xl bg-indigo-50 p-2.5 text-indigo-600">{icon}</div></div></CardBody></Card>;
}

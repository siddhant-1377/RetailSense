import { useMemo, useState } from 'react';
import { CheckCircle2, RotateCcw, Wand2 } from 'lucide-react';
import type { SummaryResponse } from '../types';
import { api } from '../api';
import { Badge, Button, Card, CardBody, CardHeader, Notice, PageHeader, Select, Table } from '../components/UI';

export function PreprocessPage({ sessionId, data, refresh }: { sessionId:string; data:SummaryResponse|null; refresh:()=>Promise<void> }) {
  const [missingMethod,setMissingMethod]=useState('median'); const [removeDup,setRemoveDup]=useState(true); const [normalize,setNormalize]=useState<string[]>([]); const [loading,setLoading]=useState(false); const [error,setError]=useState(''); const [result,setResult]=useState<any>(null);
  const numeric = data?.profile.numeric_columns || [];
  const toggle=(c:string)=>setNormalize(v=>v.includes(c)?v.filter(x=>x!==c):[...v,c]);
  const run=async()=>{setLoading(true);setError('');try{const r=await api.preprocess({session_id:sessionId,missing_method:missingMethod,remove_duplicates:removeDup,detect_outliers:true,normalize_columns:normalize,encode_categoricals:false});setResult(r);await refresh()}catch(e:any){setError(e.message)}finally{setLoading(false)}};
  const outlierRows=(result?.outliers||[]).map((r:any)=>({column:r.column,count:r.count,range:`${r.min ?? '—'} → ${r.max ?? '—'}`,q1:r.q1??'—',q3:r.q3??'—'}));
  return <>
    <PageHeader eyebrow="Assignment 4" title="Data preprocessing" description="Prepare the current dataset for downstream mining and modeling using standard data-quality techniques." right={<Button onClick={run} disabled={loading}><Wand2 size={16}/>{loading?'Applying...':'Apply preprocessing'}</Button>}/>
    {error&&<div className="mb-4"><Notice kind="error">{error}</Notice></div>}
    <div className="grid gap-6 xl:grid-cols-[1fr_350px]">
      <Card><CardHeader title="Preprocessing controls" description="Choose how the current dataset should be transformed."/><CardBody><div className="grid gap-5 sm:grid-cols-2">
        <div><label className="label">Missing-value method</label><Select value={missingMethod} onChange={e=>setMissingMethod(e.target.value)} options={[{value:'remove',label:'Remove rows with missing values'},{value:'mean',label:'Mean imputation (numeric) + mode'},{value:'median',label:'Median imputation (numeric) + mode'}]}/></div>
        <div><label className="label">Duplicate records</label><button onClick={()=>setRemoveDup(v=>!v)} className={`flex w-full items-center justify-between rounded-xl border p-3 text-left text-sm ${removeDup?'border-emerald-200 bg-emerald-50':'border-slate-200 bg-white'}`}><span>{removeDup?'Remove duplicates':'Keep duplicates'}</span>{removeDup&&<CheckCircle2 size={17} className="text-emerald-600"/>}</button></div>
      </div><div className="mt-6"><div className="label">Min-Max normalization (optional)</div><div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{numeric.map(c=><button key={c} onClick={()=>toggle(c)} className={`rounded-xl border px-3 py-2.5 text-left text-xs font-medium ${normalize.includes(c)?'border-indigo-300 bg-indigo-50 text-indigo-700':'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'}`}>{normalize.includes(c)?'✓ ':''}{c}</button>)}</div></div></CardBody></Card>
      <Card><CardHeader title="Current data quality"/><CardBody><div className="space-y-3">{[
        ['Missing cells',data?.profile.missing_values||0],['Duplicates',data?.profile.duplicate_records||0],['Numeric columns',numeric.length],['Categorical columns',data?.profile.categorical_columns.length||0]
      ].map(([l,v])=><div key={String(l)} className="flex items-center justify-between border-b border-slate-100 py-2 last:border-0"><span className="text-sm text-slate-600">{l}</span><span className="font-semibold">{v}</span></div>)}</div><div className="mt-4 rounded-xl bg-slate-50 p-3 text-xs leading-5 text-slate-500">Categorical encoding is performed internally by the classification and regression pipelines when required.</div></CardBody></Card>
    </div>
    {result&&<div className="mt-6 grid gap-6 lg:grid-cols-2"><Card><CardHeader title="Preprocessing summary"/><CardBody><div className="grid gap-3 sm:grid-cols-2">{Object.entries(result.summary||{}).map(([k,v])=><div key={k} className="rounded-xl bg-slate-50 p-4"><div className="text-xs capitalize text-slate-500">{k.split('_').join(' ')}</div><div className="mt-1 text-xl font-bold">{String(v)}</div></div>)}</div><div className="mt-4"><Badge tone="green">Changes applied to the active dataset</Badge></div></CardBody></Card><Card><CardHeader title="IQR outlier scan" description="Numerical columns inspected using the 1.5×IQR rule"/><CardBody><Table columns={[{key:'column',label:'Column'},{key:'count',label:'Outliers'},{key:'range',label:'Observed range'},{key:'q1',label:'Q1'},{key:'q3',label:'Q3'}]} rows={outlierRows}/></CardBody></Card></div>}
    <div className="mt-6 flex flex-wrap items-center gap-2 text-xs text-slate-500"><button onClick={()=>{setResult(null);refresh()}} className="inline-flex items-center gap-2 rounded-xl px-3 py-2 hover:bg-slate-100"><RotateCcw size={14}/> Refresh quality</button><span>After preprocessing, the cleaned dataset is used by all analytics modules.</span></div>
  </>;
}

import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import type { SummaryResponse, TabKey } from './types';
import { api } from './api';
import { Layout, MobileNav } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { DatasetPage } from './pages/DatasetPage';
import { PreprocessPage } from './pages/PreprocessPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { InsightsPage } from './pages/InsightsPage';
import { DWMPage } from './pages/DWMPage';
import { Notice } from './components/UI';

export function App() {
  const [active,setActive]=useState<TabKey>('dashboard');
  const [sessionId,setSessionIdState]=useState(localStorage.getItem('retailsense_session')||'demo');
  const [data,setData]=useState<SummaryResponse|null>(null);
  const [fileName,setFileName]=useState(localStorage.getItem('retailsense_filename')||'retail_transactions.csv');
  const [isDemo,setIsDemo]=useState(localStorage.getItem('retailsense_demo')!=='false');
  const [loading,setLoading]=useState(true); const [error,setError]=useState('');
  const setSessionId=(id:string)=>{setSessionIdState(id);localStorage.setItem('retailsense_session',id)};
  const refresh=async()=>{try{const s=await api.summary(sessionId);setData(s);setIsDemo(s.demo);localStorage.setItem('retailsense_demo',String(s.demo));}catch(e:any){setError(e.message);if(sessionId!=='demo'){setSessionId('demo');setFileName('retail_transactions.csv');localStorage.setItem('retailsense_filename','retail_transactions.csv')}}};
  useEffect(()=>{(async()=>{setLoading(true);try{await refresh()}finally{setLoading(false)}})()},[sessionId]);
  const changeFileName=(s:string)=>{setFileName(s);localStorage.setItem('retailsense_filename',s)};
  const page = active==='dashboard'?<Dashboard data={data} navigate={setActive}/>:active==='dataset'?<DatasetPage sessionId={sessionId} data={data} setSessionId={setSessionId} refresh={refresh} setFileName={changeFileName} setDemo={setIsDemo}/>:active==='preprocess'?<PreprocessPage sessionId={sessionId} data={data} refresh={refresh}/>:active==='analytics'?<AnalyticsPage sessionId={sessionId} data={data}/>:active==='insights'?<InsightsPage sessionId={sessionId} data={data}/>:<DWMPage/>;
  if(loading)return <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-slate-500"><Loader2 size={18} className="mr-2 animate-spin"/> Loading RetailSense...</div>;
  return <Layout active={active} onNavigate={setActive} isDemo={isDemo} fileName={fileName}><MobileNav active={active} onNavigate={setActive}/>{error&&<div className="mb-4"><Notice kind="error">{error}</Notice></div>}{page}</Layout>;
}

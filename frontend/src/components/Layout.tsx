import type { ReactNode } from 'react';
import { BarChart3, Database, FileSpreadsheet, Gauge, GitBranch, Info, Lightbulb, Settings2, Sparkles, UploadCloud } from 'lucide-react';
import type { TabKey } from '../types';

const items: { key: TabKey; label: string; icon: typeof Gauge }[] = [
  { key: 'dashboard', label: 'Dashboard', icon: Gauge },
  { key: 'dataset', label: 'Dataset Management', icon: Database },
  { key: 'preprocess', label: 'Data Preprocessing', icon: Settings2 },
  { key: 'analytics', label: 'Analytics', icon: BarChart3 },
  { key: 'insights', label: 'Insights & Reports', icon: Lightbulb },
  { key: 'dwm', label: 'About / DWM Concepts', icon: Info },
];

export function Layout({ active, onNavigate, children, isDemo, fileName }: { active: TabKey; onNavigate: (key: TabKey) => void; children: ReactNode; isDemo: boolean; fileName: string }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-slate-200 bg-white lg:block">
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-3 px-6 py-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-lg shadow-indigo-200"><Sparkles size={20}/></div>
            <div><div className="font-bold tracking-tight">RetailSense</div><div className="text-xs text-slate-500">DWM Analytics Platform</div></div>
          </div>
          <nav className="space-y-1 px-3">
            {items.map(({ key, label, icon: Icon }) => (
              <button key={key} onClick={() => onNavigate(key)} className={`nav-item ${active === key ? 'nav-item-active' : ''}`}>
                <Icon size={18}/><span>{label}</span>
              </button>
            ))}
          </nav>
          <div className="mt-auto border-t border-slate-200 p-4">
            <div className="rounded-2xl bg-slate-50 p-4">
              <div className="mb-2 flex items-center gap-2 text-sm font-semibold"><FileSpreadsheet size={16}/> Current dataset</div>
              <div className="truncate text-xs text-slate-500">{fileName || 'Demo dataset'}</div>
              <div className="mt-3 inline-flex items-center gap-2 rounded-full bg-white px-2.5 py-1 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200">
                <span className={`h-1.5 w-1.5 rounded-full ${isDemo ? 'bg-amber-500' : 'bg-emerald-500'}`}/>{isDemo ? 'Synthetic demo' : 'Uploaded dataset'}
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
              <div className="lg:hidden flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white"><Sparkles size={18}/></div>
              <div><div className="font-semibold">Retail analytics workspace</div><div className="hidden text-xs text-slate-500 sm:block">Data Warehousing & Data Mining · Assignment 10</div></div>
            </div>
            <div className="flex items-center gap-2">
              <div className="hidden rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600 sm:flex items-center gap-2"><UploadCloud size={14}/> {isDemo ? 'Using Demo Dataset' : 'Live Dataset'}</div>
            </div>
          </div>
        </header>
        <main className="p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}

export function MobileNav({ active, onNavigate }: { active: TabKey; onNavigate: (key: TabKey) => void }) {
  return <div className="mb-5 overflow-x-auto rounded-2xl border border-slate-200 bg-white p-2 shadow-soft lg:hidden">
    <div className="flex min-w-max gap-1">{items.map(({ key, label }) => <button key={key} onClick={() => onNavigate(key)} className={`mobile-tab ${active===key?'mobile-tab-active':''}`}>{label}</button>)}</div>
  </div>
}

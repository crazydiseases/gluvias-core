'use client';
import React, { useState } from 'react';

export default function Dashboard() {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('legal');
  const [report, setReport] = useState('');
  const [scope, setScope] = useState('');
  const [loading, setLoading] = useState(false);
  const [showExport, setShowExport] = useState(false);

  const executePipeline = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setReport('');
    try {
      const res = await fetch(`/api/master-intel?q=${encodeURIComponent(query)}&mode=${mode}`);
      
      // Let's protect against raw text errors (like 500 pages) crashing the JSON parser
      const contentType = res.headers.get("content-type");
      if (!res.ok) {
        const errText = await res.text();
        setReport(`Server returned error status (${res.status}): ${errText}`);
        return;
      }

      const data = await res.json();
      
      // Handle it if the backend responds with a raw intelligence string or an object wrapper
      if (typeof data === 'string') {
        setReport(data);
      } else {
        setReport(data.intelligence_report || JSON.stringify(data) || 'No data resolved.');
        setScope(data.structured_data?.scope || (data.fact_table?.name) || mode.toUpperCase());
      }
      setShowExport(true);
    } catch (e) {
      console.error("Pipeline Exception Captured:", e);
      setReport(`Execution sequence aborted internally. Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const triggerExport = async () => {
    try {
      const res = await fetch('/api/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: scope, content: report })
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `GLUVIAS_REPORT.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch(e) {
      alert("Context export generation failed.");
    }
  };

  return (
    <div className="p-6 bg-[#050507] text-[#d4d4d8] min-h-screen" style={{ fontFamily: '"Gill Sans", "Gill Sans MT", Calibri, sans-serif' }}>
      <header className="flex justify-between items-center pb-4 mb-6 border-b border-zinc-800">
        <span className="text-2xl font-bold tracking-widest text-zinc-100 uppercase">GLUVIAS // INTERFACE</span>
        <div className="px-3 py-1 text-xs font-bold text-red-500 border border-red-900 bg-red-950/20 rounded tracking-wider">Active Core Node</div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side Control Panel */}
        <section className="lg:col-span-4 flex flex-col space-y-4">
          <div className="bg-[#0d0f14] p-5 rounded border border-zinc-800 flex flex-col space-y-4">
            <div>
              <h3 className="text-xs font-bold text-red-500 tracking-wider uppercase mb-2">// Main Workspace Interface</h3>
              <p className="text-zinc-400 text-xs leading-relaxed">Describe your case parameters. Default state executes a high-level Master Legal Search mapping CPR, Case Law, and statutes.</p>
            </div>

            {/* Selection Overrides */}
            <div className="border-t border-b border-zinc-900 py-3 space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500 block">Secondary Modifiers</span>
              <label className="flex items-center space-x-2 text-xs text-zinc-300 cursor-pointer">
                <input type="radio" name="dashboardMode" value="legal" checked={mode === 'legal'} onChange={() => setMode('legal')} className="accent-red-600" />
                <span>Pure Master Legal Search (Default)</span>
              </label>
              <label className="flex items-center space-x-2 text-xs text-zinc-300 cursor-pointer">
                <input type="radio" name="dashboardMode" value="corp" checked={mode === 'corp'} onChange={() => setMode('corp')} className="accent-red-600" />
                <span>Override: Search Companies House</span>
              </label>
              <label className="flex items-center space-x-2 text-xs text-zinc-300 cursor-pointer">
                <input type="radio" name="dashboardMode" value="plan" checked={mode === 'plan'} onChange={() => setMode('plan')} className="accent-red-600" />
                <span>Override: Search Planning Metadata</span>
              </label>
            </div>

            {/* Primary Unified Textarea input box */}
            <div className="flex flex-col space-y-2">
              <textarea 
                rows={4} 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={mode === 'corp' ? "Enter corporate registration names or CRN keys..." : mode === 'plan' ? "Enter area coordinates or spatial track tags..." : "Describe the master legal problem framework, core liabilities, or rule violations..."}
                className="w-full bg-[#050507] text-zinc-200 p-3 text-xs border border-zinc-800 focus:outline-none focus:border-red-700 tracking-wide rounded resize-none"
              />
              <button onClick={executePipeline} className="bg-red-950 hover:bg-red-900 text-red-200 border border-red-900 text-xs py-2 font-bold tracking-widest uppercase transition rounded w-full">
                Run Engine Pipeline
              </button>
            </div>
          </div>
        </section>

        {/* Right Side Analysis Display */}
        <section className="lg:col-span-8 flex flex-col">
          <div className="bg-[#0d0f14] p-6 rounded border border-zinc-800 flex-1 min-h-[500px]">
            <div className="flex justify-between items-center border-b border-zinc-800 pb-3 mb-4">
              <h2 className="text-sm font-bold text-red-500 uppercase tracking-widest">// Engine Response Pipeline</h2>
              {showExport && (
                <button onClick={triggerExport} className="text-xs font-bold tracking-wider text-zinc-400 hover:text-zinc-100 bg-zinc-900/50 px-3 py-1 border border-zinc-800 rounded transition">
                  [ DOWNLOAD BRIEFING .DOCX ]
                </button>
              )}
            </div>
            <div className="text-xs text-zinc-300 space-y-4 tracking-wide leading-relaxed">
              {loading ? (
                <p className="text-zinc-500 animate-pulse">// Querying operational nodes and syncing Claude 4.6 legal analysis structures...</p>
              ) : report ? (
                <div>
                  <div className="bg-zinc-950 p-2 border border-zinc-900 rounded mb-4 text-zinc-400 text-[10px] tracking-wider uppercase">
                    SYSTEM TARGET PROFILE: <strong className="text-red-500">{scope}</strong>
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: report.replace(/\n/g, '<br />') }} />
                </div>
              ) : (
                <p className="italic text-zinc-600">Awaiting user parameters. System context layer standing by.</p>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

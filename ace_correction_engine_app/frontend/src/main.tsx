import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { createSession, generateRevised, submitCorrection } from './api/client';
import type { CorrectionItem } from './types/models';
import './style.css';

const sampleResponse = `A4197AEK      050126     AX
B  4197AEKAX                                  4197AEK  1
E0 SUMMRY 000001 REF ID: AEK 11139903              JBZ
E0 LINITM 000014 REF ID: 014
E0 TARIFF 000003 REF ID: 7326908688
E1 I465   ARTICLE MAY BE SUBJECT TO AD/CVD        AEK  11139903
E0 LINITM 000015 REF ID: 015
E0 TARIFF 000003 REF ID: 7326908688
E1 I465   ARTICLE MAY BE SUBJECT TO AD/CVD        AEK  11139903
E1AI995   SUMMARY HAS BEEN ADDED                  AEK  1113990300100
Y  4197AEKAX00008
Z4197AEK      050126`;

const sampleRequest = `10AAEK  11139903 4197            1140 X           050126          Y
1194-33804250294-338042502               050126050126
203S  4197050126Z529
213S 50
2200000011CTN
23M    61598707652
318B 036
40  014 CNHK050126        0000000000     0000000000    N
44METAL ARTICLE
47C00-000000000
47MCNMANUFACTURER1
47ECNEXPORTER0001
507326908688 0000000000 0000000000 000000000001NO
40  015 CNHK050126        0000000000     0000000000    N
44METAL ARTICLE 2
47C00-000000000
47MCNMANUFACTURER2
47ECNEXPORTER0002
507326908688 0000000000 0000000000 000000000001NO
9000000000000 00000000000 00000000000 00000000000 00000000000 00000000000`;

function App() {
  const [requestText, setRequestText] = useState(sampleRequest);
  const [responseText, setResponseText] = useState(sampleResponse);
  const [sessionId, setSessionId] = useState<string>('');
  const [corrections, setCorrections] = useState<CorrectionItem[]>([]);
  const [revised, setRevised] = useState('');
  const [error, setError] = useState('');

  async function onCreate() {
    setError(''); setRevised('');
    try {
      const data = await createSession(requestText, responseText);
      setSessionId(data.sessionId);
      setCorrections(data.corrections);
    } catch (e: any) { setError(e.message); }
  }

  async function onCorrection(item: CorrectionItem, newValue: string) {
    if (!sessionId) return;
    try {
      const updated = await submitCorrection(sessionId, item.id, newValue);
      setCorrections(prev => prev.map(x => x.id === updated.id ? updated : x));
    } catch (e: any) { setError(e.message); }
  }

  async function onGenerate() {
    if (!sessionId) return;
    try {
      const data = await generateRevised(sessionId);
      setRevised(data.revisedAceRequestMessage);
    } catch (e: any) { setError(e.message); }
  }

  return <main>
    <h1>ACE ABI Correction Engine</h1>
    <p className="subtitle">Configuration-driven correction workflow for ACE request/response messages.</p>
    {error && <pre className="error">{error}</pre>}
    <section className="grid">
      <label>ACE Request Message<textarea value={requestText} onChange={e => setRequestText(e.target.value)} /></label>
      <label>ACE Response Message<textarea value={responseText} onChange={e => setResponseText(e.target.value)} /></label>
    </section>
    <button onClick={onCreate}>Create Correction Session</button>

    {corrections.length > 0 && <section>
      <h2>Correction Work Items</h2>
      {corrections.map(item => <CorrectionCard key={item.id} item={item} onSave={(v) => onCorrection(item, v)} />)}
      <button onClick={onGenerate}>Generate Revised ACE Request</button>
    </section>}

    {revised && <section><h2>Revised ACE Request</h2><textarea className="output" value={revised} readOnly /></section>}
  </main>;
}

function CorrectionCard({ item, onSave }: { item: CorrectionItem; onSave: (value: string) => void }) {
  const [value, setValue] = useState(item.correctedValue ?? item.currentValue ?? '');
  const isEditable = item.status !== 'MANUAL_REVIEW' && item.fieldStart != null;
  return <div className="card">
    <div className="row"><strong>{item.conditionCode}</strong><span>{item.severityCode}</span><span>{item.scope}</span><span>{item.status}</span></div>
    <p>{item.narrativeText}</p>
    <p><b>View:</b> {item.viewName} / {item.sectionName}</p>
    <p><b>Field:</b> {item.uiLabel ?? item.fieldName} | <b>Record:</b> {item.recordId} | <b>Line:</b> {item.requestLineNo ?? '-'}</p>
    <p><b>Current:</b> <code>{item.currentValue}</code></p>
    {isEditable ? <div className="row"><input value={value} onChange={e => setValue(e.target.value)} /><button onClick={() => onSave(value)}>Save Correction</button></div> : <em>Manual review required; no mapped request field.</em>}
  </div>;
}

createRoot(document.getElementById('root')!).render(<App />);

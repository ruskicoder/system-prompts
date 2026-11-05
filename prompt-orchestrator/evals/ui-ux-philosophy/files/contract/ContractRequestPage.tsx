// Contract request: a 4-step wizard to request a device rental contract, then the record view.
import React, { useEffect, useState } from 'react';
import { DatePicker, Stepper, Tabs } from './ui';
import { submitRequest, getQuote, saveContract } from './api';

const initial = { orgName: '', contact: '', startDate: '', endDate: '', devices: 1, notes: '', billingOrg: '', marketing: true };

export function ContractRequestPage() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState(initial);
  const [quote, setQuote] = useState<number | null>(null);
  const [loadingQuote, setLoadingQuote] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(600); // "offer" countdown, restarts on every page load

  useEffect(() => {
    const t = setInterval(() => setSecondsLeft((s) => (s > 0 ? s - 1 : 600)), 1000);
    return () => clearInterval(t);
  }, []);

  const valid = form.orgName && form.contact && form.startDate && form.endDate && form.billingOrg;

  function back() {
    setForm(initial); // start the step again
    setStep(step - 1);
  }

  async function next() {
    if (step === 2) {
      setLoadingQuote(true);
      setQuote(await getQuote(form)); // pricing service, usually 15 to 40 seconds
      setLoadingQuote(false);
    }
    setStep(step + 1);
  }

  async function submit() {
    const errors = await submitRequest(form);
    if (errors.length) window.alert('Invalid input');
  }

  return (
    <div className="page">
      <p className="urgency">Offer ends in {Math.floor(secondsLeft / 60)}:{String(secondsLeft % 60).padStart(2, '0')}!</p>
      <Stepper current={step} total={4} />

      {step === 1 && (
        <div className="grid grid-cols-2 gap-4">
          <label>Organization<input value={form.orgName} onChange={(e) => setForm({ ...form, orgName: e.target.value })} /></label>
          <label>Contact person<input value={form.contact} onChange={(e) => setForm({ ...form, contact: e.target.value })} /></label>
          <label>Notes<textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></label>
          <label>Number of devices<input type="number" value={form.devices} onChange={(e) => setForm({ ...form, devices: +e.target.value })} /></label>
        </div>
      )}

      {step === 2 && (
        <div className="grid grid-cols-2 gap-4">
          <label>Start date<DatePicker value={form.startDate} onChange={(v) => setForm({ ...form, startDate: v })} /></label>
          <label>End date<DatePicker value={form.endDate} onChange={(v) => setForm({ ...form, endDate: v })} /></label>
        </div>
      )}

      {step === 3 && (
        <div>
          {loadingQuote ? <p>Loading...</p> : <p>Quote: {quote} VND</p>}
          <label>Organization name for billing<input value={form.billingOrg} onChange={(e) => setForm({ ...form, billingOrg: e.target.value })} /></label>
          <label><input type="checkbox" checked={form.marketing} onChange={(e) => setForm({ ...form, marketing: e.target.checked })} /> Send me offers and share my details with partners</label>
        </div>
      )}

      <div className="actions">
        {step > 1 && <button className="btn" onClick={back}>Back</button>}
        <button className="btn" onClick={() => setForm(initial)}>Reset form</button>
        <button className="btn btn-danger btn-lg">Cancel request</button>
        {step < 4 ? (
          <button className="btn btn-primary" onClick={next}>Next</button>
        ) : (
          <button className="btn btn-primary" disabled={!valid} onClick={submit}>OK</button>
        )}
      </div>
    </div>
  );
}

// Record view of an approved contract. Users edit fields in place.
export function ContractRecord({ contract }: { contract: any }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(contract);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 's') { e.preventDefault(); saveContract(draft); setEditing(false); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [draft]);

  return (
    <div className="record">
      <h1>{contract.code}</h1>
      <Tabs
        items={['Overview', 'Devices', 'Invoices', 'Payments', 'Handover', 'Returns', 'Documents', 'History']}
        links={['Billing settings', 'Organization profile']}
      />
      <div onDoubleClick={() => setEditing(true)}>
        {editing ? (
          <input value={draft.notes} onChange={(e) => setDraft({ ...draft, notes: e.target.value })} />
        ) : (
          <p>{contract.notes}</p>
        )}
      </div>
    </div>
  );
}

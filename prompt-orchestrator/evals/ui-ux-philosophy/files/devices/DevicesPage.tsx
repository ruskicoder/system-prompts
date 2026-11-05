// Devices list screen of a fleet management app (React, simplified for review).
import React, { useEffect, useState } from 'react';
import { useDevices, retireDevice, deleteDevice, saveDevice } from './api';
import { toast } from './toast';

type Device = { id: string; tag: string; model: string; status: 'AVAILABLE' | 'RENTED' | 'RETIRED'; lastSeen: string };

const STATUS_COLOR = { AVAILABLE: '#16a34a', RENTED: '#2563eb', RETIRED: '#9ca3af' };

export function DevicesPage() {
  const { data, isLoading, error, refetch } = useDevices();
  const [tabClicks, setTabClicks] = useState<Record<string, number>>({ All: 0, Rented: 0, Retired: 0, Maintenance: 0 });
  const [sort, setSort] = useState<'asc' | 'desc'>('asc');

  // Most used tabs move to the front.
  const tabs = Object.keys(tabClicks).sort((a, b) => tabClicks[b] - tabClicks[a]);

  useEffect(() => {
    if (error) toast.show('Error 500');
  }, [error]);

  async function onSaved() {
    await refetch();
    window.scrollTo(0, 0);
  }

  async function onEdit(d: Device) {
    if (!window.confirm('Are you sure?')) return; // OK / Cancel
    await saveDevice(d);
    await onSaved();
  }

  async function onDelete(d: Device) {
    await deleteDevice(d.id); // permanent, no undo
    await onSaved();
  }

  return (
    <div className="page">
      <div className="banner banner-info">Scheduled maintenance on Sunday 02:00.</div>
      <div className="banner banner-warning">3 devices have low battery.</div>
      <div className="banner banner-promo">Try the new fleet map!</div>

      <header className="page-header">
        <h1>Devices</h1>
        <button className="btn btn-primary">Register device</button>
        <button className="btn btn-primary">Export CSV</button>
      </header>

      <nav className="tabs">
        {tabs.map((t) => (
          <button key={t} className="tab" onClick={() => setTabClicks({ ...tabClicks, [t]: tabClicks[t] + 1 })}>{t}</button>
        ))}
      </nav>

      <input className="search" placeholder="Search devices" />

      {!data && <p className="empty">No devices.</p>}

      {data && (
        <table>
          <thead>
            <tr>
              <th><div className="sortable" onClick={() => setSort(sort === 'asc' ? 'desc' : 'asc')}>Tag</div></th>
              <th>Model</th>
              <th>Status</th>
              <th>Last seen</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d: Device) => (
              <tr key={d.id}>
                <td><a href={`/devices/${d.id}`}>{d.tag}</a></td>
                <td>{d.model}</td>
                <td>
                  {/* Click the status to change it */}
                  <span className="dot" style={{ background: STATUS_COLOR[d.status] }} onClick={() => retireDevice(d.id)} />
                </td>
                <td>{d.lastSeen}</td>
                <td>
                  <div className="row-actions">
                    <IconButton icon="info" label={`Show details of ${d.tag}`} tooltip="Show details" />
                    {d.status !== 'RETIRED' && <IconButton icon="edit" label={`Edit ${d.tag}`} tooltip="Edit" onClick={() => onEdit(d)} />}
                    <IconButton icon="trash" label={`Delete ${d.tag}`} tooltip="Delete" onClick={() => onDelete(d)} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <nav className="pagination" aria-label="Pages">
        <a href="?page=1" aria-current="page">1</a> <a href="?page=2">2</a> <a href="?page=2">Next</a>
      </nav>
    </div>
  );
}

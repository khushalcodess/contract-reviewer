import { useEffect, useState } from "react";
import { listContracts, uploadContract, deleteContract } from "./api";

function Findings({ c }) {
  if (c.status !== "done") return <span className="muted">-</span>;
  const s = c.summary || {};
  const parts = [];
  if (s.high) parts.push(<span key="h" className="badge high">{s.high} High</span>);
  if (s.medium) parts.push(<span key="m" className="badge medium">{s.medium} Medium</span>);
  if (s.low) parts.push(<span key="l" className="badge low">{s.low} Low</span>);
  if (s.check) parts.push(<span key="c" className="badge none">{s.check} to check</span>);
  if (parts.length === 0) return <span className="muted">No clauses found</span>;
  return <span className="pills">{parts}</span>;
}

export default function ContractsPage({ onOpen }) {
  const [contracts, setContracts] = useState([]);
  const [file, setFile] = useState(null);
  const [customer, setCustomer] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      setContracts(await listContracts());
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 3000);
    return () => clearInterval(timer);
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      await uploadContract(file, customer);
      setFile(null);
      e.target.reset();
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function onDelete(c) {
    if (!window.confirm(`Delete "${c.filename}" and all its findings?`)) return;
    try {
      await deleteContract(c.id);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  const count = (s) => contracts.filter((c) => c.status === s).length;

  return (
    <>
      <h1 className="page-title">My contracts</h1>
      <p className="page-sub">Upload a contract and review its key clauses. Only you can see your contracts.</p>

      <div className="stats">
        <div className="stat"><div className="n">{contracts.length}</div><div className="l">Total</div></div>
        <div className="stat"><div className="n" style={{ color: "var(--low)" }}>{count("done")}</div><div className="l">Done</div></div>
        <div className="stat"><div className="n" style={{ color: "var(--medium)" }}>{count("processing")}</div><div className="l">Processing</div></div>
        <div className="stat"><div className="n" style={{ color: "var(--high)" }}>{count("failed")}</div><div className="l">Failed</div></div>
      </div>

      <div className="card">
        <h3>Upload a contract</h3>
        <p className="privacy">
          Use public or sample contracts only. The text is sent to a hosted language model, and free tiers may keep it.
          Contracts are deleted after 7 days. Limit: 5 uploads per day.
        </p>
        <form onSubmit={onSubmit}>
          <label className="dropzone">
            <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files[0])} />
            {file ? <b>{file.name}</b> : <span><b>Click to choose a file</b><br />PDF, DOCX or TXT, up to 15 MB</span>}
          </label>

          <label className="field-label" htmlFor="party">Which party are you?</label>
          <p className="hint">
            Type the name as written in the contract. It helps judge risk from your side. Leave empty if unsure.
          </p>
          <input
            id="party"
            className="input"
            style={{ marginTop: 0 }}
            value={customer}
            onChange={(e) => setCustomer(e.target.value)}
          />

          <p style={{ margin: "14px 0 0" }}>
            <button className="btn" type="submit" disabled={!file || busy}>
              {busy ? "Uploading..." : "Review contract"}
            </button>
            {!file && <span className="helper">Choose a file to enable.</span>}
          </p>
        </form>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="card">
        <h3>History</h3>
        {contracts.length === 0 ? (
          <p className="muted">No contracts yet. Upload one above.</p>
        ) : (
          <table>
            <thead>
              <tr><th>ID</th><th>File</th><th>Uploaded</th><th>Status</th><th>Findings</th><th></th></tr>
            </thead>
            <tbody>
              {contracts.map((c) => (
                <tr key={c.id}>
                  <td className="muted">#{c.id}</td>
                  <td>{c.filename}</td>
                  <td className="muted">{new Date(c.created_at).toLocaleString()}</td>
                  <td>
                    <span className={`badge ${c.status}`}>
                      {c.status === "processing" && <span className="spinner" />}
                      {c.status}
                    </span>
                  </td>
                  <td><Findings c={c} /></td>
                  <td style={{ whiteSpace: "nowrap" }}>
                    {c.status === "done" && (
                      <button className="btn ghost sm" onClick={() => onOpen(c.id)}>Open</button>
                    )}{" "}
                    <button className="btn ghost sm reject on" onClick={() => onDelete(c)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
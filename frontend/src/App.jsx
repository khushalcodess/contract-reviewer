import { useEffect, useState } from "react";
import { listContracts, uploadContract } from "./api";
import Review from "./Review";

const NOTICE =
  "Decision support only. This is not legal advice. A person must check every finding.";

function ContractsPage({ onOpen }) {
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

  const count = (s) => contracts.filter((c) => c.status === s).length;

  return (
    <>
      <h1 className="page-title">Contracts</h1>
      <p className="page-sub">Upload a contract and review its key clauses.</p>

      <div className="stats">
        <div className="stat"><div className="n">{contracts.length}</div><div className="l">Total</div></div>
        <div className="stat"><div className="n" style={{ color: "var(--low)" }}>{count("done")}</div><div className="l">Done</div></div>
        <div className="stat"><div className="n" style={{ color: "var(--medium)" }}>{count("processing")}</div><div className="l">Processing</div></div>
        <div className="stat"><div className="n" style={{ color: "var(--high)" }}>{count("failed")}</div><div className="l">Failed</div></div>
      </div>

      <div className="card">
        <h3>Upload a contract</h3>
        <form onSubmit={onSubmit}>
          <label className="dropzone">
            <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files[0])} />
            {file ? <b>{file.name}</b> : <span><b>Click to choose a file</b><br />PDF, DOCX or TXT, up to 15 MB</span>}
          </label>
          <input
            className="input"
            placeholder="Your party name as written in the contract (optional)"
            value={customer}
            onChange={(e) => setCustomer(e.target.value)}
          />
          <p style={{ margin: "14px 0 0" }}>
            <button className="btn" type="submit" disabled={!file || busy}>
              {busy ? "Uploading..." : "Review contract"}
            </button>
          </p>
        </form>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="card">
        <h3>Your contracts</h3>
        {contracts.length === 0 ? (
          <p className="muted">No contracts yet. Upload one above.</p>
        ) : (
          <table>
            <thead>
              <tr><th>ID</th><th>File</th><th>Uploaded</th><th>Status</th><th></th></tr>
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
                  <td>
                    {c.status === "done" && (
                      <button className="btn ghost sm" onClick={() => onOpen(c.id)}>Open</button>
                    )}
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

export default function App() {
  const [page, setPage] = useState("contracts");
  const [openId, setOpenId] = useState(null);

  function go(p) {
    setPage(p);
    setOpenId(null);
  }

  let content;
  if (openId) {
    content = <Review id={openId} onBack={() => setOpenId(null)} />;
  } else if (page === "admin") {
    content = (
      <>
        <h1 className="page-title">Evaluation</h1>
        <div className="card muted">Metrics page comes in the next step.</div>
      </>
    );
  } else {
    content = <ContractsPage onOpen={setOpenId} />;
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="logo"><div className="logo-mark">⚖</div>Contract Reviewer</div>
        <button className={`nav-item ${page === "contracts" ? "active" : ""}`} onClick={() => go("contracts")}>
          Contracts
        </button>
        <button className={`nav-item ${page === "admin" ? "active" : ""}`} onClick={() => go("admin")}>
          Evaluation
        </button>
      </aside>
      <main className="main">
        <div className="notice">{NOTICE}</div>
        {content}
      </main>
    </div>
  );
}
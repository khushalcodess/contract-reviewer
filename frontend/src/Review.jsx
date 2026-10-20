import { useEffect, useRef, useState } from "react";
import { getFindings, getText, decide } from "./api";

export default function Review({ id, onBack }) {
  const [data, setData] = useState(null);
  const [text, setText] = useState("");
  const [focus, setFocus] = useState(null);
  const [error, setError] = useState("");
  const markRef = useRef(null);

  async function load() {
    try {
      setData(await getFindings(id));
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    load();
    getText(id).then(setText).catch((e) => setError(e.message));
  }, [id]);

  useEffect(() => {
    if (focus && markRef.current) markRef.current.scrollIntoView({ block: "center" });
  }, [focus]);

  async function onDecide(clause, decision) {
    try {
      await decide(id, clause, decision);
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p className="muted"><span className="spinner" />Loading...</p>;
  if (data.status !== "done")
    return (
      <div className="card">
        <button className="btn ghost sm" onClick={onBack}>← Back</button>
        <p>Status: {data.status}. {data.error || "Try again in a moment."}</p>
      </div>
    );

  const fs = data.findings;
  const risk = (r) => fs.filter((f) => f.status === "found" && f.finding?.risk_level === r).length;
  const notFound = fs.filter((f) => f.status === "not_found").length;
  const unverified = fs.filter((f) => f.status === "unverified").length;

  let shown;
  if (focus) {
    const [s, e] = focus;
    const a = Math.max(0, s - 1500);
    const b = Math.min(text.length, e + 1500);
    shown = (
      <>
        {text.slice(a, s)}
        <mark ref={markRef}>{text.slice(s, e)}</mark>
        {text.slice(e, b)}
      </>
    );
  } else {
    shown = text.slice(0, 4000);
  }

  return (
    <div>
      <div className="topbar">
        <button className="btn ghost sm" onClick={onBack}>← Back</button>
        <h1 className="page-title" style={{ margin: 0 }}>Contract #{id}</h1>
      </div>

      <div className="chips">
        <span className="chip"><b style={{ color: "var(--high)" }}>{risk("High")}</b>High</span>
        <span className="chip"><b style={{ color: "var(--medium)" }}>{risk("Medium")}</b>Medium</span>
        <span className="chip"><b style={{ color: "var(--low)" }}>{risk("Low")}</b>Low</span>
        <span className="chip"><b>{notFound}</b>Not found</span>
        {unverified > 0 && <span className="chip"><b>{unverified}</b>Review manually</span>}
      </div>

      <div className="review-grid">
        <div>
          {fs.map((f) => {
            const fd = f.finding || {};
            const level = (fd.risk_level || "").toLowerCase();
            return (
              <div key={f.clause} className={`clause ${f.status === "found" ? level : ""}`}>
                <div className="clause-head">
                  <h3>{f.clause}</h3>
                  {f.status === "found" && <span className={`badge ${level}`}>{fd.risk_level} risk</span>}
                  {f.status === "not_found" && <span className="badge none">Not found</span>}
                  {f.status === "unverified" && <span className="badge medium">Could not verify</span>}
                </div>

                {f.status === "found" && (
                  <>
                    <p style={{ margin: "0 0 4px" }}>{fd.explanation}</p>
                    <div className="label">Quote from the contract{f.page ? ` · page ${f.page}` : ""}</div>
                    <blockquote className="quote">{fd.cited_text}</blockquote>
                    <div className="label">Suggested safer wording</div>
                    <p className="redline">{fd.suggested_redline}</p>
                    <div className="actions">
                      <button className="btn ghost sm" onClick={() => setFocus([fd.citation_start, fd.citation_end])}>
                        Show in contract
                      </button>
                      <button className={`btn ghost sm accept ${f.decision === "accepted" ? "on" : ""}`} onClick={() => onDecide(f.clause, "accepted")}>
                        Accept
                      </button>
                      <button className={`btn ghost sm reject ${f.decision === "rejected" ? "on" : ""}`} onClick={() => onDecide(f.clause, "rejected")}>
                        Reject
                      </button>
                    </div>
                  </>
                )}
                {f.status === "unverified" && (
                  <p className="muted" style={{ margin: 0 }}>
                    The answer could not be checked against the contract. Review this clause manually.
                  </p>
                )}
                {f.status === "not_found" && (
                  <p className="muted" style={{ margin: 0, fontSize: 13 }}>Decided by: {f.decided_by}</p>
                )}
              </div>
            );
          })}
        </div>

        <div className="contract-panel">
          <header>Contract text</header>
          <div className="contract-body">{shown}</div>
        </div>
      </div>
    </div>
  );
}
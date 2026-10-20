const CLAUSES = [
  "Governing Law",
  "Renewal Term",
  "Notice Period To Terminate Renewal",
  "Termination For Convenience",
  "Non-Compete",
  "Cap On Liability",
  "Uncapped Liability",
  "Indemnification",
];

const STEPS = [
  ["1", "Upload", "Add a PDF, Word or text contract and tell us which party you are."],
  ["2", "Find the clauses", "The system searches the contract for 8 key clauses. If a clause is not there, it says so."],
  ["3", "Rate the risk", "Each clause gets a Low, Medium or High rating from your side, with a plain explanation."],
  ["4", "Check the proof", "Every finding quotes the exact words from the contract. Click to see them highlighted."],
];

export default function Landing({ onLogin, onSignup }) {
  return (
    <div className="landing">
      <header className="l-top">
        <div className="logo"><div className="logo-mark">⚖</div>Contract Reviewer</div>
        <div className="l-actions">
          <button className="btn ghost sm" onClick={onLogin}>Log in</button>
          <button className="btn sm" onClick={onSignup}>Sign up</button>
        </div>
      </header>

      <section className="l-hero">
        <span className="badge none">Decision support for contract review</span>
        <h1>Spot risky contract clauses before you sign</h1>
        <p>
          Upload a contract. Get the key clauses, a risk rating for each, the exact quote from the
          document, and safer wording you can suggest.
        </p>
        <div className="l-actions" style={{ justifyContent: "center" }}>
          <button className="btn" onClick={onSignup}>Get started</button>
          <button className="btn ghost" onClick={onLogin}>Log in</button>
        </div>
      </section>

      <section className="l-section">
        <h2>How it works</h2>
        <div className="l-grid">
          {STEPS.map(([n, title, text]) => (
            <div className="card" key={n}>
              <div className="l-num">{n}</div>
              <h3>{title}</h3>
              <p className="muted" style={{ margin: 0 }}>{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="l-section">
        <h2>The 8 clauses it checks</h2>
        <div className="pills" style={{ justifyContent: "center" }}>
          {CLAUSES.map((c) => (
            <span className="chip" key={c}>{c}</span>
          ))}
        </div>
      </section>

      <section className="l-section">
        <h2>Good to know</h2>
        <div className="l-grid two">
          <div className="card">
            <h3>Not legal advice</h3>
            <p className="muted" style={{ margin: 0 }}>
              This tool supports a human reviewer. A person must check every finding. Risk is judged
              from the customer's side, using simplified rules.
            </p>
          </div>
          <div className="card">
            <h3>Use sample contracts</h3>
            <p className="muted" style={{ margin: 0 }}>
              The text is sent to a hosted language model, and free tiers may keep it. Do not upload
              confidential contracts. Scanned PDFs are not supported yet.
            </p>
          </div>
        </div>
      </section>

      <footer className="l-foot">
        <button className="btn" onClick={onSignup}>Create a free account</button>
      </footer>
    </div>
  );
}
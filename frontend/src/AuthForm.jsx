import { useState } from "react";
import { login, signup } from "./api";

export default function AuthForm({ mode, onDone, onSwitch, onBack }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const isSignup = mode === "signup";

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    if (isSignup && password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    setBusy(true);
    try {
      await (isSignup ? signup : login)(email, password);
      onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="card auth-card">
        <button className="btn ghost sm" onClick={onBack}>← Back</button>
        <h2 style={{ margin: "16px 0 4px" }}>{isSignup ? "Create your account" : "Welcome back"}</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          {isSignup ? "Sign up to review your contracts." : "Log in to see your contracts."}
        </p>
        <form onSubmit={onSubmit}>
          <label className="field-label" htmlFor="email">Email</label>
          <input
            id="email" className="input" style={{ marginTop: 0 }} type="email"
            autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required
          />
          <label className="field-label" htmlFor="password">Password</label>
          {isSignup && <p className="hint">At least 8 characters.</p>}
          <input
            id="password" className="input" style={{ marginTop: 0 }} type="password"
            autoComplete={isSignup ? "new-password" : "current-password"}
            value={password} onChange={(e) => setPassword(e.target.value)} required
          />
          {error && <p className="error">{error}</p>}
          <p style={{ margin: "16px 0 0" }}>
            <button className="btn" type="submit" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Please wait..." : isSignup ? "Sign up" : "Log in"}
            </button>
          </p>
        </form>
        <p className="muted" style={{ textAlign: "center", marginBottom: 0 }}>
          {isSignup ? "Already have an account? " : "New here? "}
          <button className="link" onClick={onSwitch}>{isSignup ? "Log in" : "Sign up"}</button>
        </p>
      </div>
    </div>
  );
}
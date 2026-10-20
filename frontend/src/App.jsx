import { useEffect, useState } from "react";
import { clearToken, getToken } from "./api";
import AuthForm from "./AuthForm";
import ContractsPage from "./ContractsPage";
import Landing from "./Landing";
import Review from "./Review";

const NOTICE =
  "Decision support only, not legal advice. A person must check every finding. Risk is judged from the customer's side.";

export default function App() {
  const [token, setTok] = useState(getToken());
  const [view, setView] = useState("landing");
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    const out = () => {
      setTok(null);
      setOpenId(null);
      setView("login");
    };
    window.addEventListener("auth-expired", out);
    return () => window.removeEventListener("auth-expired", out);
  }, []);

  function logout() {
    clearToken();
    setTok(null);
    setOpenId(null);
    setView("landing");
  }

  if (!token) {
    if (view === "login" || view === "signup") {
      return (
        <AuthForm
          mode={view}
          onDone={() => setTok(getToken())}
          onSwitch={() => setView(view === "login" ? "signup" : "login")}
          onBack={() => setView("landing")}
        />
      );
    }
    return <Landing onLogin={() => setView("login")} onSignup={() => setView("signup")} />;
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="logo"><div className="logo-mark">⚖</div>Contract Reviewer</div>
        <button className="nav-item active" onClick={() => setOpenId(null)}>My contracts</button>
        <button className="nav-item" onClick={logout}>Log out</button>
      </aside>
      <main className="main">
        <div className="notice">{NOTICE}</div>
        {openId ? (
          <Review id={openId} onBack={() => setOpenId(null)} />
        ) : (
          <ContractsPage onOpen={setOpenId} />
        )}
      </main>
    </div>
  );
}
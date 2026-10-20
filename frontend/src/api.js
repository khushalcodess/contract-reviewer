const API = import.meta.env.PROD ? "/api" : "http://localhost:8000";
const KEY = "token";

export const getToken = () => localStorage.getItem(KEY);
export const clearToken = () => localStorage.removeItem(KEY);

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const r = await fetch(`${API}${path}`, { ...options, headers });
  if (r.status === 401 && token) {
    clearToken();
    window.dispatchEvent(new Event("auth-expired"));
  }
  return r;
}

async function authCall(path, email, password) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  let data = {};
  try {
    data = await r.json();
  } catch {
    /* no body */
  }
  if (!r.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : "Something went wrong");
  }
  localStorage.setItem(KEY, data.token);
}

export const signup = (email, password) => authCall("/auth/signup", email, password);
export const login = (email, password) => authCall("/auth/login", email, password);

export async function listContracts() {
  const r = await request("/contracts");
  if (!r.ok) throw new Error("Cannot load contracts");
  return r.json();
}

export async function uploadContract(file, customer) {
  const form = new FormData();
  form.append("file", file);
  form.append("customer", customer);
  const r = await request("/contracts", { method: "POST", body: form });
  let data = {};
  try {
    data = await r.json();
  } catch {
    /* no body */
  }
  if (!r.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Upload failed");
  return data;
}

export async function deleteContract(id) {
  const r = await request(`/contracts/${id}`, { method: "DELETE" });
  if (!r.ok) throw new Error("Cannot delete contract");
}

export async function getFindings(id) {
  const r = await request(`/contracts/${id}/findings`);
  if (!r.ok) throw new Error("Cannot load findings");
  return r.json();
}

export async function getText(id) {
  const r = await request(`/contracts/${id}/text`);
  if (!r.ok) throw new Error("Cannot load text");
  return (await r.json()).text;
}

export async function decide(id, clause, decision) {
  const r = await request(
    `/contracts/${id}/findings/${encodeURIComponent(clause)}/decision`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    }
  );
  if (!r.ok) throw new Error("Cannot save decision");
}
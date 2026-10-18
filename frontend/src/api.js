const API = "http://localhost:8000";

export async function listContracts() {
  const r = await fetch(`${API}/contracts`);
  if (!r.ok) throw new Error("Cannot load contracts");
  return r.json();
}

export async function uploadContract(file, customer) {
  const form = new FormData();
  form.append("file", file);
  form.append("customer", customer);
  const r = await fetch(`${API}/contracts`, { method: "POST", body: form });
  const data = await r.json();
  if (!r.ok) throw new Error(data.detail || "Upload failed");
  return data;
}
export async function getFindings(id) {
  const r = await fetch(`${API}/contracts/${id}/findings`);
  if (!r.ok) throw new Error("Cannot load findings");
  return r.json();
}

export async function getText(id) {
  const r = await fetch(`${API}/contracts/${id}/text`);
  if (!r.ok) throw new Error("Cannot load text");
  return (await r.json()).text;
}

export async function decide(id, clause, decision) {
  const r = await fetch(
    `${API}/contracts/${id}/findings/${encodeURIComponent(clause)}/decision`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    }
  );
  if (!r.ok) throw new Error("Cannot save decision");
}
export async function deleteContract(id) {
  const r = await fetch(`${API}/contracts/${id}`, { method: "DELETE" });
  if (!r.ok) throw new Error("Cannot delete contract");
}
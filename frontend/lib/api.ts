const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function submitClaim(data: {
  complaint_text: string;
  contract_clauses?: string;
}): Promise<import("./types").ClaimAccepted> {
  const payload: Record<string, string> = {
    complaint_text: data.complaint_text,
  };
  if (data.contract_clauses && data.contract_clauses.trim()) {
    payload.contract_clauses = data.contract_clauses;
  }
  const res = await fetch(`${BASE_URL}/api/claims`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to submit claim: ${res.status}`);
  return res.json();
}

export async function getClaim(
  claimId: string,
): Promise<import("./types").ClaimRead> {
  const res = await fetch(`${BASE_URL}/api/claims/${claimId}`);
  if (!res.ok) throw new Error(`Failed to get claim: ${res.status}`);
  return res.json();
}

export async function listClaims(): Promise<import("./types").ClaimSummary[]> {
  const res = await fetch(`${BASE_URL}/api/claims`);
  if (!res.ok) throw new Error(`Failed to list claims: ${res.status}`);
  return res.json();
}

export async function deleteClaim(claimId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/claims/${claimId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Failed to delete claim: ${res.status}`);
}

export async function getDocuments(): Promise<
  import("./types").DocumentMeta[]
> {
  const res = await fetch(`${BASE_URL}/api/documents`);
  if (!res.ok) throw new Error(`Failed to list documents: ${res.status}`);
  return res.json();
}

export function documentUrl(filename: string): string {
  return `${BASE_URL}/api/documents/${encodeURIComponent(filename)}`;
}

export async function getClauses(): Promise<import("./types").ClausesDoc[]> {
  const res = await fetch(`${BASE_URL}/api/clauses`);
  if (!res.ok) throw new Error(`Failed to get clauses: ${res.status}`);
  return res.json();
}

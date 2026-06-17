const BASE_URL = "http://localhost:8000";

export async function submitClaim(data: {
  complaint_text: string;
  contract_clauses: string;
}): Promise<import("./types").ClaimAccepted> {
  const res = await fetch(`${BASE_URL}/api/claims`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
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

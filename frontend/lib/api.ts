const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function handle(res: Response) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export type DocType = "cv" | "transcript" | "gre" | "toefl_ielts" | "research_paper" | "sop" | "other";

export type DocumentSummary = {
  id: string;
  doc_type: DocType;
  filename: string | null;
  created_at: string | null;
};

export async function uploadDocument(file: File, docType: DocType, profileId?: string | null) {
  const form = new FormData();
  form.append("file", file);
  form.append("doc_type", docType);
  if (profileId) form.append("profile_id", profileId);
  const res = await fetch(`${API_BASE}/api/profile/upload`, { method: "POST", body: form });
  return handle(res) as Promise<{ profile_id: string; profile: any; documents: DocumentSummary[] }>;
}

// Backward-compatible alias for a plain CV upload.
export async function uploadCV(file: File) {
  return uploadDocument(file, "cv");
}

export async function deleteDocument(profileId: string, documentId: string) {
  const res = await fetch(`${API_BASE}/api/profile/${profileId}/documents/${documentId}`, {
    method: "DELETE",
  });
  return handle(res) as Promise<{ profile_id: string; profile: any; documents: DocumentSummary[] }>;
}

export async function updateProfile(profileId: string, edits: Record<string, any>) {
  const res = await fetch(`${API_BASE}/api/profile/${profileId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(edits),
  });
  return handle(res) as Promise<{ profile_id: string; profile: any; documents: DocumentSummary[] }>;
}

export async function retrieveProgram(params: {
  university_name: string;
  program_name: string;
  seed_url?: string;
  manual_text?: string;
}) {
  const res = await fetch(`${API_BASE}/api/program/retrieve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handle(res);
}

export async function runAnalysis(profile_id: string, program_id: string) {
  const res = await fetch(`${API_BASE}/api/analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile_id, program_id }),
  });
  return handle(res);
}

export async function getAnalysis(analysis_id: string) {
  const res = await fetch(`${API_BASE}/api/analysis/${analysis_id}`);
  return handle(res);
}

export async function getProfile(profile_id: string) {
  const res = await fetch(`${API_BASE}/api/profile/${profile_id}`);
  return handle(res);
}

export type JobStatus = "pending" | "retrieving" | "analyzing" | "done" | "error";

export async function createJob(params: {
  profile_id: string;
  university_name: string;
  program_name: string;
  seed_url?: string;
  manual_text?: string;
}) {
  const res = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handle(res);
}

export async function getJob(job_id: string): Promise<{
  job_id: string;
  status: JobStatus;
  program_id: string | null;
  analysis_id: string | null;
  error: string | null;
}> {
  const res = await fetch(`${API_BASE}/api/jobs/${job_id}`);
  return handle(res);
}

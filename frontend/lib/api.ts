const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

async function handle(res: Response) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      body.detail || `Request failed (${res.status})`
    );
  }

  return res.json();
}

/* =========================================================
   PROFILE
   ========================================================= */

export async function uploadCV(file: File) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(
    `${API_BASE}/api/profile/upload`,
    {
      method: "POST",
      body: form,
    }
  );

  return handle(res);
}

export async function getProfile(profile_id: string) {
  const res = await fetch(
    `${API_BASE}/api/profile/${profile_id}`
  );

  return handle(res);
}

/* =========================================================
   PROGRAM RETRIEVAL
   ========================================================= */

export async function retrieveProgram(params: {
  university_name: string;
  program_name: string;
  seed_url?: string;
  manual_text?: string;
}) {
  const res = await fetch(
    `${API_BASE}/api/program/retrieve`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    }
  );

  return handle(res);
}

/* =========================================================
   ANALYSIS
   ========================================================= */

export async function runAnalysis(
  profile_id: string,
  program_id: string
) {
  const res = await fetch(
    `${API_BASE}/api/analysis`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        profile_id,
        program_id,
      }),
    }
  );

  return handle(res);
}

export async function getAnalysis(
  analysis_id: string
) {
  const res = await fetch(
    `${API_BASE}/api/analysis/${analysis_id}`
  );

  return handle(res);
}

/* =========================================================
   COMPATIBILITY LAYER FOR NEW FRONTEND
   ========================================================= */

/*
  The redesigned frontend expects createJob/getJob.

  The existing FastAPI backend does NOT have /api/jobs.

  Instead of modifying the backend, createJob runs the existing
  pipeline:

  Program Retrieval
        ↓
  Analysis

  and returns a job-shaped response to keep the new UI working.
*/

export type JobStatus =
  | "pending"
  | "retrieving"
  | "analyzing"
  | "done"
  | "error";

export async function createJob(params: {
  profile_id: string;
  university_name: string;
  program_name: string;
  seed_url?: string;
  manual_text?: string;
}) {
  try {
    // Step 1 — retrieve university/program information
    const program = await retrieveProgram({
      university_name: params.university_name,
      program_name: params.program_name,
      seed_url: params.seed_url,
      manual_text: params.manual_text,
    });

    const programId =
      program.program_id ||
      program.id;

    if (!programId) {
      throw new Error(
        "Program retrieval succeeded but no program_id was returned."
      );
    }

    // Step 2 — run applicant/program analysis
    const analysis = await runAnalysis(
      params.profile_id,
      programId
    );

    const analysisId =
      analysis.analysis_id ||
      analysis.id;

    if (!analysisId) {
      throw new Error(
        "Analysis succeeded but no analysis_id was returned."
      );
    }

    /*
      Return the shape expected by Claude's redesigned UI.
      No /api/jobs backend endpoint is required.
    */
    return {
      job_id: analysisId,
      status: "done" as JobStatus,
      program_id: programId,
      analysis_id: analysisId,
      error: null,
    };

  } catch (error) {
    console.error(
      "GradPilot analysis pipeline failed:",
      error
    );

    throw error;
  }
}

/*
  Compatibility function.

  createJob currently completes the real backend pipeline before
  returning, so the analysis ID doubles as the temporary job ID.
*/
export async function getJob(job_id: string): Promise<{
  job_id: string;
  status: JobStatus;
  program_id: string | null;
  analysis_id: string | null;
  error: string | null;
}> {
  try {
    await getAnalysis(job_id);

    return {
      job_id,
      status: "done",
      program_id: null,
      analysis_id: job_id,
      error: null,
    };

  } catch {
    return {
      job_id,
      status: "analyzing",
      program_id: null,
      analysis_id: null,
      error: null,
    };
  }
}
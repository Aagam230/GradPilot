"use client";
import { createContext, useContext, useEffect, useState, ReactNode } from "react";

import { DocumentSummary } from "./api";

export type StudentProfileData = Record<string, any>;

export type LastJob = {
  jobId: string;
  universityName: string;
  programName: string;
  analysisId?: string | null;
};

type AppState = {
  profileId: string | null;
  profile: StudentProfileData | null;
  documents: DocumentSummary[];
  fileName: string | null;
  lastJob: LastJob | null;
  setProfile: (id: string, profile: StudentProfileData, documents?: DocumentSummary[], fileName?: string) => void;
  clearProfile: () => void;
  setLastJob: (job: LastJob | null) => void;
  setDocuments: (docs: DocumentSummary[]) => void;
};

const AppStateContext = createContext<AppState | null>(null);

const STORAGE_KEY = "gradpilot.profile";

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [profile, setProfileData] = useState<StudentProfileData | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const [lastJob, setLastJobState] = useState<LastJob | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        setProfileId(parsed.profileId ?? null);
        setProfileData(parsed.profile ?? null);
        setDocuments(parsed.documents ?? []);
        setFileName(parsed.fileName ?? null);
        setLastJobState(parsed.lastJob ?? null);
      }
    } catch {}
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ profileId, profile, documents, fileName, lastJob })
    );
  }, [profileId, profile, documents, fileName, lastJob, hydrated]);

  function setProfile(id: string, p: StudentProfileData, docs?: DocumentSummary[], fn?: string) {
    setProfileId(id);
    setProfileData(p);
    if (docs) setDocuments(docs);
    if (fn) setFileName(fn);
  }

  function clearProfile() {
    setProfileId(null);
    setProfileData(null);
    setDocuments([]);
    setFileName(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  function setLastJob(job: LastJob | null) {
    setLastJobState(job);
  }

  return (
    <AppStateContext.Provider
      value={{
        profileId,
        profile,
        documents,
        fileName,
        lastJob,
        setProfile,
        clearProfile,
        setLastJob,
        setDocuments,
      }}
    >
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState() {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error("useAppState must be used within AppStateProvider");
  return ctx;
}

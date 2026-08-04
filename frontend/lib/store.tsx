"use client";
import { createContext, useContext, useEffect, useState, ReactNode } from "react";

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
  fileName: string | null;
  lastJob: LastJob | null;
  setProfile: (id: string, profile: StudentProfileData, fileName?: string) => void;
  clearProfile: () => void;
  setLastJob: (job: LastJob | null) => void;
};

const AppStateContext = createContext<AppState | null>(null);

const STORAGE_KEY = "gradpilot.profile";

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [profile, setProfileData] = useState<StudentProfileData | null>(null);
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
        setFileName(parsed.fileName ?? null);
        setLastJobState(parsed.lastJob ?? null);
      }
    } catch {}
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ profileId, profile, fileName, lastJob }));
  }, [profileId, profile, fileName, lastJob, hydrated]);

  function setProfile(id: string, p: StudentProfileData, fn?: string) {
    setProfileId(id);
    setProfileData(p);
    if (fn) setFileName(fn);
  }

  function clearProfile() {
    setProfileId(null);
    setProfileData(null);
    setFileName(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  function setLastJob(job: LastJob | null) {
    setLastJobState(job);
  }

  return (
    <AppStateContext.Provider
      value={{ profileId, profile, fileName, lastJob, setProfile, clearProfile, setLastJob }}
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

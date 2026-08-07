"use client";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  FileText,
  GraduationCap,
  FlaskConical,
  Languages,
  BookOpen,
  PenLine,
  CheckCircle2,
  Info,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { DocumentSlot } from "@/components/DocumentSlot";
import { uploadDocument, deleteDocument, DocType } from "@/lib/api";
import { useAppState } from "@/lib/store";

const DOC_SLOTS: { docType: DocType; label: string; icon: any; required?: boolean }[] = [
  { docType: "cv", label: "CV / Resume", icon: FileText, required: true },
  { docType: "transcript", label: "Transcript", icon: GraduationCap },
  { docType: "gre", label: "GRE score", icon: FlaskConical },
  { docType: "toefl_ielts", label: "TOEFL / IELTS", icon: Languages },
  { docType: "research_paper", label: "Research paper", icon: BookOpen },
  { docType: "sop", label: "Statement of Purpose", icon: PenLine },
];

export default function DocumentsPage() {
  const router = useRouter();
  const { profileId, profile, documents, setProfile } = useAppState();

  async function handleUpload(file: File, docType: DocType) {
    const data = await uploadDocument(file, docType, profileId);
    setProfile(data.profile_id, data.profile, data.documents, file.name);
  }

  async function handleRemove(docId: string) {
    if (!profileId) return;
    const data = await deleteDocument(profileId, docId);
    setProfile(data.profile_id, data.profile, data.documents);
  }

  const hasCv = documents.some((d) => d.doc_type === "cv");

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Documents</h1>
      <p className="text-ink-muted mb-8">
        Upload every document you have. Admissions committees judge a full application packet, not
        a resume alone — GradPilot builds one profile from everything you provide.
      </p>

      <div className="grid lg:grid-cols-[1.15fr_0.85fr] gap-6">
        <Card className="p-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {DOC_SLOTS.map((slot) => (
              <DocumentSlot
                key={slot.docType}
                icon={slot.icon}
                label={slot.label}
                docType={slot.docType}
                required={slot.required}
                existing={documents.find((d) => d.doc_type === slot.docType)}
                onUpload={handleUpload}
                onRemove={handleRemove}
              />
            ))}
          </div>

          <div className="mt-5 flex items-start gap-2 text-xs text-ink-faint">
            <Info size={13} className="mt-0.5 shrink-0" />
            <span>
              Only a CV is required to start. Re-uploading a document type replaces the previous
              version. Scanned PDFs are read automatically with OCR. Nothing is fabricated for
              documents you haven&apos;t uploaded.
            </span>
          </div>

          {hasCv && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 flex items-center justify-between gap-4 rounded-xl bg-likely/10 border border-likely/25 px-4 py-3"
            >
              <div className="flex items-center gap-2 text-sm text-likely">
                <CheckCircle2 size={16} />
                Profile built from {documents.length} document{documents.length === 1 ? "" : "s"}
              </div>
              <Button size="sm" onClick={() => router.push("/app/profile")}>
                Review profile
              </Button>
            </motion.div>
          )}
        </Card>

        <Card className="p-6">
          <h2 className="text-sm font-medium text-ink mb-3">Why more than a resume?</h2>
          <ul className="space-y-3 text-sm text-ink-muted leading-relaxed">
            <li>
              <span className="text-ink font-medium">Transcript</span> — gives an authoritative GPA
              and coursework, more reliable than what&apos;s self-reported on a CV.
            </li>
            <li>
              <span className="text-ink font-medium">GRE / TOEFL / IELTS</span> — official scores,
              used instead of guessing from a resume line.
            </li>
            <li>
              <span className="text-ink font-medium">Research papers</span> — grounds your research
              fit in the actual work, not just a title.
            </li>
            <li>
              <span className="text-ink font-medium">Statement of Purpose</span> — captures your
              goals and motivation, which admissions committees weigh directly.
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
}

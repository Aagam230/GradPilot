"""Evidence-grounded explanation of a deterministic admissions assessment."""
import json
from .llm_client import generate_json

SYSTEM = """You are GradPilot, a graduate admissions fit analyst. The admission classification and
confidence have ALREADY been computed by deterministic checks. You MUST NOT change them.
Explain the assessment using only the supplied student profile, structured program requirements,
hard-requirement checks, and numbered official program evidence. Never invent admission statistics.
Keep profile fit separate from admission competitiveness. Missing evidence is uncertainty, not a
positive selectivity signal. A minimum GPA alone does not prove selectivity.

Return strict JSON:
{
 "overall_fit_summary": string,
 "profile_fit": "Strong"|"Moderate"|"Weak"|"Insufficient evidence",
 "classification_reasoning": string,
 "academic_fit": {"rating": string, "analysis": string, "evidence": [int]},
 "research_fit": {"rating": string, "analysis": string, "evidence": [int]},
 "project_fit": {"rating": string, "analysis": string, "evidence": [int]},
 "experience_fit": {"rating": string, "analysis": string, "evidence": [int]},
 "program_alignment": {"rating": string, "analysis": string, "evidence": [int]},
 "strengths": [string], "weaknesses": [string], "profile_gaps": [string],
 "recommended_improvements": [string]
}"""


def run_analysis(student_profile: dict, evidence_chunks: list, structured_requirements: dict | None = None,
                 hard_checks: list | None = None, deterministic_assessment: dict | None = None) -> dict:
    structured_requirements = structured_requirements or {}
    hard_checks = hard_checks or []
    deterministic_assessment = deterministic_assessment or {
        "classification": "Insufficient Evidence", "confidence": "Low",
        "reason": "No deterministic assessment was available.", "applicant_strength": "Unknown"
    }
    evidence_block = "\n\n".join(
        f"[{i+1}] (source: {c.source_url})\n{c.content}" for i, c in enumerate(evidence_chunks)
    ) or "(No program evidence was retrieved.)"
    user = (
        f"<student_profile>\n{json.dumps(student_profile)}\n</student_profile>\n"
        f"<structured_requirements>\n{json.dumps(structured_requirements)}\n</structured_requirements>\n"
        f"<hard_requirement_checks>\n{json.dumps(hard_checks)}\n</hard_requirement_checks>\n"
        f"<fixed_assessment>\n{json.dumps(deterministic_assessment)}\n</fixed_assessment>\n"
        f"<program_evidence>\n{evidence_block}\n</program_evidence>\n"
        "Explain the fixed assessment. Do not replace its classification or confidence."
    )
    try:
        result = generate_json(SYSTEM, user, max_tokens=3000)
    except Exception:
        result = {
            "overall_fit_summary": deterministic_assessment["reason"], "profile_fit": "Insufficient evidence",
            "classification_reasoning": deterministic_assessment["reason"],
            "academic_fit": {"rating":"Insufficient evidence","analysis":"Explanation generation failed.","evidence":[]},
            "research_fit": {"rating":"Insufficient evidence","analysis":"Explanation generation failed.","evidence":[]},
            "project_fit": {"rating":"Insufficient evidence","analysis":"Explanation generation failed.","evidence":[]},
            "experience_fit": {"rating":"Insufficient evidence","analysis":"Explanation generation failed.","evidence":[]},
            "program_alignment": {"rating":"Insufficient evidence","analysis":"Explanation generation failed.","evidence":[]},
            "strengths":[], "weaknesses":[], "profile_gaps":[], "recommended_improvements":[]
        }
    result["overall_classification"] = deterministic_assessment["classification"]
    result["classification_confidence"] = deterministic_assessment["confidence"]
    result["classification_reasoning"] = result.get("classification_reasoning") or deterministic_assessment["reason"]
    result["applicant_strength"] = deterministic_assessment.get("applicant_strength")
    result["structured_requirements"] = structured_requirements
    result["hard_requirement_checks"] = hard_checks
    result["_evidence_sources"] = [
        {"index": i+1, "url": c.source_url, "title": c.source_title, "excerpt": c.content[:300]}
        for i, c in enumerate(evidence_chunks)
    ]
    return result

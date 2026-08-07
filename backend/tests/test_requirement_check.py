from app.services.requirement_check import check_requirements


def test_gre_below_minimum_flagged():
    profile = {"test_scores": [{"test": "GRE", "score": "314"}], "education": [{"gpa": "3.6"}]}
    reqs = {"gre_minimum": 320, "minimum_gpa": 3.0, "selectivity_evidence": []}
    result = check_requirements(profile, reqs)

    assert result["any_hard_failure"] is True
    gre_check = next(c for c in result["checks"] if c["requirement"] == "Minimum GRE")
    assert gre_check["meets"] is False
    assert gre_check["applicant_value"] == 314.0
    assert gre_check["required"] == 320


def test_all_requirements_met_no_failure():
    profile = {"test_scores": [{"test": "GRE", "score": "325"}], "education": [{"gpa": "3.8"}]}
    reqs = {"gre_minimum": 320, "minimum_gpa": 3.5, "selectivity_evidence": []}
    result = check_requirements(profile, reqs)

    assert result["any_hard_failure"] is False
    assert all(c["meets"] is True for c in result["checks"])


def test_missing_applicant_data_flagged_unknown_not_failure():
    profile = {"test_scores": [], "education": [{"gpa": "3.8"}]}
    reqs = {"gre_minimum": 320, "minimum_gpa": 3.0, "selectivity_evidence": []}
    result = check_requirements(profile, reqs)

    gre_check = next(c for c in result["checks"] if c["requirement"] == "Minimum GRE")
    assert gre_check["meets"] is None
    assert gre_check["applicant_value"] is None
    assert result["any_unknown_applicant_value"] is True
    assert result["any_hard_failure"] is False  # unknown is not the same as failing


def test_no_stated_requirements_produces_no_checks():
    profile = {"test_scores": [{"test": "GRE", "score": "314"}], "education": [{"gpa": "3.6"}]}
    reqs = {"selectivity_evidence": []}  # nothing stated
    result = check_requirements(profile, reqs)

    assert result["checks"] == []
    assert result["any_hard_failure"] is False


def test_has_selectivity_evidence_flag():
    reqs_with = {"selectivity_evidence": ["Acceptance rate ~6%"]}
    reqs_without = {"selectivity_evidence": []}
    assert check_requirements({}, reqs_with)["has_selectivity_evidence"] is True
    assert check_requirements({}, reqs_without)["has_selectivity_evidence"] is False


def test_toefl_and_ielts_checks():
    profile = {"test_scores": [{"test": "TOEFL", "score": "85"}, {"test": "IELTS", "score": "7.0"}]}
    reqs = {"toefl_minimum": 90, "ielts_minimum": 6.5, "selectivity_evidence": []}
    result = check_requirements(profile, reqs)

    toefl = next(c for c in result["checks"] if c["requirement"] == "Minimum TOEFL")
    ielts = next(c for c in result["checks"] if c["requirement"] == "Minimum IELTS")
    assert toefl["meets"] is False  # 85 < 90
    assert ielts["meets"] is True   # 7.0 >= 6.5
    assert result["any_hard_failure"] is True

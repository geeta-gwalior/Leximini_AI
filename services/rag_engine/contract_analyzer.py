import re
from typing import Dict, List, Any

class ContractRiskAnalyzer:
    """
    Automated Contract Risk & Clause Scanner for Indian Legal Agreements
    (Rent Agreements, Employment Contracts, NDAs, Service Agreements).
    """

    def analyze_contract(self, text: str, doc_type: str = "auto") -> Dict[str, Any]:
        text_lower = text.lower()
        if doc_type == "auto":
            if any(w in text_lower for w in ["rent", "tenant", "landlord", "lease", "lessor", "premises"]):
                doc_type = "Rent Agreement"
            elif any(w in text_lower for w in ["employee", "employer", "salary", "probation", "employment"]):
                doc_type = "Employment Contract"
            elif any(w in text_lower for w in ["confidential", "disclose", "receiving party", "disclosing party", "nda"]):
                doc_type = "Non-Disclosure Agreement (NDA)"
            else:
                doc_type = "General Commercial Agreement"

        risks: List[Dict[str, str]] = []
        clause_checks: List[Dict[str, Any]] = []

        if doc_type == "Rent Agreement":
            # 1. Lock-in Period Check
            has_lockin = bool(re.search(r"lock-?in", text_lower))
            clause_checks.append({"clause": "Lock-in Period Clause", "present": has_lockin, "severity": "Medium"})
            if not has_lockin:
                risks.append({"title": "Missing Lock-in Period Clause", "severity": "Medium", "impact": "Either party may terminate prematurely without financial safety buffer."})

            # 2. Security Deposit Refund Check
            has_deposit_refund = bool(re.search(r"deposit.*refund|refund.*deposit|deduction", text_lower))
            clause_checks.append({"clause": "Security Deposit Refund Timeline", "present": has_deposit_refund, "severity": "High"})
            if not has_deposit_refund:
                risks.append({"title": "Unclear Security Deposit Refund Terms", "severity": "High", "impact": "No mandatory deadline (e.g. 7-15 days) specified for returning security deposit upon vacating."})

            # 3. Notice Period Check
            has_notice = bool(re.search(r"notice period|days notice|month notice", text_lower))
            clause_checks.append({"clause": "Termination Notice Period", "present": has_notice, "severity": "High"})
            if not has_notice:
                risks.append({"title": "Missing Termination Notice Clause", "severity": "High", "impact": "Ambiguity on notice timeline required before vacating or requesting eviction."})

            # 4. Stamp Duty & Registration Check
            has_registration = bool(re.search(r"registration|sub-registrar|stamp duty|registered", text_lower))
            clause_checks.append({"clause": "Stamp Duty & Registration Compliance", "present": has_registration, "severity": "High"})
            if not has_registration:
                risks.append({"title": "Unregistered / Non-stamped Agreement Risk", "severity": "High", "impact": "Under Section 17 Registration Act 1908, leases over 11 months are inadmissible in court unless registered."})

            # 5. Maintenance & Repair Duties
            has_maintenance = bool(re.search(r"maintenance|repair|painting|damage", text_lower))
            clause_checks.append({"clause": "Maintenance & Utility Responsibility", "present": has_maintenance, "severity": "Low"})

        elif doc_type == "Employment Contract":
            has_non_compete = bool(re.search(r"non-?compete|restraint of trade", text_lower))
            if has_non_compete:
                risks.append({"title": "Post-Employment Non-Compete Risk", "severity": "High", "impact": "Under Section 27 Indian Contract Act 1872, post-employment non-compete clauses are generally void in India."})

            has_ip = bool(re.search(r"intellectual property|invention|work for hire", text_lower))
            clause_checks.append({"clause": "IP Assignment Clause", "present": has_ip, "severity": "Medium"})

            has_notice = bool(re.search(r"notice period|payment in lieu", text_lower))
            clause_checks.append({"clause": "Notice Period & Buyout", "present": has_notice, "severity": "High"})

        else: # General NDA / Commercial Agreement
            has_governing_law = bool(re.search(r"governing law|jurisdiction|courts at", text_lower))
            clause_checks.append({"clause": "Jurisdiction & Governing Law", "present": has_governing_law, "severity": "High"})
            if not has_governing_law:
                risks.append({"title": "Missing Governing Law & Jurisdiction", "severity": "High", "impact": "Disputes may be subjected to ambiguous court jurisdictions."})

            has_arbitration = bool(re.search(r"arbitration|mediat", text_lower))
            clause_checks.append({"clause": "Arbitration & Dispute Resolution", "present": has_arbitration, "severity": "Medium"})

        # Risk Score Calculation (0-100 scale, lower is safer)
        high_count = sum(1 for r in risks if r["severity"] == "High")
        med_count = sum(1 for r in risks if r["severity"] == "Medium")
        score = min(100, (high_count * 30) + (med_count * 15))
        safety_rating = "Low Risk 🟢" if score < 25 else ("Moderate Risk 🟡" if score < 60 else "High Risk 🔴")

        return {
            "document_type": doc_type,
            "risk_score": score,
            "safety_rating": safety_rating,
            "total_clauses_checked": len(clause_checks),
            "missing_critical_clauses": [c["clause"] for c in clause_checks if not c["present"] and c["severity"] in ["High", "Medium"]],
            "clause_checks": clause_checks,
            "identified_risks": risks,
            "summary_recommendation": f"Agreement analyzed as '{doc_type}'. Identified {len(risks)} potential risk areas requiring legal amendment."
        }

contract_analyzer = ContractRiskAnalyzer()

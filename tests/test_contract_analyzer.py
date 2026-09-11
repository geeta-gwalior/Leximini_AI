import pytest
from services.rag_engine.contract_analyzer import contract_analyzer

def test_contract_risk_analyzer_rent_agreement():
    sample_contract = """
    This Rent Agreement is made between Landlord and Tenant for premises Flat 101.
    The monthly rent shall be Rs 20000.
    """
    result = contract_analyzer.analyze_contract(sample_contract, doc_type="Rent Agreement")
    assert isinstance(result, dict)
    assert result["document_type"] == "Rent Agreement"
    assert "risk_score" in result
    assert len(result["clause_checks"]) > 0
    assert len(result["identified_risks"]) > 0

def test_contract_risk_analyzer_nda():
    sample_nda = """
    Non-Disclosure Agreement between Party A and Party B.
    All confidential information shall be kept secret.
    Governing law shall be laws of India under courts at Delhi.
    Arbitration shall apply.
    """
    result = contract_analyzer.analyze_contract(sample_nda, doc_type="auto")
    assert result["document_type"] == "Non-Disclosure Agreement (NDA)"
    assert result["risk_score"] < 50

import pytest
from services.rag_engine.document_drafter import document_drafter

def test_draft_rent_agreement():
    draft = document_drafter.draft_rent_agreement(
        landlord_name="Rajesh Sharma",
        tenant_name="Amit Kumar",
        property_address="Bandra, Mumbai",
        monthly_rent="30000"
    )
    assert "RESIDENTIAL LEASE / RENT AGREEMENT" in draft
    assert "Rajesh Sharma" in draft
    assert "30000" in draft
    assert "Registration Act" in draft

def test_draft_legal_notice():
    notice = document_drafter.draft_legal_notice(
        sender_name="Advocate Roy",
        client_name="Apex Ltd",
        recipient_name="Suresh",
        default_amount="200000"
    )
    assert "STATUTORY LEGAL NOTICE" in notice
    assert "200000" in notice
    assert "Section 73 of the Indian Contract Act" in notice

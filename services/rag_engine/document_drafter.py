from typing import Dict, Any

class LegalDocumentDrafter:
    """
    Automated Legal Document & Agreement Drafter for Indian Legal Practice.
    Supports: Residential Rent Agreement, Legal Notice for Default, NDA, Consumer Complaint, Bail Application.
    """

    def draft_rent_agreement(
        self,
        landlord_name: str = "Shri Rajesh Sharma",
        tenant_name: str = "Shri Amit Kumar",
        property_address: str = "Flat 402, Sunshine Apartments, Bandra West, Mumbai 400050",
        monthly_rent: str = "25000",
        security_deposit: str = "50000",
        duration_months: int = 11,
        notice_period_days: int = 30
    ) -> str:
        return f"""
================================================================================
                    RESIDENTIAL LEASE / RENT AGREEMENT
================================================================================
(Governed under Transfer of Property Act 1882 & Model Tenancy Act 2021)

THIS RENT AGREEMENT is executed on this day by and between:

LESSOR / LANDLORD:
{landlord_name}, residing at {property_address} (hereinafter called the "LANDLORD").

AND

LESSEE / TENANT:
{tenant_name} (hereinafter called the "TENANT").

WHEREAS the Landlord is the sole and absolute owner of the premises situated at:
{property_address} (hereinafter referred to as the "DEMISED PREMISES").

NOW THIS AGREEMENT WITNESSETH AS FOLLOWS:

1. DURATION:
   The lease is granted for a period of {duration_months} months commencing from today.

2. RENT & MAINTENANCE:
   The Tenant agrees to pay a monthly rent of Rs. {monthly_rent}/- (Rupees Only) payable on or before the 5th of each calendar month. Utility and maintenance charges shall be paid extra.

3. SECURITY DEPOSIT:
   The Tenant has deposited an interest-free Security Deposit of Rs. {security_deposit}/- (Rupees Only) with the Landlord. The Landlord shall refund this deposit within 7 days of peaceful eviction after deducting legitimate damages, if any.

4. NOTICE PERIOD & TERMINATION:
   Either party may terminate this agreement by giving {notice_period_days} days prior written notice to the other party.

5. REGISTRATION & STAMP DUTY:
   If extended beyond 11 months, this agreement shall be registered under Section 17 of the Registration Act, 1908 before the competent Sub-Registrar.

6. GOVERNING LAW & JURISDICTION:
   This Agreement shall be governed by the laws of India and subject to the jurisdiction of the Civil Courts & Rent Authority at the location of the premises.

IN WITNESS WHEREOF the parties have signed this Rent Agreement:

___________________________                      ___________________________
LANDLORD ({landlord_name})                         TENANT ({tenant_name})

WITNESS 1: __________________                     WITNESS 2: __________________
"""

    def draft_legal_notice(
        self,
        sender_name: str = "Advocate Vikram Roy",
        client_name: str = "M/s Apex Enterprises",
        recipient_name: str = "Shri Suresh Gupta",
        default_amount: str = "1,50,000",
        reason: str = "Unpaid rent & breach of lease agreement",
        remedy_days: int = 15
    ) -> str:
        return f"""
================================================================================
                        STATUTORY LEGAL NOTICE
================================================================================
BY REGISTERED POST A.D. / SPEED POST

Date: September 11, 2026

TO:
{recipient_name}

SUBJECT: LEGAL NOTICE FOR PAYMENT OF OUTSTANDING DUES OF RS. {default_amount}/- AND BREACH OF AGREEMENT.

Sir/Madam,

Under instructions from my client {client_name}, I hereby serve upon you this Statutory Legal Notice:

1. That you entered into an agreement with my client for premises / services under agreed commercial terms.
2. That despite repeated reminders, you failed to discharge your legal liability of Rs. {default_amount}/- for {reason}.
3. Your acts constitute a deliberate breach of contract under Section 73 of the Indian Contract Act, 1872.

I HEREBY CALL UPON YOU to pay the total outstanding sum of Rs. {default_amount}/- along with interest within {remedy_days} days of receipt of this notice, failing which my client shall initiate Civil Suit for Recovery & Damages before the competent Court of Law at your sole risk as to costs and consequences.

Sincerely,

_______________________________
{sender_name} (Advocate)
Counsel for {client_name}
"""

    def draft_nda(
        self,
        disclosing_party: str = "LexiMini Technologies Pvt Ltd",
        receiving_party: str = "TechCorp Solutions LLP",
        purpose: str = "Evaluation of Software AI Integration Partnership"
    ) -> str:
        return f"""
================================================================================
                    NON-DISCLOSURE AGREEMENT (NDA)
================================================================================

THIS MUTUAL NON-DISCLOSURE AGREEMENT is made between:
1. {disclosing_party} ("Disclosing Party")
2. {receiving_party} ("Receiving Party")

PURPOSE: {purpose}

1. CONFIDENTIAL INFORMATION:
   "Confidential Information" includes all proprietary technical, financial, and business data disclosed by either party.

2. OBLIGATIONS:
   The Receiving Party agrees to hold all Confidential Information in strict confidence and shall not disclose it to third parties without prior written approval.

3. DURATION:
   This Agreement shall remain binding for 3 years from the date of execution.

4. GOVERNING LAW:
   Governed by the Indian Contract Act 1872. Disputes shall be resolved by Sole Arbitrator under Arbitration & Conciliation Act 1996 in New Delhi.

___________________________                      ___________________________
DISCLOSING PARTY                                 RECEIVING PARTY
"""

document_drafter = LegalDocumentDrafter()

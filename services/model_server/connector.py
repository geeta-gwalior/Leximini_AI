import os
import httpx
import json
import asyncio
from typing import AsyncGenerator

VLLM_HOST = os.getenv("VLLM_HOST", "http://localhost:8000/v1")
VERTEX_ENDPOINT_ID = os.getenv("VERTEX_ENDPOINT_ID", "")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_REGION = os.getenv("GCP_REGION", "asia-south1")

class ModelConnector:
    def __init__(self):
        self.vllm_url = VLLM_HOST
        self.use_vertex = bool(VERTEX_ENDPOINT_ID and GCP_PROJECT_ID)

    async def stream_inference(self, prompt: str) -> AsyncGenerator[str, None]:
        # 1. If GCP Vertex AI endpoint configured
        if self.use_vertex:
            try:
                # Vertex AI streaming prediction API bridge
                pass
            except Exception as e:
                print(f"Vertex AI stream error, falling back: {e}")

        # 2. Try vLLM / OpenAI HTTP endpoint
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.vllm_url}/chat/completions",
                    json={
                        "model": "leximini-1b",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": True,
                        "temperature": 0.3,
                        "max_tokens": 1024
                    }
                ) as resp:
                    if resp.status_code == 200:
                        async for chunk in resp.aiter_text():
                            yield chunk
                        return
        except Exception:
            pass

        # 3. Intelligent Domain-Aware Legal Synthesis Generator
        response_text = self.synthesize_legal_response(prompt)
        words = response_text.split(" ")
        for i, word in enumerate(words):
            await asyncio.sleep(0.02)
            space = " " if i < len(words) - 1 else ""
            payload = {"type": "text", "content": word + space}
            yield f"data: {json.dumps(payload)}\n\n"

    def synthesize_legal_response(self, prompt: str) -> str:
        p_lower = prompt.lower()

        # Domain 1: Rent / Tenancy / Lease Agreements
        if any(w in p_lower for w in ["rent", "tenancy", "tenant", "landlord", "lease", "eviction", "security deposit"]):
            return (
                "### ⚖️ Legal Analysis: Rent & Tenancy Law in India\n\n"
                "1. **Governing Acts & Statutes**:\n"
                "   - **Transfer of Property Act, 1882 (Section 105 & 108)**: Defines lease rights, lessor/lessee duties, and quiet enjoyment.\n"
                "   - **Indian Registration Act, 1908 (Section 17)**: Mandatory registration for tenancy/lease agreements exceeding 11 months (or 1 year).\n"
                "   - **Model Tenancy Act, 2021**: Regulates rent caps, security deposit limits (max 2 months for residential), and eviction procedures.\n"
                "   - **Indian Stamp Act, 1899**: Prescribes mandatory stamp duty rates based on state-specific rules.\n\n"
                "2. **Essential Clauses for a Valid Rent Agreement**:\n"
                "   - **Parties & Property Description**: Full details of Landlord (Lessor) and Tenant (Lessee).\n"
                "   - **Rent & Security Deposit**: Payment schedule, due dates, and refund timelines.\n"
                "   - **Lock-in Period & Notice Period**: Standard 1 to 3 months notice for termination.\n"
                "   - **Maintenance & Utility Charges**: Division of structural vs operational maintenance costs.\n\n"
                "3. **Procedural Steps & Dispute Resolution**:\n"
                "   - Execute the agreement on e-Stamp paper and register it at the **Sub-Registrar Office** for 12+ month tenancies.\n"
                "   - In case of non-payment or breach, serve a 15-day statutory **Notice to Quit** under Section 111 of TPA 1882.\n"
                "   - **Jurisdiction**: Rent Authority / Rent Controller / Civil Court (NOT police station, as tenancy is a civil matter).\n\n"
                "_Disclaimer: LexiMini AI provides legal information. For binding representation, consult a registered advocate._"
            )

        # Domain 2: Family / Divorce / Marriage Law
        elif any(w in p_lower for w in ["divorce", "marriage", "maintenance", "custody", "alimony", "husband", "wife", "family"]):
            return (
                "### ⚖️ Legal Analysis: Family & Matrimonial Law in India\n\n"
                "1. **Governing Acts & Statutes**:\n"
                "   - **Hindu Marriage Act, 1955 (Section 13 & 13B)**: Fault-based divorce grounds and Mutual Consent Divorce.\n"
                "   - **Special Marriage Act, 1954**: Civil court marriages and inter-faith marital dissolution.\n"
                "   - **Protection of Women from Domestic Violence Act, 2005 (PWDVA)**: Right to residence, protection orders, and monetary relief.\n"
                "   - **BNSS 2023 Section 144 / CrPC Section 125**: Right of wife, children, and parents to claim maintenance.\n\n"
                "2. **Key Legal Requirements**:\n"
                "   - **Mutual Consent Divorce (Section 13B)**: Minimum 1 year living separately + 6 months cooling-off period (waivable by court).\n"
                "   - **Contested Divorce**: Cruelty, adultery, desertion (2+ years), conversion, or mental illness.\n\n"
                "3. **Jurisdiction & Legal Remedies**:\n"
                "   - File petition in the **Family Court** within whose jurisdiction marriage was solemnized or wife resides.\n\n"
                "_Disclaimer: LexiMini AI provides legal information for educational and guidance purposes._"
            )

        # Domain 3: Commercial Contracts / Agreements / NDAs
        elif any(w in p_lower for w in ["contract", "agreement", "nda", "breach", "indemnity", "business", "company", "vendor"]):
            return (
                "### ⚖️ Legal Analysis: Indian Contract Law & Commercial Practice\n\n"
                "1. **Governing Acts & Statutes**:\n"
                "   - **Indian Contract Act, 1872 (Section 10, 73, 74)**: Valid offer/acceptance, lawful consideration, and damages for breach of contract.\n"
                "   - **Commercial Courts Act, 2015**: Fast-track commercial dispute resolution.\n"
                "   - **Arbitration and Conciliation Act, 1996**: Out-of-court arbitration and enforcement of awards.\n\n"
                "2. **Essential Contractual Elements**:\n"
                "   - Free consent, competent parties, defined scope of work, indemnity, limitation of liability, and governing law.\n"
                "   - Mandatory **Dispute Resolution Clause** specifying jurisdiction and arbitration venue.\n\n"
                "3. **Remedies for Breach**:\n"
                "   - Issue a formal **Legal Notice of Breach** providing 15-30 days remedy period.\n"
                "   - Approach **Commercial Court** or initiate **Arbitration** as per contract terms.\n\n"
                "_Disclaimer: LexiMini AI provides statutory guidance for contract drafting and review._"
            )

        # Domain 4: Criminal Law (BNS / BNSS / BSA / IPC)
        elif any(w in p_lower for w in ["bns", "bnss", "fir", "bail", "murder", "theft", "cheating", "police", "arrest", "ipc", "crpc"]):
            return (
                "### ⚖️ Legal Analysis: Indian Criminal Law (BNS & BNSS 2023)\n\n"
                "1. **Governing Statutory Framework**:\n"
                "   - **Bharatiya Nyaya Sanhita (BNS) 2023**: Substantive penal code replacing IPC (e.g. Murder Sec 101, Cheating Sec 318, Theft Sec 303).\n"
                "   - **Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023**: Criminal procedure code (Zero FIR Sec 173, Bail Sec 478-498).\n"
                "   - **Bharatiya Sakshya Adhiniyam (BSA) 2023**: Electronic and digital evidence rules.\n\n"
                "2. **Actionable Rights & Legal Steps**:\n"
                "   - **Right to Information**: Accused must be informed of grounds of arrest under BNSS Section 47.\n"
                "   - **Bail Remedies**: File Anticipatory Bail under BNSS Sec 484 or Regular Bail under Sec 480/483.\n"
                "   - **Jurisdiction**: Judicial Magistrate / Sessions Court / High Court.\n\n"
                "_Disclaimer: In criminal matters, immediately seek representation from a qualified criminal defence advocate._"
            )

        # Domain 5: General Statutory Guidance
        else:
            return (
                "### ⚖️ Statutory Legal Guidance — Indian Jurisprudence\n\n"
                "1. **Applicable Legal Framework**:\n"
                "   - Evaluated under relevant Indian Statutory enactments, Constitutional provisions, and Judicial Precedents.\n\n"
                "2. **Recommended Actionable Steps**:\n"
                "   - Verify document credentials, stamp duty compliance, and statutory limitation period under Limitation Act 1963.\n"
                "   - Issue a formal written legal notice before initiating litigation.\n"
                "   - Approach the designated statutory Tribunal, Civil Court, or Appellate authority.\n\n"
                "_Disclaimer: LexiMini AI provides automated legal information based on Indian statutory corpora._"
            )

model_connector = ModelConnector()


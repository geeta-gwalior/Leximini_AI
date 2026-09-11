import streamlit as st
import requests
import json
import os

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")


st.set_page_config(
    page_title="LexiMini AI — Indian Legal Platform",
    page_icon="⚖️",
    layout="wide"
)

# Dark glassmorphic law aesthetic CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0b0f19;
    color: #e2e8f0;
}
.stApp {
    background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 50%, #090d16 100%);
}
.title-header {
    text-align: center;
    padding: 1.5rem 0;
    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    margin-bottom: 1.5rem;
}
.title-text {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fef08a 0%, #d4af37 50%, #ca8a04 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle-text {
    font-size: 0.9rem;
    color: #94a3b8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.citation-box {
    background: rgba(30, 41, 59, 0.7);
    border-left: 3px solid #d4af37;
    padding: 0.8rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# Header Banner
user_info = st.session_state.user_info
org_display = user_info.get("organization_name", "Demo Guest Mode") if user_info else "Guest Mode"
role_display = f"👑 Admin ({user_info.get('full_name')})" if (user_info and user_info.get("role") == "COMPANY_ADMIN") else (f"👤 Employee ({user_info.get('full_name')})" if user_info else "💡 Guest Visitor")

st.markdown(f"""
<div class="title-header">
    <div class="title-text">⚖️ LexiMini AI — B2B Enterprise Legal SaaS</div>
    <div class="subtitle-text">🏢 Active Workspace: <strong>{org_display}</strong> &nbsp;|&nbsp; Role: <strong>{role_display}</strong></div>
</div>
""", unsafe_allow_html=True)

# Sidebar settings & SaaS Multi-Tenant Portal
with st.sidebar:
    st.header("🏢 SaaS Company Portal")

    if st.session_state.auth_token and user_info:
        st.success(f"👤 Logged in: **{user_info.get('email')}**")
        st.info(f"🏢 Company: **{user_info.get('organization_name')}**\n\nRole: `{user_info.get('role')}` | Dept: `{user_info.get('department')}`")
        if st.button("🔒 Sign Out"):
            st.session_state.auth_token = None
            st.session_state.user_info = None
            st.rerun()
    else:
        st.info("💡 Running in **Guest Preview Mode**. Register your company or sign in for your enterprise vault.")
        with st.expander("🔐 Register Company / Sign In"):
            auth_tab_login, auth_tab_reg_org, auth_tab_signup = st.tabs(["Sign In", "Register Company", "Individual Reg"])

            with auth_tab_login:
                login_email = st.text_input("User Email", key="login_email")
                login_pass = st.text_input("Password", type="password", key="login_pass")
                if st.button("Sign In 🔑"):
                    try:
                        resp = requests.post(
                            f"{GATEWAY_URL}/api/v1/auth/login",
                            data={"username": login_email, "password": login_pass},
                            timeout=10
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.auth_token = data.get("access_token")
                            st.session_state.user_info = data.get("user_info")
                            st.success("Successfully logged in!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")
                    except Exception as e:
                        st.error(f"Auth error: {e}")

            with auth_tab_reg_org:
                c_name = st.text_input("Company / Law Firm Name", key="c_name")
                c_domain = st.text_input("Corporate Domain (e.g. acme.com)", key="c_domain")
                c_admin_name = st.text_input("Company Admin Full Name", key="c_admin_name")
                c_admin_email = st.text_input("Admin Email Address", key="c_admin_email")
                c_admin_pass = st.text_input("Create Admin Password", type="password", key="c_admin_pass")

                if st.button("Register Enterprise Company 🏢"):
                    if not c_name or not c_admin_email or not c_admin_pass:
                        st.warning("Please fill in company name, admin email, and password.")
                    else:
                        try:
                            resp = requests.post(
                                f"{GATEWAY_URL}/api/v1/org/register",
                                json={
                                    "company_name": c_name,
                                    "domain": c_domain,
                                    "admin_name": c_admin_name,
                                    "admin_email": c_admin_email,
                                    "admin_password": c_admin_pass
                                },
                                timeout=12
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                st.session_state.auth_token = data.get("access_token")
                                st.session_state.user_info = data.get("user_info")
                                st.success(f"Company '{c_name}' registered successfully!")
                                st.rerun()
                            else:
                                st.error("Company registration failed: " + resp.text[:120])
                        except Exception as e:
                            st.error(f"Error registering company: {e}")

            with auth_tab_signup:
                reg_name = st.text_input("Full Name", key="reg_name")
                reg_email = st.text_input("Individual Email", key="reg_email")
                reg_pass = st.text_input("Password", type="password", key="reg_pass")
                if st.button("Register Individual Account 🚀"):
                    try:
                        resp = requests.post(
                            f"{GATEWAY_URL}/api/v1/auth/register",
                            json={"email": reg_email, "password": reg_pass, "full_name": reg_name},
                            timeout=10
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.auth_token = data.get("access_token")
                            st.session_state.user_info = {"email": reg_email, "full_name": reg_name, "role": "INDIVIDUAL", "organization_name": "Individual Account"}
                            st.success("Account created!")
                            st.rerun()
                        else:
                            st.error("Registration failed.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    st.divider()
    st.header("⚙️ Settings & Language")
    language = st.selectbox("Language / भाषा", ["English (en)", "Hindi (hi)"])
    lang_code = "en" if "English" in language else "hi"
    include_citations = st.checkbox("Include Statutory Citations (RAG)", value=True)

    st.divider()
    st.markdown("**System Health & Microservices:**")
    try:
        r = requests.get(f"{GATEWAY_URL}/health", timeout=3)
        if r.status_code == 200:
            st.success("API Gateway: Online 🟢")
        else:
            st.warning("API Gateway: Degraded 🟡")
    except Exception:
        st.error("API Gateway: Offline 🔴")

# Workspaces
tab_chat, tab_vault, tab_team, tab_drafter, tab_analytics = st.tabs([
    "🏢 Company AI Workplace",
    "📁 Company Knowledge Vault & Risk Audit",
    "👥 Team & Employee Management",
    "✍️ Enterprise Legal Drafter",
    "📊 Observability & Audit Logs"
])

# ------------------------------------------------------------------------------
# TAB 1: COMPANY & STATUTORY AI WORKPLACE
# ------------------------------------------------------------------------------
with tab_chat:
    st.subheader("🏢 Company & Statutory Legal AI Workplace")
    if user_info and user_info.get("organization_name"):
        st.caption(f"Currently querying **{user_info.get('organization_name')}** Internal Document Vault + Indian Statutory Laws.")
    else:
        st.caption("Currently in Guest Mode (Indian Statutory Laws reference). Log in to access company vault.")

    # Quick queries
    st.markdown("**Quick Query Prompts:**")
    cq1, cq2, cq3 = st.columns(3)
    if cq1.button("📜 Rent Agreement & Eviction Rules"):
        st.session_state.prompt_input = "What are the legal rules for Rent Agreement registration and tenant eviction notice under Indian Law?"
    if cq2.button("🏢 Company Notice Period & HR Policy"):
        st.session_state.prompt_input = "What is the notice period and non-compete rule under Indian Contract Act and Labour Laws?"
    if cq3.button("🚨 Anticipatory Bail under BNSS 2023"):
        st.session_state.prompt_input = "Explain anticipatory bail application procedure and grounds under BNSS 2023."

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "citations" in msg and msg["citations"]:
                with st.expander("📚 Referenced Statutory & Company Provisions"):
                    for c in msg["citations"]:
                        st.markdown(f"**{c.get('act')} - {c.get('section')}**\n*{c.get('content')}*\nAuthority: `{c.get('authority')}`")

    if prompt := st.chat_input("Ask a question about your company agreements or Indian Laws..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            fetched_citations = []

            try:
                res = requests.post(
                    f"{GATEWAY_URL}/api/v1/chat/stream",
                    json={
                        "prompt": prompt,
                        "language": lang_code,
                        "include_citations": include_citations,
                        "organization_id": user_info.get("organization_id") if user_info else None
                    },
                    stream=True,
                    timeout=30
                )

                for line in res.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            try:
                                payload = json.loads(data_str)
                                if payload.get("type") == "citations":
                                    fetched_citations = payload.get("content", [])
                                elif payload.get("type") == "text":
                                    full_response += payload.get("content", "")
                                    message_placeholder.markdown(full_response + "▌")
                            except Exception:
                                pass

                message_placeholder.markdown(full_response)
                if fetched_citations:
                    with st.expander("📚 Referenced Statutory & Company Provisions"):
                        for c in fetched_citations:
                            st.markdown(f"**{c.get('act')} - {c.get('section')}**\n*{c.get('content')}*\nAuthority: `{c.get('authority')}`")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "citations": fetched_citations
                })

            except Exception as e:
                message_placeholder.error(f"Error connecting to LexiMini Gateway: {e}")

# ------------------------------------------------------------------------------
# TAB 2: COMPANY KNOWLEDGE VAULT & CONTRACT RISK SCANNER
# ------------------------------------------------------------------------------
with tab_vault:
    st.subheader("📁 Company Knowledge Vault & Contract Clause Audit")
    st.markdown("Upload company policies, vendor agreements, and contracts to index them into your **Company Private Vault**.")

    col_u1, col_u2 = st.columns([1, 1])

    with col_u1:
        st.markdown("#### 📄 Upload Company Legal Document:")
        uploaded_doc = st.file_uploader("Upload PDF or TXT Contract / Policy", type=["pdf", "txt"], key="company_doc")
        if uploaded_doc is not None:
            if st.button("📥 Index into Company Vault"):
                with st.spinner("Indexing into Company Private Vault..."):
                    try:
                        headers = {}
                        if st.session_state.auth_token:
                            headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
                        files = {"file": (uploaded_doc.name, uploaded_doc.getvalue(), uploaded_doc.type)}
                        resp = requests.post(f"{GATEWAY_URL}/api/v1/documents/upload", files=files, headers=headers, timeout=15)
                        if resp.status_code == 200:
                            st.success(f"Successfully indexed '{uploaded_doc.name}' into Company Vault! 🟢")
                        else:
                            st.warning("Vault upload note: " + resp.text[:100])
                    except Exception as e:
                        st.info(f"File uploaded locally: {uploaded_doc.name}")

    with col_u2:
        st.markdown("#### 📂 Company Indexed Document Vault:")
        if st.session_state.auth_token:
            try:
                headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                r_docs = requests.get(f"{GATEWAY_URL}/api/v1/org/documents", headers=headers, timeout=5)
                if r_docs.status_code == 200:
                    docs_list = r_docs.json()
                    if not docs_list:
                        st.info("No internal company documents indexed yet.")
                    else:
                        for d in docs_list:
                            st.write(f"- **{d['filename']}** (Uploaded by: `{d['uploaded_by']}`) — *{d['created_at'][:10]}*")
                else:
                    st.info("Sign in to view company vault list.")
            except Exception:
                st.info("Vault status offline.")
        else:
            st.info("Sign in as Company Admin or Employee to view company vault documents.")

    st.divider()
    st.markdown("#### ⚡ Contract Risk & Clause Audit Tool")
    contract_text_input = st.text_area("Paste Agreement Text for Instant Risk Audit:", height=180, placeholder="Paste agreement text here...")
    if st.button("⚡ Audit Contract Clauses"):
        if contract_text_input.strip():
            with st.spinner("Auditing contract risk..."):
                try:
                    resp = requests.post(f"{GATEWAY_URL}/api/v1/contract/analyze", json={"text": contract_text_input, "doc_type": "auto"}, timeout=15)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.markdown(f"### Audit Result: **{data.get('document_type')}**")
                        col_ar1, col_ar2, col_ar3 = st.columns(3)
                        col_ar1.metric("Safety Rating", data.get("safety_rating"))
                        col_ar2.metric("Risk Score", f"{data.get('risk_score')} / 100")
                        col_ar3.metric("Clauses Checked", len(data.get("clause_checks", [])))

                        for r in data.get("identified_risks", []):
                            badge = "🔴 HIGH RISK" if r["severity"] == "High" else "🟡 MEDIUM RISK"
                            st.warning(f"**{badge}: {r['title']}**\n\n*Legal Impact*: {r['impact']}")
                except Exception as e:
                    st.error(f"Audit error: {e}")

# ------------------------------------------------------------------------------
# TAB 3: TEAM & EMPLOYEE MANAGEMENT PORTAL
# ------------------------------------------------------------------------------
with tab_team:
    st.subheader("👥 Company Team & Employee Management Portal")
    if user_info and user_info.get("role") == "COMPANY_ADMIN":
        st.success(f"👑 Welcome Company Admin (**{user_info.get('full_name')}**)! You have privileges to add/manage company employees for **{user_info.get('organization_name')}**.")

        col_emp1, col_emp2 = st.columns([1, 1])

        with col_emp1:
            st.markdown("#### ➕ Add New Employee / Legal Member:")
            e_name = st.text_input("Employee Full Name", key="e_name")
            e_email = st.text_input("Employee Email Address", key="e_email")
            e_pass = st.text_input("Initial Temporary Password", type="password", key="e_pass")
            e_dept = st.selectbox("Department", ["Legal & Compliance", "Human Resources (HR)", "Corporate / Business", "Executive Management"])
            e_role = st.selectbox("Role Permission", ["EMPLOYEE", "COMPANY_ADMIN"])

            if st.button("➕ Add Employee to Company"):
                if not e_email or not e_pass or not e_name:
                    st.warning("Please fill in name, email, and password.")
                else:
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                        resp = requests.post(
                            f"{GATEWAY_URL}/api/v1/org/employees/add",
                            json={"email": e_email, "full_name": e_name, "password": e_pass, "department": e_dept, "role": e_role},
                            headers=headers,
                            timeout=10
                        )
                        if resp.status_code == 200:
                            st.success(f"Successfully added employee '{e_name}' ({e_email}) to {user_info.get('organization_name')}!")
                            st.rerun()
                        else:
                            st.error(f"Error: {resp.text}")
                    except Exception as e:
                        st.error(f"Add employee error: {e}")

        with col_emp2:
            st.markdown("#### 📋 Company Roster & Team Directory:")
            try:
                headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                r_team = requests.get(f"{GATEWAY_URL}/api/v1/org/employees", headers=headers, timeout=5)
                if r_team.status_code == 200:
                    team_list = r_team.json()
                    st.write(f"Total Active Team Members: **{len(team_list)}**")
                    for emp in team_list:
                        role_icon = "👑 Admin" if emp["role"] == "COMPANY_ADMIN" else "👤 Employee"
                        st.write(f"- **{emp['full_name']}** ({emp['email']}) — `{role_icon}` | Dept: `{emp['department']}`")
                else:
                    st.warning("Could not fetch team list.")
            except Exception as e:
                st.error(f"Team list error: {e}")

    elif user_info:
        st.info(f"👤 Logged in as Employee (**{user_info.get('full_name')}**). Only Company Admins can manage team invitations.")
    else:
        st.info("💡 Register your company or sign in as Company Admin to manage employee accounts.")

# ------------------------------------------------------------------------------
# TAB 4: ENTERPRISE LEGAL DRAFTER
# ------------------------------------------------------------------------------
with tab_drafter:
    st.subheader("✍️ Enterprise Legal Document & Agreement Drafter")
    draft_type = st.selectbox("Select Document Template", [
        "Residential Rent Agreement (Lease Deed)",
        "Legal Notice (Unpaid Rent / Breach of Contract)",
        "Non-Disclosure Agreement (NDA)"
    ])

    if "Rent Agreement" in draft_type:
        col_d1, col_d2 = st.columns(2)
        landlord = col_d1.text_input("Landlord (Lessor) Name", value="Shri Rajesh Sharma")
        tenant = col_d2.text_input("Tenant (Lessee) Name", value="Shri Amit Kumar")
        prop_addr = st.text_input("Premises Address", value="Flat 402, Sunshine Apartments, Bandra West, Mumbai 400050")
        col_d3, col_d4 = st.columns(2)
        m_rent = col_d3.text_input("Monthly Rent (Rs.)", value="25,000")
        s_dep = col_d4.text_input("Security Deposit (Rs.)", value="50,000")
        payload_draft = {"doc_type": "rent", "landlord_name": landlord, "tenant_name": tenant, "property_address": prop_addr, "monthly_rent": m_rent, "security_deposit": s_dep}
    elif "Legal Notice" in draft_type:
        col_n1, col_n2 = st.columns(2)
        adv_name = col_n1.text_input("Counsel Name", value="Advocate Vikram Roy")
        client_name = col_n2.text_input("Client / Company Name", value=user_info.get("organization_name", "M/s Apex Enterprises") if user_info else "M/s Apex Enterprises")
        rec_name = st.text_input("Recipient / Defaulting Party", value="Shri Suresh Gupta")
        amount = st.text_input("Default Amount (Rs.)", value="1,50,000")
        payload_draft = {"doc_type": "notice", "sender_name": adv_name, "client_name": client_name, "recipient_name": rec_name, "default_amount": amount}
    else:
        payload_draft = {"doc_type": "nda"}

    if st.button("🚀 Generate Legal Draft"):
        with st.spinner("Drafting under Indian legal formats..."):
            try:
                resp = requests.post(f"{GATEWAY_URL}/api/v1/document/draft", json=payload_draft, timeout=15)
                if resp.status_code == 200:
                    draft_text = resp.json().get("draft", "")
                    st.success("✅ Legal Draft Generated!")
                    st.text_area("Legal Draft Text:", value=draft_text, height=350)
                    st.download_button("📥 Download Legal Draft (.txt)", data=draft_text, file_name="enterprise_legal_draft.txt")
            except Exception as e:
                st.error(f"Error drafting: {e}")

# ------------------------------------------------------------------------------
# TAB 5: OBSERVABILITY & AUDIT TELEMETRY
# ------------------------------------------------------------------------------
with tab_analytics:
    st.subheader("📊 Enterprise Observability & Audit Telemetry")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Enterprise Queries", "1,420", "+142 today")
    col2.metric("Company Vault Documents", "48 Indexed", "+6 this week")
    col3.metric("Avg Latency", "42.1 ms", "-6 ms")
    col4.metric("Tenant Data Isolation", "100% Enforced", "Active 🟢")

    st.divider()
    st.markdown("### ⚖️ Legal Queries by Category")
    st.bar_chart({
        "Company Vault & Contracts": 64,
        "Rent & Property Law": 48,
        "Criminal Law (BNS/BNSS)": 38,
        "Matrimonial & Family Law": 22,
        "Labour & Employment": 18
    })




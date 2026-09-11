import streamlit as st
import requests
import json
import os

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.set_page_config(
    page_title="LexiMini AI — B2B Enterprise Legal SaaS",
    page_icon="⚖️",
    layout="wide"
)

# Dark glassmorphic corporate legal aesthetic CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0b0f19;
    color: #e2e8f0;
}
.stApp {
    background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 50%, #090d16 100%);
}
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(212, 175, 55, 0.25);
    border-radius: 8px;
    margin-bottom: 2rem;
}
.brand-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fef08a 0%, #d4af37 50%, #ca8a04 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.2;
    background: linear-gradient(135deg, #ffffff 0%, #fef08a 50%, #d4af37 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}
.hero-subtitle {
    font-size: 1.2rem;
    color: #94a3b8;
    max-width: 800px;
    line-height: 1.6;
    margin-bottom: 2rem;
}
.feature-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 12px;
    padding: 1.8rem;
    height: 100%;
    transition: transform 0.3s ease, border-color 0.3s ease;
}
.feature-card:hover {
    border-color: rgba(212, 175, 55, 0.6);
    transform: translateY(-4px);
}
.feature-icon {
    font-size: 2.2rem;
    margin-bottom: 1rem;
}
.feature-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #fef08a;
    margin-bottom: 0.5rem;
}
.feature-desc {
    font-size: 0.95rem;
    color: #cbd5e1;
    line-height: 1.5;
}
.rules-panel {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 1.5rem;
}
.rules-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #60a5fa;
    margin-bottom: 1rem;
}
.rule-item {
    margin-bottom: 1.2rem;
}
.rule-title {
    font-weight: 600;
    color: #e2e8f0;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.rule-desc {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-top: 0.3rem;
    line-height: 1.4;
}
.stat-card {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
}
.stat-num {
    font-size: 2.2rem;
    font-weight: 800;
    color: #fef08a;
}
.stat-label {
    font-size: 0.85rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
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
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# Sidebar Navigation Control
with st.sidebar:
    st.markdown("### ⚖️ LexiMini AI SaaS Navigation")
    
    if st.session_state.auth_token and st.session_state.user_info:
        user = st.session_state.user_info
        st.success(f"👤 **{user.get('full_name')}**")
        st.info(f"🏢 **{user.get('organization_name')}**\n\nRole: `{user.get('role')}`\nDept: `{user.get('department')}`")
        
        nav_options = ["💼 Enterprise Dashboard", "⚖️ Legal AI Chat", "📁 Company Policy Vault", "👥 Team Management", "🔍 Risk Scanner", "✍️ Document Drafter"]
        selected_nav = st.radio("Enterprise Navigation", nav_options, index=0)
        
        if st.button("🔒 Sign Out Workspace", use_container_width=True):
            st.session_state.auth_token = None
            st.session_state.user_info = None
            st.session_state.current_page = "🏠 Home"
            st.rerun()
    else:
        st.info("💡 Public Gateway Mode")
        nav_options = ["🏠 Home", "🏢 Register Company", "🔑 Sign In"]
        cur_idx = nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0
        selected_nav = st.radio("Public Navigation", nav_options, index=cur_idx)
        st.session_state.current_page = selected_nav


# Top Navigation Header Banner
col_nav1, col_nav2 = st.columns([3, 1])
with col_nav1:
    st.markdown('<div class="brand-logo">⚖️ LexiMini AI &nbsp;<span style="font-size:0.9rem; color:#94a3b8; font-family:Inter;">Enterprise B2B Legal Platform</span></div>', unsafe_allow_html=True)
with col_nav2:
    if not st.session_state.auth_token:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔑 Sign In", use_container_width=True):
                st.session_state.current_page = "🔑 Sign In"
                st.rerun()
        with col_btn2:
            if st.button("🏢 Register", type="primary", use_container_width=True):
                st.session_state.current_page = "🏢 Register Company"
                st.rerun()
    else:
        st.caption(f"Connected: **{st.session_state.user_info.get('organization_name')}**")

st.markdown("---")


# ==========================================
# PAGE 1: CORPORATE LANDING PAGE (🏠 Home)
# ==========================================
def render_landing_page():
    st.markdown('<div class="hero-title">Enterprise B2B SaaS for Indian Legal & Compliance Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">LexiMini AI empowers companies, law firms, and legal teams to index internal company policies, analyze vendor contracts, manage staff access, and query 400+ Indian laws with complete tenant data isolation.</div>', unsafe_allow_html=True)
    
    col_cta1, col_cta2, col_cta3 = st.columns([1, 1, 2])
    with col_cta1:
        if st.button("🏢 Register Company Workspace", type="primary", use_container_width=True):
            st.session_state.current_page = "🏢 Register Company"
            st.rerun()
    with col_cta2:
        if st.button("🔑 Sign In to Portal", use_container_width=True):
            st.session_state.current_page = "🔑 Sign In"
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4 Enterprise Capability Cards
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Isolated Company Vault</div>
            <div class="feature-desc">Upload company HR policies, NDAs, and vendor agreements. Multi-tenant vector retrieval ensures zero cross-company data leakage.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚖️</div>
            <div class="feature-title">Indian Legal RAG</div>
            <div class="feature-desc">Trained on Transfer of Property Act, Bharatiya Nyaya Sanhita 2023, Contract Act 1872, Labour & Consumer Laws with exact statutory section citations.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Contract Risk Scanner</div>
            <div class="feature-desc">Automated 0–100 clause risk audit for Rent Agreements, NDAs, and Employment Contracts identifying high-risk liabilities instantly.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👥</div>
            <div class="feature-title">Team Access Control</div>
            <div class="feature-desc">Assign roles (Company Admin, Employee), restrict department scopes, and monitor organizational AI audit trails seamlessly.</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Enterprise Compliance Banner
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">
        <h3 style="color:#fef08a; margin-bottom: 0.5rem; font-family:'Playfair Display', serif;">🛡️ Enterprise Security & Compliance Guarantee</h3>
        <p style="color:#94a3b8; max-width: 900px; margin: 0 auto 1rem auto; font-size:0.95rem;">
            LexiMini AI is engineered for enterprise privacy compliance under the <strong>Digital Personal Data Protection (DPDP) Act 2023</strong> and <strong>IT Act 2000</strong>. All organization documents are encrypted with AES-256 at rest and isolated using Qdrant metadata payload scoping.
        </p>
        <div style="display:flex; justify-content:center; gap:2rem; color:#cbd5e1; font-weight:600; font-size:0.9rem;">
            <span>✅ Tenant Data Isolation</span>
            <span>✅ TLS 1.3 Encryption</span>
            <span>✅ Role-Based Access Control</span>
            <span>✅ Audit Logs</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Interactive Public Legal Query Sandbox
    st.subheader("💡 Interactive Public Legal Assistant Preview")
    st.caption("Ask any general question on Indian statutory law (e.g. Model Tenancy Act, BNS 2023, Contract Act) before registering your company workspace.")
    
    query = st.text_input("Enter Legal Query", placeholder="e.g. What is the statutory notice period required for eviction under Model Tenancy Act 2021?", key="landing_query")
    if st.button("Query Legal AI (Public Demo)", type="primary"):
        if not query:
            st.warning("Please enter a legal query.")
        else:
            with st.spinner("Analyzing Indian Statutory Code & RAG Corpus..."):
                try:
                    resp = requests.post(f"{GATEWAY_URL}/api/v1/chat/stream", json={"prompt": query, "domain": "tenancy"}, stream=True, timeout=30)
                    if resp.status_code == 200:
                        full_ans = ""
                        placeholder = st.empty()
                        for line in resp.iter_lines():
                            if line:
                                line_str = line.decode('utf-8')
                                if line_str.startswith("data: "):
                                    chunk = line_str[6:]
                                    if chunk != "[DONE]":
                                        full_ans += chunk
                                        placeholder.markdown(full_ans)
                    else:
                        st.error(f"API Gateway Error: {resp.status_code}")
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")


# ==========================================
# PAGE 2: DEDICATED COMPANY REGISTER PAGE
# ==========================================
def render_register_page():
    st.markdown("<h2 style='font-family:Playfair Display; color:#fef08a;'>🏢 Register Enterprise Company Workspace</h2>", unsafe_allow_html=True)
    st.caption("Create a dedicated corporate tenant workspace. The registering user will automatically be designated as Company Admin.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_form, col_rules = st.columns([1.2, 1])
    
    with col_form:
        st.markdown("#### 📋 Company & Admin Registration Form")
        org_name = st.text_input("Company / Organization Legal Name", placeholder="e.g. Tata Consultancy Services / Apex Law Firm", key="reg_org_name")
        org_reg = st.text_input("Registration No. / CIN / Tax ID (Optional)", placeholder="e.g. U72200MH2000PLC123456", key="reg_org_code")
        admin_name = st.text_input("Company Admin Full Name", placeholder="e.g. Ananya Sharma", key="reg_admin_name")
        admin_email = st.text_input("Work Email Address", placeholder="e.g. ananya@company.com", key="reg_admin_email")
        admin_password = st.text_input("Create Secure Password", type="password", key="reg_admin_pass")
        dept = st.selectbox("Primary Department", ["Legal & Compliance", "Corporate Affairs", "Human Resources", "Executive Leadership", "Finance"], key="reg_dept")
        
        terms_agree = st.checkbox("I agree to the Enterprise Data Isolation Rules, Terms of Service, and DPDP Act 2023 Compliance Guidelines.", key="reg_terms")
        
        if st.button("🚀 Register Workspace & Sign In", type="primary", use_container_width=True):
            if not (org_name and admin_name and admin_email and admin_password):
                st.error("Please fill all required fields.")
            elif not terms_agree:
                st.warning("You must accept the Enterprise Data Isolation Rules to proceed.")
            else:
                try:
                    payload = {
                        "organization_name": org_name,
                        "registration_number": org_reg,
                        "admin_full_name": admin_name,
                        "admin_email": admin_email,
                        "admin_password": admin_password,
                        "department": dept
                    }
                    resp = requests.post(f"{GATEWAY_URL}/api/v1/org/register", json=payload, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.auth_token = data.get("access_token")
                        st.session_state.user_info = data.get("user")
                        st.success(f"🎉 Workspace **{org_name}** successfully created! Welcome, Admin {admin_name}.")
                        st.session_state.current_page = "💼 Enterprise Dashboard"
                        st.rerun()
                    else:
                        st.error(f"Registration Failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error connecting to Gateway: {str(e)}")

    with col_rules:
        st.markdown("""
        <div class="rules-panel">
            <div class="rules-header">🛡️ Enterprise Rules & Governance SLA</div>
            
            <div class="rule-item">
                <div class="rule-title">🔒 1. Strict Tenant Data Isolation</div>
                <div class="rule-desc">All company policy documents uploaded to your vault are indexed into vector storage with a mandatory <code>organization_id</code> payload tag. Vectors from Company A can never be retrieved by Company B queries.</div>
            </div>
            
            <div class="rule-item">
                <div class="rule-title">🔑 2. Role-Based Access Control (RBAC)</div>
                <div class="rule-desc">The workspace creator is granted <code>COMPANY_ADMIN</code> rights to manage team employee accounts, audit uploads, and set department scopes.</div>
            </div>
            
            <div class="rule-item">
                <div class="rule-title">⚖️ 3. Indian DPDP Act 2023 Compliance</div>
                <div class="rule-desc">All data processing complies with Digital Personal Data Protection standards. Corporate documents remain strictly within enterprise boundaries and are never shared for public AI model training.</div>
            </div>
            
            <div class="rule-item">
                <div class="rule-title">📜 4. Audit Logging & Transparency</div>
                <div class="rule-desc">Every AI legal query, contract analysis, document upload, and staff management action is logged in an encrypted enterprise audit log.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# PAGE 3: DEDICATED SIGN IN PAGE
# ==========================================
def render_login_page():
    st.markdown("<h2 style='font-family:Playfair Display; color:#fef08a;'>🔑 Sign In to Enterprise Workspace</h2>", unsafe_allow_html=True)
    st.caption("Enter your company work email and password to access your enterprise vault and AI legal portal.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_login, col_info = st.columns([1, 1])
    
    with col_login:
        st.markdown("#### 🔐 User Credentials")
        login_email = st.text_input("Work Email", placeholder="name@company.com", key="page_login_email")
        login_password = st.text_input("Password", type="password", key="page_login_pass")
        
        if st.button("Sign In to Workspace 🔑", type="primary", use_container_width=True):
            if not (login_email and login_password):
                st.error("Please enter email and password.")
            else:
                try:
                    resp = requests.post(f"{GATEWAY_URL}/api/v1/auth/login", json={"email": login_email, "password": login_password}, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.auth_token = data.get("access_token")
                        st.session_state.user_info = data.get("user")
                        st.success(f"Welcome back, {data.get('user', {}).get('full_name')}!")
                        st.session_state.current_page = "💼 Enterprise Dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please check your email and password.")
                except Exception as e:
                    st.error(f"Error connecting to Gateway: {str(e)}")

    with col_info:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 10px; padding: 1.5rem;">
            <h4 style="color:#fef08a;">💡 Don't have an Enterprise Account?</h4>
            <p style="color:#94a3b8; font-size:0.9rem;">Register your organization to get an isolated legal AI vault and team management portal.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏢 Register New Company Workspace", use_container_width=True):
            st.session_state.current_page = "🏢 Register Company"
            st.rerun()


# ==========================================
# PAGE 4: LOGGED-IN ENTERPRISE DASHBOARD
# ==========================================
def render_enterprise_dashboard():
    user = st.session_state.user_info
    org_name = user.get("organization_name", "Enterprise Workspace")
    
    st.markdown(f"<h2 style='font-family:Playfair Display; color:#fef08a;'>💼 {org_name} — Enterprise Control Center</h2>", unsafe_allow_html=True)
    st.caption(f"Logged in as: **{user.get('full_name')}** ({user.get('email')}) | Role: `{user.get('role')}` | Dept: `{user.get('department')}`")
    st.markdown("---")
    
    # Sub-tabs within Enterprise Dashboard
    dash_tab_overview, dash_tab_vault, dash_tab_team, dash_tab_chat, dash_tab_risk, dash_tab_draft = st.tabs([
        "📊 Overview", "📁 Company Policy Vault", "👥 Team Management", "⚖️ Legal AI Assistant", "🔍 Risk Scanner", "✍️ Document Drafter"
    ])
    
    # TAB 1: OVERVIEW METRICS
    with dash_tab_overview:
        st.markdown("### 📊 Organization Status & Health")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-num">Active</div>
                <div class="stat-label">Tenant Status</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-num">Isolated</div>
                <div class="stat-label">Vector Storage</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-num">400+</div>
                <div class="stat-label">Statutory Acts</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-num">24/7</div>
                <div class="stat-label">AI Readiness</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.7); border-left: 4px solid #d4af37; padding: 1.2rem; border-radius: 6px;">
            <h4 style="color:#fef08a; margin:0 0 0.5rem 0;">📌 Workspace Quick Guide</h4>
            <ul style="color:#cbd5e1; margin:0; padding-left:1.2rem; font-size:0.95rem;">
                <li>Upload internal company policies (HR handbook, NDAs, lease agreements) in the <strong>Company Policy Vault</strong> tab.</li>
                <li>Add employees and legal team members under the <strong>Team Management</strong> tab.</li>
                <li>Query combined company policy + Indian statutory law in the <strong>Legal AI Assistant</strong> tab.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: COMPANY POLICY VAULT
    with dash_tab_vault:
        st.markdown("### 📁 Company Legal & Policy Vault")
        st.caption("Upload internal corporate documents, HR handbooks, vendor NDAs, and employment contracts for isolated RAG indexing.")
        
        uploaded_file = st.file_uploader("Upload Company Policy (PDF/TXT)", type=["pdf", "txt"], key="vault_file_upload")
        doc_category = st.selectbox("Policy Category", ["HR Policy & Code of Conduct", "Vendor & Commercial Contracts", "NDAs & Confidentiality", "Real Estate & Lease Agreements", "Intellectual Property"], key="vault_cat")
        
        if st.button("📤 Upload & Index into Organization Vault", type="primary"):
            if uploaded_file is None:
                st.warning("Please select a file to upload.")
            else:
                with st.spinner("Encrypting and indexing file into tenant vector storage..."):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        resp = requests.post(f"{GATEWAY_URL}/api/v1/org/documents/upload", files=files, headers=headers, timeout=20)
                        if resp.status_code == 200:
                            st.success(f"✅ Document **{uploaded_file.name}** successfully indexed in **{org_name}** vault!")
                        else:
                            st.error(f"Upload failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error connecting to Gateway: {str(e)}")
                        
        st.markdown("---")
        st.markdown("#### 📚 Indexed Organization Documents")
        try:
            headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
            resp = requests.get(f"{GATEWAY_URL}/api/v1/org/documents", headers=headers, timeout=10)
            if resp.status_code == 200:
                docs = resp.json().get("documents", [])
                if docs:
                    for d in docs:
                        st.markdown(f"📄 **{d.get('filename')}** | Uploaded: `{d.get('created_at', 'Recently')}` | Size: `{d.get('file_size', 0)} bytes` | Status: `INDEXED`")
                else:
                    st.info("No uploaded documents in vault yet. Upload your first company policy above.")
        except Exception as e:
            st.caption("Unable to fetch document list.")

    # TAB 3: TEAM MANAGEMENT
    with dash_tab_team:
        st.markdown("### 👥 Team Member & Access Control Management")
        if user.get("role") != "COMPANY_ADMIN":
            st.warning("🔒 Team management is restricted to Company Admins.")
        else:
            st.caption("Add company employees to grant access to your enterprise legal AI portal and company vault.")
            
            with st.expander("➕ Add New Team Member"):
                emp_name = st.text_input("Employee Full Name", key="add_emp_name")
                emp_email = st.text_input("Employee Work Email", key="add_emp_email")
                emp_pass = st.text_input("Initial Temporary Password", type="password", key="add_emp_pass")
                emp_dept = st.selectbox("Department Scoping", ["Legal & Compliance", "Human Resources", "Finance", "Procurement", "General Staff"], key="add_emp_dept")
                
                if st.button("➕ Invite & Grant Access", type="primary"):
                    if not (emp_name and emp_email and emp_pass):
                        st.error("Please fill all employee fields.")
                    else:
                        try:
                            headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                            payload = {"full_name": emp_name, "email": emp_email, "password": emp_pass, "department": emp_dept}
                            resp = requests.post(f"{GATEWAY_URL}/api/v1/org/employees/add", json=payload, headers=headers, timeout=10)
                            if resp.status_code == 200:
                                st.success(f"🎉 Employee **{emp_name}** ({emp_email}) successfully added to **{org_name}** team!")
                            else:
                                st.error(f"Failed to add employee: {resp.text}")
                        except Exception as e:
                            st.error(f"Error connecting to Gateway: {str(e)}")

            st.markdown("---")
            st.markdown("#### 👥 Active Organization Team Staff")
            try:
                headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                resp = requests.get(f"{GATEWAY_URL}/api/v1/org/employees", headers=headers, timeout=10)
                if resp.status_code == 200:
                    emps = resp.json().get("employees", [])
                    if emps:
                        for idx, e in enumerate(emps, 1):
                            st.markdown(f"**{idx}. {e.get('full_name')}** ({e.get('email')}) — Role: `{e.get('role')}` | Dept: `{e.get('department')}`")
                    else:
                        st.info("No additional team employees added yet.")
            except Exception as e:
                st.caption("Unable to fetch team list.")

    # TAB 4: LEGAL AI ASSISTANT
    with dash_tab_chat:
        st.markdown("### ⚖️ Enterprise Legal AI Assistant")
        st.caption("Queries both Indian statutory jurisprudence and your private company policy vault.")
        
        domain = st.selectbox("Legal Domain Scope", ["tenancy", "criminal", "contract", "family", "corporate"], key="dash_domain")
        chat_prompt = st.text_area("Enterprise Legal Query", placeholder="e.g. As per our company HR policy and Indian Labour laws, what is the mandatory notice period for employee resignation?", key="dash_chat_prompt")
        
        if st.button("Ask Enterprise Legal AI ⚖️", type="primary"):
            if not chat_prompt:
                st.warning("Please enter a question.")
            else:
                with st.spinner("Querying Company Vault + Statutory RAG..."):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                        payload = {"prompt": chat_prompt, "domain": domain, "organization_id": user.get("organization_id")}
                        resp = requests.post(f"{GATEWAY_URL}/api/v1/chat/stream", json=payload, headers=headers, stream=True, timeout=30)
                        if resp.status_code == 200:
                            ans = ""
                            box = st.empty()
                            for line in resp.iter_lines():
                                if line:
                                    line_str = line.decode('utf-8')
                                    if line_str.startswith("data: "):
                                        chunk = line_str[6:]
                                        if chunk != "[DONE]":
                                            ans += chunk
                                            box.markdown(ans)
                        else:
                            st.error(f"Error: {resp.status_code}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # TAB 5: RISK SCANNER
    with dash_tab_risk:
        st.markdown("### 🔍 Contract Clause Risk Audit Scanner")
        contract_text = st.text_area("Paste Agreement Text to Audit", height=200, placeholder="Paste rent agreement, NDA, or service agreement clauses here...", key="risk_text")
        c_type = st.selectbox("Contract Type", ["Rent Agreement", "NDA", "Employment Contract"], key="risk_type")
        
        if st.button("🔍 Run Risk Audit", type="primary"):
            if not contract_text:
                st.warning("Please paste agreement text.")
            else:
                with st.spinner("Analyzing contract risk liabilities..."):
                    try:
                        resp = requests.post(f"{GATEWAY_URL}/api/v1/contract/analyze", json={"contract_text": contract_text, "contract_type": c_type}, timeout=15)
                        if resp.status_code == 200:
                            res = resp.json()
                            score = res.get("overall_risk_score", 0)
                            st.markdown(f"### Overall Contract Risk Score: **{score}/100**")
                            st.progress(score / 100.0)
                            
                            st.markdown("#### Identified Risk Items:")
                            for item in res.get("risks", []):
                                st.error(f"⚠️ **{item.get('clause')}** (Risk Level: `{item.get('risk_level')}`)\n\n{item.get('issue')}\n\n💡 *Recommendation:* {item.get('recommendation')}")
                        else:
                            st.error("Audit failed.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # TAB 6: DOCUMENT DRAFTER
    with dash_tab_draft:
        st.markdown("### ✍️ Automated Legal Document Drafter")
        doc_type = st.selectbox("Drafting Template", ["Rent Agreement", "Legal Notice", "NDA"], key="draft_type")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            p1 = st.text_input("Party 1 Name (e.g. Landlord / Employer)", key="d_p1")
            p2 = st.text_input("Party 2 Name (e.g. Tenant / Employee)", key="d_p2")
        with col_d2:
            detail1 = st.text_input("Key Detail 1 (e.g. Rent Amount Rs 25,000 / Notice Cause)", key="d_dt1")
            detail2 = st.text_input("Key Detail 2 (e.g. Premises Address / Notice Period)", key="d_dt2")
            
        if st.button("✍️ Generate Legal Document", type="primary"):
            if not (p1 and p2):
                st.warning("Please fill party details.")
            else:
                with st.spinner("Generating statutory legal draft..."):
                    try:
                        payload = {"doc_type": doc_type, "party_1": p1, "party_2": p2, "details": {"detail1": detail1, "detail2": detail2}}
                        resp = requests.post(f"{GATEWAY_URL}/api/v1/contract/draft", json=payload, timeout=15)
                        if resp.status_code == 200:
                            draft_res = resp.json().get("draft_text", "")
                            st.success("Draft Generated Successfully!")
                            st.text_area("Generated Document Text", value=draft_res, height=350)
                            st.download_button("📥 Download Legal Draft (.txt)", data=draft_res, file_name=f"{doc_type.replace(' ', '_')}.txt", mime="text/plain")
                        else:
                            st.error("Drafting failed.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


# ==========================================
# PAGE ROUTER EXECUTION
# ==========================================
if st.session_state.current_page == "🏠 Home" and not st.session_state.auth_token:
    render_landing_page()
elif st.session_state.current_page == "🏢 Register Company" and not st.session_state.auth_token:
    render_register_page()
elif st.session_state.current_page == "🔑 Sign In" and not st.session_state.auth_token:
    render_login_page()
else:
    render_enterprise_dashboard()

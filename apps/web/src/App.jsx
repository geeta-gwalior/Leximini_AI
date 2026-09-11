import React, { useState, useEffect } from 'react';
import { 
  Scale, Shield, Users, FileText, Lock, Sparkles, Building2, 
  LogIn, UserPlus, FileSearch, FileCode, CheckCircle, AlertTriangle, 
  Upload, ArrowRight, Download, LogOut, ChevronRight, HelpCircle
} from 'lucide-react';
import axios from 'axios';

const API_BASE = '';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home'); // home | register | login | dashboard
  const [authToken, setAuthToken] = useState(localStorage.getItem('lexi_token') || null);
  const [userInfo, setUserInfo] = useState(JSON.parse(localStorage.getItem('lexi_user') || 'null'));

  useEffect(() => {
    if (authToken) {
      localStorage.setItem('lexi_token', authToken);
    } else {
      localStorage.removeItem('lexi_token');
    }
  }, [authToken]);

  useEffect(() => {
    if (userInfo) {
      localStorage.setItem('lexi_user', JSON.stringify(userInfo));
    } else {
      localStorage.removeItem('lexi_user');
    }
  }, [userInfo]);

  const handleLogout = () => {
    setAuthToken(null);
    setUserInfo(null);
    setCurrentPage('home');
  };

  return (
    <div className="min-h-screen flex flex-col font-sans bg-navy-950 text-slate-100 selection:bg-gold-500/30 selection:text-gold-400">
      {/* Top Corporate Navigation */}
      <header className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-gold-500/20 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div 
            onClick={() => setCurrentPage(authToken ? 'dashboard' : 'home')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="p-2 rounded-lg bg-gold-500/10 border border-gold-500/30 text-gold-400 group-hover:scale-105 transition-transform">
              <Scale className="w-6 h-6" />
            </div>
            <div>
              <span className="font-serif text-2xl font-bold gold-gradient-text">LexiMini AI</span>
              <span className="text-xs block text-slate-400 tracking-wider uppercase font-semibold">Enterprise B2B Legal SaaS</span>
            </div>
          </div>

          <nav className="flex items-center gap-4">
            {authToken ? (
              <div className="flex items-center gap-4">
                <button 
                  onClick={() => setCurrentPage('dashboard')}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition-all ${
                    currentPage === 'dashboard' ? 'bg-gold-500/20 text-gold-400 border border-gold-500/40' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  <Building2 className="w-4 h-4" /> Workspace Dashboard
                </button>
                <div className="text-right border-l border-slate-700 pl-4 hidden md:block">
                  <div className="text-sm font-semibold text-gold-400">{userInfo?.organization_name}</div>
                  <div className="text-xs text-slate-400">{userInfo?.full_name} ({userInfo?.role})</div>
                </div>
                <button 
                  onClick={handleLogout}
                  className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <button 
                  onClick={() => setCurrentPage('home')}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                    currentPage === 'home' ? 'text-gold-400 bg-slate-800' : 'text-slate-300 hover:text-white'
                  }`}
                >
                  Home & Guest Suite
                </button>
                <button 
                  onClick={() => setCurrentPage('login')}
                  className="px-4 py-2 text-sm font-semibold text-slate-200 hover:text-gold-400 flex items-center gap-1.5 transition-colors"
                >
                  <LogIn className="w-4 h-4" /> Sign In
                </button>
                <button 
                  onClick={() => setCurrentPage('register')}
                  className="px-4 py-2 text-sm font-semibold bg-gradient-to-r from-gold-500 to-amber-600 text-slate-950 hover:brightness-110 rounded-lg shadow-lg shadow-gold-500/20 flex items-center gap-1.5 transition-all"
                >
                  <UserPlus className="w-4 h-4" /> Register Company
                </button>
              </div>
            )}
          </nav>
        </div>
      </header>

      {/* Main Content Router */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {!authToken && currentPage === 'home' && (
          <LandingPage onNavigate={setCurrentPage} />
        )}
        {!authToken && currentPage === 'register' && (
          <RegisterPage setAuthToken={setAuthToken} setUserInfo={setUserInfo} setCurrentPage={setCurrentPage} />
        )}
        {!authToken && currentPage === 'login' && (
          <LoginPage setAuthToken={setAuthToken} setUserInfo={setUserInfo} setCurrentPage={setCurrentPage} />
        )}
        {authToken && (
          <EnterpriseDashboard userInfo={userInfo} authToken={authToken} />
        )}
      </main>

      <footer className="border-t border-slate-800 py-8 px-6 text-center text-sm text-slate-500 bg-slate-950">
        <p>© 2026 LexiMini AI — Indian B2B Enterprise Legal SaaS. Compliant with DPDP Act 2023 & IT Act 2000.</p>
      </footer>
    </div>
  );
}


// ==========================================
// 🏠 PAGE 1: PUBLIC LANDING & GUEST LEGAL SUITE
// ==========================================
function LandingPage({ onNavigate }) {
  const [activeGuestTab, setActiveGuestTab] = useState('analyzer'); // analyzer | chat | risk | drafter

  // Guest Agreement Analyzer State
  const [analysisText, setAnalysisText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  // Guest Legal Chat State
  const [chatPrompt, setChatPrompt] = useState('');
  const [chatAnswer, setChatAnswer] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Guest Risk Scanner State
  const [riskContractText, setRiskContractText] = useState('');
  const [riskContractType, setRiskContractType] = useState('Rent Agreement');
  const [riskResult, setRiskResult] = useState(null);
  const [scanningRisk, setScanningRisk] = useState(false);

  // Guest Drafter State
  const [draftType, setDraftType] = useState('Rent Agreement');
  const [party1, setParty1] = useState('');
  const [party2, setParty2] = useState('');
  const [detail1, setDetail1] = useState('');
  const [detail2, setDetail2] = useState('');
  const [draftResult, setDraftResult] = useState('');
  const [drafting, setDrafting] = useState(false);

  // Guest Document Upload Handler
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setAnalysisText(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  const runGuestAnalysis = async () => {
    if (!analysisText.trim()) return;
    setAnalyzing(true);
    setAnalysisResult(null);
    try {
      // Call Risk Analyzer & Key Extract API
      const resp = await axios.post('/api/v1/contract/analyze', {
        contract_text: analysisText,
        contract_type: 'Rent Agreement'
      });
      setAnalysisResult(resp.data);
    } catch (err) {
      alert('Analysis error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGuestChat = async () => {
    if (!chatPrompt.trim()) return;
    setChatLoading(true);
    setChatAnswer('');
    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: chatPrompt, domain: 'tenancy' })
      });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let full = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const token = line.slice(6);
            if (token !== '[DONE]') {
              full += token;
              setChatAnswer(full);
            }
          }
        }
      }
    } catch (err) {
      setChatAnswer('Error connecting to Legal AI Gateway.');
    } finally {
      setChatLoading(false);
    }
  };

  const handleGuestRiskScan = async () => {
    if (!riskContractText.trim()) return;
    setScanningRisk(true);
    try {
      const resp = await axios.post('/api/v1/contract/analyze', {
        contract_text: riskContractText,
        contract_type: riskContractType
      });
      setRiskResult(resp.data);
    } catch (err) {
      alert('Risk scan error');
    } finally {
      setScanningRisk(false);
    }
  };

  const handleGuestDraft = async () => {
    if (!party1 || !party2) return;
    setDrafting(true);
    try {
      const resp = await axios.post('/api/v1/contract/draft', {
        doc_type: draftType,
        party_1: party1,
        party_2: party2,
        details: { detail1, detail2 }
      });
      setDraftResult(resp.data.draft_text);
    } catch (err) {
      alert('Drafting error');
    } finally {
      setDrafting(false);
    }
  };

  return (
    <div className="space-y-16 py-6">
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-400 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-4 h-4" /> Domain-Specific Indian Legal Intelligence
        </div>
        <h1 className="text-5xl font-serif font-extrabold tracking-tight leading-tight gold-gradient-text">
          Enterprise B2B Legal AI & Document Intelligence
        </h1>
        <p className="text-lg text-slate-300 leading-relaxed">
          Index company policies, analyze vendor contracts, manage employee access, and query 400+ Indian statutory laws with complete tenant data isolation.
        </p>
        <div className="flex items-center justify-center gap-4 pt-2">
          <button 
            onClick={() => onNavigate('register')}
            className="px-6 py-3.5 bg-gradient-to-r from-gold-500 to-amber-600 text-slate-950 font-bold rounded-xl shadow-xl shadow-gold-500/20 hover:brightness-110 flex items-center gap-2 transition-all text-base"
          >
            <Building2 className="w-5 h-5" /> Register Company Workspace <ArrowRight className="w-4 h-4" />
          </button>
          <button 
            onClick={() => onNavigate('login')}
            className="px-6 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl border border-slate-700 flex items-center gap-2 transition-all text-base"
          >
            <LogIn className="w-5 h-5" /> Sign In to Portal
          </button>
        </div>
      </div>

      {/* 4 Feature Highlights Grid */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="glass-card p-6 rounded-xl space-y-3">
          <div className="p-3 bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded-lg w-fit">
            <Lock className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-serif font-bold text-gold-400">Isolated Company Vault</h3>
          <p className="text-sm text-slate-400">Upload HR handbooks & contracts. Multi-tenant vector retrieval ensures zero data leakage.</p>
        </div>
        <div className="glass-card p-6 rounded-xl space-y-3">
          <div className="p-3 bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded-lg w-fit">
            <Scale className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-serif font-bold text-gold-400">Indian Legal RAG</h3>
          <p className="text-sm text-slate-400">Trained on TPA 1882, BNS 2023, Model Tenancy Act, and Contract Act with statutory section citations.</p>
        </div>
        <div className="glass-card p-6 rounded-xl space-y-3">
          <div className="p-3 bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg w-fit">
            <FileSearch className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-serif font-bold text-gold-400">Contract Risk Scanner</h3>
          <p className="text-sm text-slate-400">Automated 0-100 risk score auditing rent agreements and NDAs for liabilities.</p>
        </div>
        <div className="glass-card p-6 rounded-xl space-y-3">
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg w-fit">
            <Users className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-serif font-bold text-gold-400">Team RBAC Access</h3>
          <p className="text-sm text-slate-400">Assign Company Admin & Employee roles, restrict departments, and track audit trails.</p>
        </div>
      </div>

      {/* PUBLIC GUEST LEGAL SUITE SECTION */}
      <div className="glass-panel p-8 rounded-2xl border border-gold-500/30 space-y-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h2 className="text-2xl font-serif font-bold text-gold-400 flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-gold-400" /> Public Guest Legal Suite
            </h2>
            <p className="text-sm text-slate-400">No registration required! Upload any individual agreement, query legal AI, or run risk scans instantly as a guest.</p>
          </div>
          <div className="flex bg-slate-900/90 p-1 rounded-xl border border-slate-800">
            <button 
              onClick={() => setActiveGuestTab('analyzer')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${
                activeGuestTab === 'analyzer' ? 'bg-gold-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileSearch className="w-4 h-4" /> Agreement Analyzer
            </button>
            <button 
              onClick={() => setActiveGuestTab('chat')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${
                activeGuestTab === 'chat' ? 'bg-gold-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Scale className="w-4 h-4" /> Legal AI Chat
            </button>
            <button 
              onClick={() => setActiveGuestTab('risk')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${
                activeGuestTab === 'risk' ? 'bg-gold-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <AlertTriangle className="w-4 h-4" /> Risk Scanner
            </button>
            <button 
              onClick={() => setActiveGuestTab('drafter')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${
                activeGuestTab === 'drafter' ? 'bg-gold-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileCode className="w-4 h-4" /> Auto Drafter
            </button>
          </div>
        </div>

        {/* GUEST TAB 1: AGREEMENT ANALYZER */}
        {activeGuestTab === 'analyzer' && (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <label className="block text-sm font-semibold text-slate-300">
                  Upload or Paste Individual Rent / Lease / NDA Agreement Text
                </label>
                <div className="flex items-center gap-3">
                  <label className="cursor-pointer px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-lg border border-slate-700 flex items-center gap-2">
                    <Upload className="w-4 h-4 text-gold-400" /> Choose TXT / PDF File
                    <input type="file" accept=".txt,.pdf" onChange={handleFileUpload} className="hidden" />
                  </label>
                  <span className="text-xs text-slate-400">or paste agreement clauses below:</span>
                </div>
                <textarea 
                  rows={8}
                  value={analysisText}
                  onChange={(e) => setAnalysisText(e.target.value)}
                  placeholder="Paste rent agreement clauses (e.g. Landlord agrees to lease Premises for Rs 25,000/month with 2 months security deposit. Either party may terminate with 1 month notice...)"
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl p-4 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
                />
                <button 
                  onClick={runGuestAnalysis}
                  disabled={analyzing || !analysisText.trim()}
                  className="w-full py-3 bg-gradient-to-r from-gold-500 to-amber-600 text-slate-950 font-bold rounded-xl shadow-lg hover:brightness-110 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                  {analyzing ? 'Analyzing Agreement Clauses...' : '🔍 Analyze Agreement & Explain Key Points'}
                </button>
              </div>

              <div className="space-y-4">
                <label className="block text-sm font-semibold text-slate-300">
                  Agreement Summary & Key Points Explanation
                </label>
                {analysisResult ? (
                  <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                      <span className="text-sm font-bold text-gold-400">Contract Risk Score</span>
                      <span className="text-2xl font-extrabold text-amber-400">{analysisResult.overall_risk_score}/100</span>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Key Clauses & Recommendations:</h4>
                      <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
                        {analysisResult.risks?.map((r, i) => (
                          <div key={i} className="p-3 bg-slate-800/80 border-l-2 border-amber-500 rounded text-xs space-y-1">
                            <div className="font-semibold text-slate-200">Clause: {r.clause}</div>
                            <div className="text-slate-400">{r.issue}</div>
                            <div className="text-gold-400">💡 Advice: {r.recommendation}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-900/50 border border-dashed border-slate-800 rounded-xl p-8 text-center text-slate-500 text-sm space-y-2">
                    <FileSearch className="w-10 h-10 mx-auto text-slate-600" />
                    <p>Upload or paste your agreement text to get an instant breakdown of key rights, obligations, and risk liabilities.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* GUEST TAB 2: LEGAL AI CHAT */}
        {activeGuestTab === 'chat' && (
          <div className="space-y-4">
            <label className="block text-sm font-semibold text-slate-300">Ask Any Question on Indian Law</label>
            <div className="flex gap-3">
              <input 
                type="text"
                value={chatPrompt}
                onChange={(e) => setChatPrompt(e.target.value)}
                placeholder="e.g. What is the statutory notice period required for eviction under Model Tenancy Act 2021?"
                className="flex-1 bg-slate-900/90 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
              />
              <button 
                onClick={handleGuestChat}
                disabled={chatLoading || !chatPrompt.trim()}
                className="px-6 py-3 bg-gold-500 text-slate-950 font-bold rounded-xl shadow-lg hover:bg-gold-400 disabled:opacity-50 transition-all"
              >
                {chatLoading ? 'Analyzing...' : 'Ask AI ⚖️'}
              </button>
            </div>
            {chatAnswer && (
              <div className="p-5 bg-slate-900/90 border border-slate-800 rounded-xl text-sm leading-relaxed whitespace-pre-wrap text-slate-200">
                {chatAnswer}
              </div>
            )}
          </div>
        )}

        {/* GUEST TAB 3: RISK SCANNER */}
        {activeGuestTab === 'risk' && (
          <div className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Contract Type</label>
                <select 
                  value={riskContractType} 
                  onChange={(e) => setRiskContractType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
                >
                  <option value="Rent Agreement">Rent Agreement</option>
                  <option value="NDA">Non-Disclosure Agreement (NDA)</option>
                  <option value="Employment Contract">Employment Contract</option>
                </select>
              </div>
            </div>
            <textarea 
              rows={6}
              value={riskContractText}
              onChange={(e) => setRiskContractText(e.target.value)}
              placeholder="Paste contract text here to perform automated clause risk audit..."
              className="w-full bg-slate-900/90 border border-slate-800 rounded-xl p-4 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
            />
            <button 
              onClick={handleGuestRiskScan}
              disabled={scanningRisk || !riskContractText.trim()}
              className="px-6 py-3 bg-red-500/20 border border-red-500/40 text-red-400 font-bold rounded-xl hover:bg-red-500/30 transition-all"
            >
              {scanningRisk ? 'Scanning Contract...' : '🔍 Run Risk Audit'}
            </button>
            {riskResult && (
              <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl space-y-3">
                <div className="font-bold text-amber-400">Risk Score: {riskResult.overall_risk_score}/100</div>
                {riskResult.risks?.map((r, i) => (
                  <div key={i} className="text-xs text-slate-300 border-l-2 border-red-500 pl-3">
                    <strong>{r.clause}:</strong> {r.issue}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* GUEST TAB 4: AUTO DRAFTER */}
        {activeGuestTab === 'drafter' && (
          <div className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Document Type</label>
                <select 
                  value={draftType}
                  onChange={(e) => setDraftType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200"
                >
                  <option value="Rent Agreement">Rent Agreement</option>
                  <option value="Legal Notice">Legal Notice</option>
                  <option value="NDA">NDA</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Party 1 Name</label>
                <input 
                  type="text" 
                  value={party1} 
                  onChange={(e) => setParty1(e.target.value)} 
                  placeholder="e.g. Ramesh Kumar (Landlord)"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200" 
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Party 2 Name</label>
                <input 
                  type="text" 
                  value={party2} 
                  onChange={(e) => setParty2(e.target.value)} 
                  placeholder="e.g. Priya Sharma (Tenant)"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200" 
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Key Detail 1</label>
                <input 
                  type="text" 
                  value={detail1} 
                  onChange={(e) => setDetail1(e.target.value)} 
                  placeholder="e.g. Rent Rs 25,000 / Cause of Notice"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200" 
                />
              </div>
            </div>
            <button 
              onClick={handleGuestDraft}
              disabled={drafting || !party1 || !party2}
              className="px-6 py-3 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-bold rounded-xl hover:bg-emerald-500/30 transition-all"
            >
              {drafting ? 'Drafting...' : '✍️ Generate Legal Document'}
            </button>
            {draftResult && (
              <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl space-y-3">
                <textarea rows={10} value={draftResult} readOnly className="w-full bg-slate-950 p-3 rounded text-xs font-mono text-slate-300" />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Enterprise Security Banner */}
      <div className="glass-card p-8 rounded-2xl border border-blue-500/30 text-center space-y-4">
        <h3 className="text-2xl font-serif font-bold text-gold-400">🛡️ Enterprise Security & Compliance SLA</h3>
        <p className="text-sm text-slate-300 max-w-3xl mx-auto leading-relaxed">
          LexiMini AI is engineered for enterprise privacy compliance under the <strong>Digital Personal Data Protection (DPDP) Act 2023</strong> and <strong>IT Act 2000</strong>. Corporate documents remain strictly within enterprise boundaries and are never shared for public AI training.
        </p>
        <div className="flex flex-wrap justify-center gap-6 text-sm font-semibold text-slate-300 pt-2">
          <span className="flex items-center gap-1.5"><CheckCircle className="w-4 h-4 text-emerald-400" /> Multi-Tenant Data Isolation</span>
          <span className="flex items-center gap-1.5"><CheckCircle className="w-4 h-4 text-emerald-400" /> TLS 1.3 & AES-256 Encryption</span>
          <span className="flex items-center gap-1.5"><CheckCircle className="w-4 h-4 text-emerald-400" /> Role-Based Access Control</span>
        </div>
      </div>
    </div>
  );
}


// ==========================================
// 🏢 PAGE 2: DEDICATED COMPANY REGISTER PAGE
// ==========================================
function RegisterPage({ setAuthToken, setUserInfo, setCurrentPage }) {
  const [orgName, setOrgName] = useState('');
  const [orgReg, setOrgReg] = useState('');
  const [adminName, setAdminName] = useState('');
  const [adminEmail, setAdminEmail] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [department, setDepartment] = useState('Legal & Compliance');
  const [termsAgreed, setTermsAgreed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!orgName || !adminName || !adminEmail || !adminPassword) {
      alert('Please fill all required fields.');
      return;
    }
    if (!termsAgreed) {
      alert('Please accept the Enterprise Data Isolation Rules to proceed.');
      return;
    }

    setLoading(true);
    try {
      const resp = await axios.post('/api/v1/org/register', {
        organization_name: orgName,
        registration_number: orgReg,
        admin_full_name: adminName,
        admin_email: adminEmail,
        admin_password: adminPassword,
        department: department
      });

      setAuthToken(resp.data.access_token);
      setUserInfo(resp.data.user);
      setCurrentPage('dashboard');
    } catch (err) {
      alert('Registration error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-6">
      <div>
        <h1 className="text-3xl font-serif font-bold text-gold-400">🏢 Register Enterprise Company Workspace</h1>
        <p className="text-sm text-slate-400 mt-1">Create a dedicated corporate tenant workspace. The registrant will automatically be designated as Company Admin.</p>
      </div>

      <div className="grid md:grid-cols-12 gap-8">
        {/* Left Column: Form */}
        <div className="md:col-span-7 glass-panel p-8 rounded-2xl space-y-6">
          <h2 className="text-xl font-serif font-bold text-slate-200">📋 Company & Admin Setup</h2>
          
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Organization Legal Name *</label>
              <input 
                type="text" 
                required
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                placeholder="e.g. Tata Consultancy Services / Apex Law Firm"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Reg No / CIN (Optional)</label>
                <input 
                  type="text" 
                  value={orgReg}
                  onChange={(e) => setOrgReg(e.target.value)}
                  placeholder="e.g. U72200MH2000PLC123456"
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Primary Department</label>
                <select 
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
                >
                  <option value="Legal & Compliance">Legal & Compliance</option>
                  <option value="Corporate Affairs">Corporate Affairs</option>
                  <option value="Human Resources">Human Resources</option>
                  <option value="Executive Leadership">Executive Leadership</option>
                  <option value="Finance">Finance</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Company Admin Full Name *</label>
              <input 
                type="text" 
                required
                value={adminName}
                onChange={(e) => setAdminName(e.target.value)}
                placeholder="e.g. Ananya Sharma"
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Work Email Address *</label>
                <input 
                  type="email" 
                  required
                  value={adminEmail}
                  onChange={(e) => setAdminEmail(e.target.value)}
                  placeholder="ananya@company.com"
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Password *</label>
                <input 
                  type="password" 
                  required
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-start gap-3 pt-2">
              <input 
                type="checkbox"
                id="terms"
                checked={termsAgreed}
                onChange={(e) => setTermsAgreed(e.target.checked)}
                className="mt-1 accent-gold-500"
              />
              <label htmlFor="terms" className="text-xs text-slate-400 leading-relaxed cursor-pointer">
                I agree to the Enterprise Data Isolation Policy, DPDP Act 2023 Compliance Rules, and Terms of Service.
              </label>
            </div>

            <button 
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-gradient-to-r from-gold-500 to-amber-600 text-slate-950 font-bold rounded-xl shadow-lg hover:brightness-110 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              {loading ? 'Creating Workspace...' : '🚀 Register Workspace & Access Portal'}
            </button>
          </form>
        </div>

        {/* Right Column: Rules & Governance Side Panel */}
        <div className="md:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-blue-500 space-y-5">
            <h3 className="text-lg font-serif font-bold text-blue-400 flex items-center gap-2">
              <Shield className="w-5 h-5" /> Enterprise Rules & Governance SLA
            </h3>

            <div className="space-y-4 text-xs">
              <div className="space-y-1">
                <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-gold-400" /> 1. Strict Tenant Data Isolation
                </div>
                <p className="text-slate-400 leading-relaxed">
                  All company policy documents uploaded to your vault are vector-indexed with a mandatory <code className="bg-slate-950 px-1 py-0.5 rounded text-gold-400">organization_id</code> metadata tag. Vectors from Company A can never be retrieved by Company B.
                </p>
              </div>

              <div className="space-y-1">
                <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-gold-400" /> 2. Admin & Role Hierarchy
                </div>
                <p className="text-slate-400 leading-relaxed">
                  The workspace registrant is granted <code className="bg-slate-950 px-1 py-0.5 rounded text-gold-400">COMPANY_ADMIN</code> rights to manage staff accounts, upload policy documents, and inspect audit trails.
                </p>
              </div>

              <div className="space-y-1">
                <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Scale className="w-3.5 h-3.5 text-gold-400" /> 3. Indian DPDP Act 2023 Compliance
                </div>
                <p className="text-slate-400 leading-relaxed">
                  Data processing strictly complies with Digital Personal Data Protection guidelines. Data is never repurposed for external AI training.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


// ==========================================
// 🔑 PAGE 3: DEDICATED SIGN IN PAGE
// ==========================================
function LoginPage({ setAuthToken, setUserInfo, setCurrentPage }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    try {
      const resp = await axios.post('/api/v1/auth/login', { email, password });
      setAuthToken(resp.data.access_token);
      setUserInfo(resp.data.user);
      setCurrentPage('dashboard');
    } catch (err) {
      alert('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-gold-400">🔑 Sign In to Workspace</h1>
        <p className="text-sm text-slate-400">Enter your company work email and password to access your enterprise vault.</p>
      </div>

      <div className="glass-panel p-8 rounded-2xl space-y-6">
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Work Email</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Password</label>
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
            />
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-gradient-to-r from-gold-500 to-amber-600 text-slate-950 font-bold rounded-xl shadow-lg hover:brightness-110 disabled:opacity-50 transition-all"
          >
            {loading ? 'Signing In...' : 'Sign In 🔑'}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-slate-800">
          <p className="text-xs text-slate-400">Don't have a company workspace?</p>
          <button 
            onClick={() => setCurrentPage('register')}
            className="text-xs font-semibold text-gold-400 hover:underline mt-1"
          >
            Register Organization Workspace
          </button>
        </div>
      </div>
    </div>
  );
}


// ==========================================
// 💼 PAGE 4: LOGGED-IN ENTERPRISE DASHBOARD
// ==========================================
function EnterpriseDashboard({ userInfo, authToken }) {
  const [activeTab, setActiveTab] = useState('overview'); // overview | vault | team | chat

  // Company Vault Upload State
  const [uploading, setUploading] = useState(false);
  const [vaultDocs, setVaultDocs] = useState([]);

  // Team Management State
  const [empName, setEmpName] = useState('');
  const [empEmail, setEmpEmail] = useState('');
  const [empPass, setEmpPass] = useState('');
  const [empDept, setEmpDept] = useState('Legal & Compliance');
  const [teamMembers, setTeamMembers] = useState([]);
  const [addingEmp, setAddingEmp] = useState(false);

  // Private RAG Chat State
  const [dashPrompt, setDashPrompt] = useState('');
  const [dashAnswer, setDashAnswer] = useState('');
  const [dashChatting, setDashChatting] = useState(false);

  useEffect(() => {
    fetchDocs();
    fetchTeam();
  }, []);

  const fetchDocs = async () => {
    try {
      const resp = await axios.get('/api/v1/org/documents', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setVaultDocs(resp.data.documents || []);
    } catch (err) {}
  };

  const fetchTeam = async () => {
    try {
      const resp = await axios.get('/api/v1/org/employees', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setTeamMembers(resp.data.employees || []);
    } catch (err) {}
  };

  const handleVaultUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('/api/v1/org/documents/upload', formData, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      alert(`Document ${file.name} successfully indexed in company vault!`);
      fetchDocs();
    } catch (err) {
      alert('Upload error');
    } finally {
      setUploading(false);
    }
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    if (!empName || !empEmail || !empPass) return;

    setAddingEmp(true);
    try {
      await axios.post('/api/v1/org/employees/add', {
        full_name: empName,
        email: empEmail,
        password: empPass,
        department: empDept
      }, {
        headers: { Authorization: `Bearer ${authToken}` }
      });

      alert(`Staff ${empName} added!`);
      setEmpName('');
      setEmpEmail('');
      setEmpPass('');
      fetchTeam();
    } catch (err) {
      alert('Error adding employee');
    } finally {
      setAddingEmp(false);
    }
  };

  const handleDashChat = async () => {
    if (!dashPrompt.trim()) return;
    setDashChatting(true);
    setDashAnswer('');

    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify({ 
          prompt: dashPrompt, 
          domain: 'tenancy',
          organization_id: userInfo?.organization_id 
        })
      });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let full = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const token = line.slice(6);
            if (token !== '[DONE]') {
              full += token;
              setDashAnswer(full);
            }
          }
        }
      }
    } catch (err) {
      setDashAnswer('Error querying corporate vault.');
    } finally {
      setDashChatting(false);
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Workspace Header */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border border-gold-500/30">
        <div>
          <h1 className="text-3xl font-serif font-bold text-gold-400">{userInfo?.organization_name}</h1>
          <p className="text-xs text-slate-400 mt-1">
            Logged in: <strong className="text-slate-200">{userInfo?.full_name}</strong> ({userInfo?.email}) | Role: <code className="bg-slate-900 px-1 py-0.5 rounded text-amber-400">{userInfo?.role}</code> | Dept: <code className="bg-slate-900 px-1 py-0.5 rounded text-blue-400">{userInfo?.department}</code>
          </p>
        </div>

        {/* Dashboard Navigation Tabs */}
        <div className="flex bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          <button 
            onClick={() => setActiveTab('overview')}
            aria-label="Dashboard Overview Tab"
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeTab === 'overview' ? 'bg-gold-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            📊 Overview
          </button>
          <button 
            onClick={() => setActiveTab('vault')}
            aria-label="Company Policy Vault Tab"
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeTab === 'vault' ? 'bg-gold-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            📁 Company Vault
          </button>
          <button 
            onClick={() => setActiveTab('team')}
            aria-label="Team Management Tab"
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeTab === 'team' ? 'bg-gold-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            👥 Team Management
          </button>
          <button 
            onClick={() => setActiveTab('chat')}
            aria-label="Enterprise Legal AI Assistant Tab"
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeTab === 'chat' ? 'bg-gold-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            ⚖️ Enterprise AI Chat
          </button>
        </div>
      </div>

      {/* TAB 1: OVERVIEW METRICS */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-4 gap-6">
            <div className="glass-card p-6 rounded-xl text-center space-y-1">
              <div className="text-3xl font-extrabold text-gold-400">ACTIVE</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Tenant Workspace</div>
            </div>
            <div className="glass-card p-6 rounded-xl text-center space-y-1">
              <div className="text-3xl font-extrabold text-blue-400">{vaultDocs.length} Docs</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Indexed Vault Storage</div>
            </div>
            <div className="glass-card p-6 rounded-xl text-center space-y-1">
              <div className="text-3xl font-extrabold text-emerald-400">{teamMembers.length} Members</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Active Staff Access</div>
            </div>
            <div className="glass-card p-6 rounded-xl text-center space-y-1">
              <div className="text-3xl font-extrabold text-amber-400">400+ Acts</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Indian Statutory RAG</div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: COMPANY POLICY VAULT */}
      {activeTab === 'vault' && (
        <div className="glass-panel p-8 rounded-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-xl font-serif font-bold text-gold-400">📁 Organization Legal & Policy Vault</h2>
              <p className="text-xs text-slate-400">Upload internal corporate handbooks, HR rules, NDAs, and commercial contracts for tenant-isolated RAG search.</p>
            </div>
            <label className="cursor-pointer px-4 py-2.5 bg-gold-500 hover:bg-gold-400 text-slate-950 font-bold text-sm rounded-xl shadow-lg flex items-center gap-2 transition-all">
              <Upload className="w-4 h-4" /> {uploading ? 'Uploading...' : 'Upload Policy (PDF/TXT)'}
              <input type="file" accept=".pdf,.txt" onChange={handleVaultUpload} className="hidden" />
            </label>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-300">📚 Indexed Vault Documents ({vaultDocs.length})</h3>
            {vaultDocs.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-4">
                {vaultDocs.map((doc, idx) => (
                  <div key={idx} className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl flex items-center gap-3">
                    <FileText className="w-8 h-8 text-gold-400" />
                    <div>
                      <div className="text-sm font-semibold text-slate-200">{doc.filename}</div>
                      <div className="text-xs text-slate-500">Size: {doc.file_size} bytes | Status: <span className="text-emerald-400 font-semibold">INDEXED</span></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-slate-500 text-sm bg-slate-900/50 rounded-xl border border-dashed border-slate-800">
                No uploaded policy documents yet. Upload your first document above.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: TEAM MANAGEMENT */}
      {activeTab === 'team' && (
        <div className="glass-panel p-8 rounded-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-xl font-serif font-bold text-gold-400">👥 Team Staff & Access Control</h2>
              <p className="text-xs text-slate-400">Grant employees access to your company legal AI portal and policy vault.</p>
            </div>
          </div>

          {userInfo?.role === 'COMPANY_ADMIN' ? (
            <form onSubmit={handleAddEmployee} className="p-4 bg-slate-900/90 border border-slate-800 rounded-xl grid md:grid-cols-4 gap-3">
              <input 
                type="text"
                required
                placeholder="Full Name"
                value={empName}
                onChange={(e) => setEmpName(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100"
              />
              <input 
                type="email"
                required
                placeholder="Work Email"
                value={empEmail}
                onChange={(e) => setEmpEmail(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100"
              />
              <input 
                type="password"
                required
                placeholder="Temp Password"
                value={empPass}
                onChange={(e) => setEmpPass(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100"
              />
              <button 
                type="submit"
                disabled={addingEmp}
                className="bg-gold-500 text-slate-950 font-bold text-xs rounded-lg p-2.5 hover:bg-gold-400 transition-all"
              >
                {addingEmp ? 'Adding...' : '➕ Add Staff Member'}
              </button>
            </form>
          ) : (
            <div className="p-3 bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded-lg text-xs">
              🔒 Team management is restricted to Company Admins.
            </div>
          )}

          <div className="space-y-2">
            <h3 className="text-sm font-bold text-slate-300">👥 Active Organization Team ({teamMembers.length})</h3>
            <div className="divide-y divide-slate-800">
              {teamMembers.map((m, i) => (
                <div key={i} className="py-3 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-semibold text-slate-200">{m.full_name}</span>
                    <span className="text-slate-500 ml-2">({m.email})</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="bg-slate-800 text-gold-400 px-2 py-0.5 rounded font-mono">{m.role}</span>
                    <span className="bg-slate-800 text-blue-400 px-2 py-0.5 rounded font-mono">{m.department}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: ENTERPRISE LEGAL AI CHAT */}
      {activeTab === 'chat' && (
        <div className="glass-panel p-8 rounded-2xl space-y-6">
          <div>
            <h2 className="text-xl font-serif font-bold text-gold-400">⚖️ Enterprise Private Legal AI</h2>
            <p className="text-xs text-slate-400">Queries both Indian statutory law and your organization's private policy vault.</p>
          </div>

          <div className="space-y-4">
            <textarea 
              rows={4}
              value={dashPrompt}
              onChange={(e) => setDashPrompt(e.target.value)}
              placeholder="e.g. As per our company HR policy and Indian Labour laws, what is the mandatory notice period for resignation?"
              className="w-full bg-slate-900/90 border border-slate-800 rounded-xl p-4 text-sm text-slate-100 focus:border-gold-500/50 focus:outline-none"
            />
            <button 
              onClick={handleDashChat}
              disabled={dashChatting || !dashPrompt.trim()}
              className="px-6 py-3 bg-gradient-to-r from-gold-500 to-amber-600 text-slate-950 font-bold rounded-xl shadow-lg hover:brightness-110 disabled:opacity-50 transition-all"
            >
              {dashChatting ? 'Analyzing Vault...' : 'Ask Enterprise Legal AI ⚖️'}
            </button>
            {dashAnswer && (
              <div className="p-5 bg-slate-900/90 border border-slate-800 rounded-xl text-sm leading-relaxed whitespace-pre-wrap text-slate-200">
                {dashAnswer}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

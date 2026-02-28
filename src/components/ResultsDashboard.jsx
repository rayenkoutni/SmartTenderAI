import React, { useState, useEffect } from 'react';
import { Award, Briefcase, CheckCircle2, FileSearch, XCircle, RotateCcw, AlertTriangle, FileText, Download, Loader2 } from 'lucide-react';
import emailjs from 'emailjs-com';
import './ResultsDashboard.css';

const ResultsDashboard = ({ onStartOver }) => {
    const [candidates, setCandidates] = useState([]);
    const [tenderReq, setTenderReq] = useState(null);
    const [selectedCandidateId, setSelectedCandidateId] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [fetchError, setFetchError] = useState(null);
    const [noData, setNoData] = useState(false);
    const [mailStatus, setMailStatus] = useState(null);

    const handleSendMail = async () => {
        if (!candidates.length || !selectedCandidateId) return;
        const selectedData = candidates.find(c => c.id === selectedCandidateId);
        const candidateEmail = selectedData.profile.email || '';
        const result = selectedData.matchingInfo.matching_explanation;
        const status = selectedData.matchingInfo.matching_explanation.overall_status || (selectedData.score >= 40 ? 'Suitable' : 'Not suitable');
        let reason = '';
        let templateId = '';
        if (selectedData.score >= 40) {
            reason = selectedData.bidDraft || 'You meet the requirements.';
            templateId = process.env.EMAIL_JS_TEMPLATE_VALIDATION || 'template_5s7hlc9';
        } else {
            reason = 'Reasons: ';
            if (result.experience_match !== 'Meets') reason += 'Experience does not meet requirements. ';
            if (result.missing_skills && result.missing_skills.length > 0) reason += 'Missing required skills. ';
            if (result.certification_match && result.certification_match.length === 0) reason += 'Required certifications not satisfied. ';
            templateId = process.env.EMAIL_JS_TEMPLATE_REJECTION || 'template_0c0y28k';
        }
        setMailStatus('Sending...');
        try {
            await emailjs.send(
                process.env.EMAIL_JS_SERVICE_ID || 'service_ko3lfks',
                templateId,
                {
                    to_email: candidateEmail,
                    status,
                    reason,
                    candidate_name: selectedData.profile.name
                },
                process.env.EMAIL_JS_API_KEY || '8gjZqa7ygevnQatFqW2JW'
            );
            setMailStatus('Mail sent successfully!');
        } catch (err) {
            setMailStatus('Failed to send mail.');
        }
    };

    useEffect(() => {
        const fetchAnalysisData = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/intelligence/analyze');
                if (!response.ok) {
                    const errData = await response.json().catch(() => ({}));
                    setFetchError(errData.error || `Server error: ${response.status}`);
                    return;
                }

                const data = await response.json();
                if (!data.candidates || data.candidates.length === 0) {
                    setNoData(true);
                    return;
                }
                setTenderReq(data.tender_requirements);
                setCandidates(data.candidates);

                if (data.candidates.length > 0) {
                    setSelectedCandidateId(data.candidates[0].id);
                }
            } catch (err) {
                setFetchError('Cannot connect to Python backend at port 5000. Is it running?');
            } finally {
                setIsLoading(false);
            }
        };

        fetchAnalysisData();
    }, []);

    if (isLoading) return (
        <div style={{ padding: '64px', textAlign: 'center', minHeight: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <Loader2 size={40} className="spin" color="var(--primary)" />
            <h3 style={{ marginTop: '16px' }}>Analyzing Candidates...</h3>
            <p className="text-muted" style={{ marginTop: '8px' }}>Your candidates are being matched against tender requirements. This may take a moment.</p>
        </div>
    );

    if (fetchError) return (
        <div style={{ padding: '64px', textAlign: 'center' }}>
            <AlertTriangle size={40} color="#da1e28" style={{ margin: '0 auto 16px' }} />
            <h3>Backend Connection Error</h3>
            <p className="text-muted" style={{ marginTop: '8px', maxWidth: '400px', margin: '8px auto' }}>{fetchError}</p>
            <button className="btn btn-outline mt-4" onClick={onStartOver}><RotateCcw size={16} /> Start Over</button>
        </div>
    );

    if (noData) return (
        <div style={{ padding: '64px', textAlign: 'center' }}>
            <FileSearch size={40} color="var(--primary)" style={{ margin: '0 auto 16px' }} />
            <h3>No analysis results yet</h3>
            <p className="text-muted" style={{ marginTop: '8px', maxWidth: '400px', margin: '8px auto' }}>
                No candidates were found or analyzed. Please go back and re-upload your tender document and CVs.
            </p>
            <button className="btn btn-primary mt-4" onClick={onStartOver}><RotateCcw size={16} /> Upload Documents</button>
        </div>
    );

    if (!tenderReq || candidates.length === 0) return null;

    const selectedData = candidates.find(c => c.id === selectedCandidateId);
    const { profile, matchingInfo, bidDraft } = selectedData;
    const matchDetails = matchingInfo.matching_explanation;

    return (
        <div className="results-dashboard">
            <div className="dashboard-header flex justify-between items-center mb-4">
                <div>
                    <h2 style={{ fontSize: '28px' }}>Best Matching Profiles</h2>
                    <p className="text-muted mt-1">Matched against the uploaded tender requirements</p>
                </div>
                <button className="btn btn-outline" onClick={onStartOver}>
                    <RotateCcw size={16} /> New Match
                </button>
            </div>



            <div className="dashboard-grid mt-4">
                <div className="candidates-column">
                    {candidates.map((candidate) => (
                        <div
                            key={candidate.id}
                            className={`card candidate-card ${selectedCandidateId === candidate.id ? 'selected' : ''}`}
                            onClick={() => setSelectedCandidateId(candidate.id)}
                        >
                            <div className="candidate-header flex justify-between">
                                <div>
                                    <h3 className="candidate-name">{candidate.profile.name}</h3>
                                    <p className="text-muted mt-1" style={{ fontSize: '13px' }}>
                                        {candidate.profile.experience_years} years exp • {candidate.profile.sector_experience?.[0] || 'IT'}
                                        {candidate.llm_used === false && <span style={{ marginLeft: '6px', fontSize: '11px', background: '#f4f4f4', border: '1px solid #ddd', borderRadius: '4px', padding: '1px 5px', color: '#777' }}>regex</span>}
                                        {candidate.llm_used === true && <span style={{ marginLeft: '6px', fontSize: '11px', background: '#e8f4fd', border: '1px solid #a8d5f5', borderRadius: '4px', padding: '1px 5px', color: '#0063c0' }}>AI</span>}
                                    </p>
                                </div>
                                <div className="score-badge">
                                    <Award size={16} color="var(--primary)" style={{ marginRight: '6px' }} />
                                    <span className="score-value">{candidate.score}%</span>
                                </div>
                            </div>

                            <div className="score-bar-container mt-3 mb-3">
                                <div
                                    className="score-bar-fill"
                                    style={{
                                        width: `${candidate.score}%`,
                                        backgroundColor: candidate.score >= 80 ? 'var(--success)' : candidate.score >= 50 ? 'var(--primary)' : '#f1c21b'
                                    }}
                                ></div>
                            </div>

                            <div className="skills-preview text-muted" style={{ fontSize: '13px' }}>
                                <strong style={{ color: 'var(--text-main)' }}>Matched: </strong>
                                {candidate.matchingInfo.matching_explanation.matched_skills.slice(0, 3).join(', ')}
                                {candidate.matchingInfo.matching_explanation.matched_skills.length > 3 && '...'}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="explainability-column">
                    <div className="card explainability-card">

                        <div className="explainability-header flex items-center mb-4 text-muted justify-between" style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '16px' }}>
                            <div className="flex items-center gap-2">
                                <div style={{ backgroundColor: 'rgba(15, 98, 254, 0.1)', padding: '8px', borderRadius: '8px' }}>
                                    <FileSearch size={20} color="var(--primary)" />
                                </div>
                                <h3 style={{ fontSize: '18px', color: 'var(--text-main)' }}>AI Analysis: {profile.name}</h3>
                            </div>
                            <span className="tag" style={{ backgroundColor: '#F0F6FF', color: 'var(--primary)', border: '1px solid currentColor' }}>
                                Strict Mapping Enforced
                            </span>
                        </div>

                        {/* Structured Requirement Matching */}
                        <div className="criteria-grid mt-4">

                            <div className="criteria-row">
                                <div className="criteria-label">Experience Match</div>
                                <div className="criteria-value">
                                    {matchDetails.experience_match === "Meets" ? (
                                        <span className="tag badge-success"><CheckCircle2 size={12} className="mr-1" /> {matchDetails.experience_match}</span>
                                    ) : matchDetails.experience_match === "Does not meet" ? (
                                        <span className="tag" style={{ backgroundColor: '#FFF1F1', color: '#da1e28' }}><XCircle size={12} className="mr-1" /> {matchDetails.experience_match}</span>
                                    ) : <span className="tag">{matchDetails.experience_match}</span>}
                                    <span className="text-muted ml-2" style={{ fontSize: '13px' }}>({profile.experience_years} vs {tenderReq.experience_years} req)</span>
                                </div>
                            </div>

                            <div className="criteria-row">
                                <div className="criteria-label">Sector Match</div>
                                <div className="criteria-value">
                                    {matchDetails.sector_match === "Yes" ? (
                                        <span className="tag badge-success"><CheckCircle2 size={12} className="mr-1" /> {matchDetails.sector_match}</span>
                                    ) : matchDetails.sector_match === "No" ? (
                                        <span className="tag" style={{ backgroundColor: '#FFF1F1', color: '#da1e28' }}><XCircle size={12} className="mr-1" /> {matchDetails.sector_match}</span>
                                    ) : <span className="tag">{matchDetails.sector_match}</span>}
                                </div>
                            </div>

                            <div className="criteria-row">
                                <div className="criteria-label">Required Certs</div>
                                <div className="criteria-value">
                                    {matchDetails.certification_match.length > 0 ? (
                                        matchDetails.certification_match.map(c => <span key={c} className="tag badge-success mr-1">{c}</span>)
                                    ) : (
                                        <span className="text-muted italic" style={{ fontSize: '13px' }}>None matched</span>
                                    )}
                                </div>
                            </div>

                        </div>

                        {/* Skills Mapping View */}
                        <div className="requirements-breakdown mt-4">
                            <h4 className="mb-3" style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)' }}>
                                Required Skills Mapping
                            </h4>
                            <ul className="requirements-list">
                                {tenderReq.skills.map((reqSkill, index) => {
                                    const isMatch = matchDetails.matched_skills.some(s => s.toLowerCase() === reqSkill.toLowerCase() || reqSkill.toLowerCase().includes(s.toLowerCase()));
                                    return (
                                        <li key={index} className={`requirement-item ${isMatch ? 'match' : 'missing'}`}>
                                            {isMatch ? <CheckCircle2 size={18} color="var(--success)" /> : <XCircle size={18} color="#da1e28" />}
                                            <span style={{ fontSize: '14px', fontWeight: isMatch ? 500 : 400 }}>{reqSkill}</span>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>

                        {/* AI Generated Bid Draft Paragraph Phase 4 - Hidden if score is too low */}
                        {selectedData.score >= 40 ? (
                            <div className="bid-draft-section mt-4 pt-4" style={{ borderTop: '1px solid var(--border-light)' }}>
                                <h4 className="mb-3 flex items-center gap-2" style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)' }}>
                                    <FileText size={16} />
                                    Draft Bid Paragraph (Auto-generated)
                                </h4>
                                <div className="draft-content" style={{ padding: '16px', backgroundColor: '#F8FBFF', borderLeft: '3px solid var(--primary)', borderRadius: '4px', fontSize: '14px', lineHeight: '1.6', color: 'var(--text-main)' }}>
                                    {bidDraft}
                                </div>
                                <p className="text-muted mt-2" style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <AlertTriangle size={12} /> This draft relies purely on extracted candidate facts. Human validation is required.
                                </p>
                            </div>
                        ) : (
                            <div className="bid-draft-section mt-4 pt-4" style={{ borderTop: '1px solid var(--border-light)', textAlign: 'center' }}>
                                <div style={{ padding: '24px', backgroundColor: '#FAFAFA', borderRadius: '8px', border: '1px solid #E0E0E0' }}>
                                    <AlertTriangle size={24} color="#da1e28" style={{ margin: '0 auto 12px' }} />
                                    <h4 style={{ fontSize: '14px', color: 'var(--text-main)', marginBottom: '8px' }}>Candidate match too low</h4>
                                    <p className="text-muted" style={{ fontSize: '13px', maxWidth: '250px', margin: '0 auto' }}>
                                        This profile does not meet the minimum requirements necessary to auto-generate a valid bid proposal.
                                    </p>
                                </div>
                            </div>
                        )}

                        <button className="btn btn-primary w-full mt-4" style={{ padding: '14px' }} onClick={handleSendMail}>
                            <FileText size={18} className="mr-2" />
                            {selectedData.score >= 40 ? 'Send Validation Result to Candidate' : 'Send Rejection Email to Candidate'}
                        </button>
                        {mailStatus && (
                            <div className="mail-status mt-2" style={{ textAlign: 'center', color: mailStatus.includes('success') ? 'var(--success)' : '#da1e28' }}>
                                {mailStatus}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResultsDashboard;

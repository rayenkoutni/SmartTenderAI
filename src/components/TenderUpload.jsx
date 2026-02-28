import React, { useState, useEffect } from 'react';
import { UploadCloud, FileText, CheckCircle2, Loader2, Search, Briefcase, MapPin, Target, Shield, UserCheck, Lock } from 'lucide-react';
import './TenderUpload.css';

const TenderUpload = ({ onNext }) => {
    const [file, setFile] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [loadingStep, setLoadingStep] = useState(0);

    const loadingMessages = [
        "Extracting document structure...",
        "Identifying required skills...",
        "Analyzing experience requirements...",
        "Preparing matching criteria..."
    ];

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;
        setIsAnalyzing(true);
        setLoadingStep(0);

        const formData = new FormData();
        formData.append('file', file);

        try {
            await fetch('http://127.0.0.1:5000/api/upload-tender', {
                method: 'POST',
                body: formData
            });

            // Simulate AI analysis steps visually
            let step = 0;
            const interval = setInterval(() => {
                step++;
                if (step < loadingMessages.length) {
                    setLoadingStep(step);
                } else {
                    clearInterval(interval);
                    setTimeout(() => {
                        setIsAnalyzing(false);
                        onNext();
                    }, 800);
                }
            }, 1000);

        } catch (error) {
            console.error("Error uploading tender:", error);
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="upload-page enterprise-upload">
            <div className="upload-header text-center mb-4">
                <h2>Upload Tender Document</h2>
                <p className="description-text mt-2">
                    SmartTender AI analyzes tender documents to extract qualification criteria and prepare expert matching.
                </p>
            </div>

            <div className={`upload-zone card ${file ? 'has-file' : ''}`}>
                {!file ? (
                    <div className="upload-zone-content">
                        <div className="upload-icon-container">
                            <UploadCloud size={40} color="var(--primary)" />
                        </div>
                        <h3 style={{ fontSize: '18px' }}>Drag & Drop your tender document</h3>
                        <p className="text-muted mt-1 mb-3" style={{ fontSize: '14px' }}>Supports PDF, DOCX (Max 20MB)</p>
                        <input
                            type="file"
                            id="tender-upload"
                            className="hidden-input"
                            accept=".pdf,.doc,.docx"
                            onChange={handleFileChange}
                        />
                        <label htmlFor="tender-upload" className="btn btn-primary browse-btn">
                            Browse Files
                        </label>
                    </div>
                ) : (
                    <div className="file-preview-enterprise">
                        <div className="file-icon-enterprise">
                            <FileText size={24} color="var(--primary)" />
                        </div>
                        <div className="file-details">
                            <span className="file-name">{file.name}</span>
                            <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB • Ready for analysis</span>
                        </div>
                        <button className="btn-icon" onClick={() => setFile(null)} aria-label="Remove file">✕</button>
                    </div>
                )}
            </div>

            {/* Visible AI Intelligence Panel */}
            <div className="ai-intelligence-panel mt-4">
                <h4 className="panel-title mb-3">What the AI will do</h4>
                <div className="ai-steps-grid">
                    <div className="ai-step">
                        <Search size={18} className="ai-step-icon" />
                        <span style={{ fontWeight: 500 }}>Extract required skills</span>
                    </div>
                    <div className="ai-step">
                        <Briefcase size={18} className="ai-step-icon" />
                        <span style={{ fontWeight: 500 }}>Identify experience & certs</span>
                    </div>
                    <div className="ai-step">
                        <MapPin size={18} className="ai-step-icon" />
                        <span style={{ fontWeight: 500 }}>Detect sector constraints</span>
                    </div>
                    <div className="ai-step">
                        <Target size={18} className="ai-step-icon" />
                        <span style={{ fontWeight: 500 }}>Prepare matching criteria</span>
                    </div>
                </div>
            </div>

            <div className="action-footer text-center mt-4 pt-2">
                <button
                    className={`btn btn-primary analyze-btn ${isAnalyzing ? 'analyzing' : ''}`}
                    disabled={!file || isAnalyzing}
                    onClick={handleAnalyze}
                    style={{ boxShadow: isAnalyzing ? 'none' : '0 4px 14px rgba(15, 98, 254, 0.25)' }}
                >
                    {isAnalyzing ? (
                        <div className="loading-state">
                            <Loader2 size={20} className="spin" />
                            <span>{loadingMessages[loadingStep]}</span>
                        </div>
                    ) : (
                        <>
                            Analyze Tender
                            <CheckCircle2 size={20} />
                        </>
                    )}
                </button>
                <p className="note text-muted mt-2 analyze-helper">
                    AI analysis usually takes 5–10 seconds.
                </p>
            </div>

            {/* Enterprise Trust Signals */}
            <div className="trust-signals mt-4 pt-4 text-muted">
                <div className="trust-signal">
                    <Shield size={14} />
                    <span>Explainable AI scoring</span>
                </div>
                <div className="trust-signal-dot">•</div>
                <div className="trust-signal">
                    <UserCheck size={14} />
                    <span>Human validation required before submission</span>
                </div>
                <div className="trust-signal-dot">•</div>
                <div className="trust-signal">
                    <Lock size={14} />
                    <span>Enterprise-ready, audit-friendly</span>
                </div>
            </div>
        </div>
    );
};

export default TenderUpload;

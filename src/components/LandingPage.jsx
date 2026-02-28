import React from 'react';
import { ArrowRight, BrainCircuit, FileSearch, Users, Zap } from 'lucide-react';
import './LandingPage.css';

const LandingPage = ({ onNext }) => {
    return (
        <div className="landing-page">
            <div className="hero-section text-center">
                <div className="hero-icon">
                    <BrainCircuit size={48} color="var(--primary)" />
                </div>
                <h1 className="hero-title">SmartTender AI</h1>
                <p className="hero-subtitle">
                    Automate tender analysis and expert selection with AI
                </p>
                <p className="hero-description text-muted">
                    SmartTender AI helps enterprise bid managers and technical leads effortlessly analyze complex
                    tender documents and automatically match the most qualified consultant CVs from your database.
                    Reduce bid preparation time by up to 80%.
                </p>
                <button className="btn btn-primary cta-button mt-4" onClick={onNext}>
                    Start Tender Analysis
                    <ArrowRight size={18} />
                </button>
            </div>

            <div className="features-grid mt-4">
                <div className="card feature-card text-center">
                    <div className="feature-icon mb-2">
                        <FileSearch size={32} color="var(--primary)" />
                    </div>
                    <h3>1. Analyze Tenders</h3>
                    <p className="text-muted mt-1">Our AI instantly extracts key required skills, experience, and criteria from any PDF or DOC tender.</p>
                </div>
                <div className="card feature-card text-center">
                    <div className="feature-icon mb-2">
                        <Users size={32} color="var(--primary)" />
                    </div>
                    <h3>2. Match Consultant CVs</h3>
                    <p className="text-muted mt-1">Automatically compare your candidate pool against the extracted requirements.</p>
                </div>
                <div className="card feature-card text-center">
                    <div className="feature-icon mb-2">
                        <Zap size={32} color="var(--primary)" />
                    </div>
                    <h3>3. Get Ranked Results</h3>
                    <p className="text-muted mt-1">Review the best matching profiles with an intuitive explainability dashboard.</p>
                </div>
            </div>
        </div>
    );
};

export default LandingPage;

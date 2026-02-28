import React, { useState } from 'react';
import { BrainCircuit, CheckCircle2, ChevronRight, FileText, UploadCloud, Users } from 'lucide-react';
import LandingPage from './components/LandingPage';
import TenderUpload from './components/TenderUpload';
import CvUpload from './components/CvUpload';
import ResultsDashboard from './components/ResultsDashboard';

function App() {
  const [currentStep, setCurrentStep] = useState(1);

  const goNext = () => setCurrentStep(prev => prev + 1);
  const goStep = (step) => setCurrentStep(step);

  return (
    <div className="layout">
      <header className="header">
        <div className="container header-content">
          <div className="logo" onClick={() => goStep(1)}>
            <BrainCircuit size={28} />
            SmartTender AI
          </div>
          <nav className="progress-nav">
            <div className={`progress-item ${currentStep === 1 ? 'active' : ''}`}>
              <span>1. Overview</span>
            </div>
            <div className={`progress-item ${currentStep === 2 ? 'active' : ''}`}>
              <span>2. Tender Analysis</span>
            </div>
            <div className={`progress-item ${currentStep === 3 ? 'active' : ''}`}>
              <span>3. Candidate Matching</span>
            </div>
            <div className={`progress-item ${currentStep === 4 ? 'active' : ''}`}>
              <span>4. Results</span>
            </div>
          </nav>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          {currentStep === 1 && <LandingPage onNext={goNext} />}
          {currentStep === 2 && <TenderUpload onNext={goNext} />}
          {currentStep === 3 && <CvUpload onNext={goNext} />}
          {currentStep === 4 && <ResultsDashboard onStartOver={() => goStep(1)} />}
        </div>
      </main>
    </div>
  );
}

export default App;

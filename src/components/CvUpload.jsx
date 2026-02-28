import React, { useState } from 'react';
import { Users, FileText, Play } from 'lucide-react';
import './TenderUpload.css'; // Reuse upload styles

const CvUpload = ({ onNext }) => {
    const [files, setFiles] = useState([]);
    const [isMatching, setIsMatching] = useState(false);

    const handleFileChange = (e) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files);
            setFiles(prev => [...prev, ...newFiles]);
        }
    };

    const removeFile = (index) => {
        setFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleRunMatching = async () => {
        setIsMatching(true);

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });

        try {
            await fetch('http://127.0.0.1:5000/api/upload-cvs', {
                method: 'POST',
                body: formData
            });
            setIsMatching(false);
            onNext();
        } catch (error) {
            console.error("Error uploading CVs:", error);
            setIsMatching(false);
        }
    };

    return (
        <div className="upload-page">
            <div className="upload-header text-center mb-4">
                <h2>Upload Candidate CVs</h2>
                <p className="text-muted mt-1">
                    Upload multiple CVs to compare against the active tender requirements.
                </p>
            </div>

            <div className="upload-zone card">
                <div className="upload-zone-content">
                    <div className="upload-icon-container">
                        <Users size={48} color="var(--primary)" />
                    </div>
                    <h3>Select candidate CVs</h3>
                    <p className="text-muted mt-1 mb-3">You can upload up to 50 CVs at once (PDF, DOCX)</p>
                    <input
                        type="file"
                        id="cv-upload"
                        className="hidden-input"
                        accept=".pdf,.doc,.docx"
                        multiple
                        onChange={handleFileChange}
                    />
                    <label htmlFor="cv-upload" className="btn btn-secondary">
                        Browse Files
                    </label>
                </div>
            </div>

            {files.length > 0 && (
                <div className="files-list mt-3">
                    <p className="mb-2 font-weight-500">{files.length} CV(s) Ready for Matching</p>
                    <div className="files-container" style={{ maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', paddingRight: '4px' }}>
                        {files.map((file, idx) => (
                            <div key={idx} className="card file-preview" style={{ padding: '12px', minHeight: 'auto' }}>
                                <div className="file-info" style={{ gap: '12px' }}>
                                    <FileText size={20} color="var(--primary)" />
                                    <span className="file-name" style={{ fontSize: '14px' }}>{file.name}</span>
                                </div>
                                <button className="btn-icon" onClick={() => removeFile(idx)}>✕</button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="action-footer text-center mt-4">
                <button
                    className="btn btn-primary analyze-btn"
                    disabled={files.length === 0 || isMatching}
                    onClick={handleRunMatching}
                >
                    {isMatching ? (
                        <>
                            Running Matching Algorithm...
                        </>
                    ) : (
                        <>
                            Run Matching
                            <Play size={18} fill="currentColor" />
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

export default CvUpload;

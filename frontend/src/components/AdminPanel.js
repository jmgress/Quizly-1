import React, { useState } from 'react';
import AdminQuestions from './AdminQuestions';
import LLMSettings from './LLMSettings';

const AdminPanel = ({ onGoHome }) => {
  const [activeTab, setActiveTab] = useState('questions');

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🛠️ Admin Panel</h1>
        <p>Manage questions and LLM configuration</p>
        <button className="button" onClick={onGoHome}>
          Back to Home
        </button>
      </div>

      <div className="tab-buttons">
        <button
          className={`tab-button ${activeTab === 'questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('questions')}
        >
          Questions
        </button>
        <button
          className={`tab-button ${activeTab === 'llm' ? 'active' : ''}`}
          onClick={() => setActiveTab('llm')}
        >
          LLM Settings
        </button>
      </div>

      {activeTab === 'questions' && <AdminQuestions onGoHome={onGoHome} hideHeader />}
      {activeTab === 'llm' && <LLMSettings />}
    </div>
  );
};

export default AdminPanel;

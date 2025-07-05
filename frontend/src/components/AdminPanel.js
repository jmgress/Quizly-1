import React, { useState } from 'react';
import AdminQuestions from './AdminQuestions';
import LLMSettings from './LLMSettings';
import LoggingSettings from './LoggingSettings';

const AdminPanel = ({ onGoHome }) => {
  const [activeTab, setActiveTab] = useState('questions');

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🛠️ Admin Panel</h1>
        <p>Manage quiz questions, LLM settings and logging</p>
        <button className="button" onClick={onGoHome}>
          Back to Home
        </button>
      </div>

      <div className="admin-tabs">
        <button 
          className={`tab-button ${activeTab === 'questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('questions')}
        >
          📝 Questions
        </button>
        <button
          className={`tab-button ${activeTab === 'llm' ? 'active' : ''}`}
          onClick={() => setActiveTab('llm')}
        >
          🤖 LLM Settings
        </button>
        <button
          className={`tab-button ${activeTab === 'logging' ? 'active' : ''}`}
          onClick={() => setActiveTab('logging')}
        >
          📜 Logging
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'questions' && (
          <AdminQuestions hideHeader={true} />
        )}
        {activeTab === 'llm' && (
          <LLMSettings />
        )}
        {activeTab === 'logging' && (
          <LoggingSettings />
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
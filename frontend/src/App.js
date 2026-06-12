import { useState } from 'react';
import Dashboard from './Dashboard';
import './App.css';

const AGENTS = [
  { id: 'query', label: '📊 Ask About Data', endpoint: '/agent/query', param: 'question' },
  { id: 'anomaly', label: '⚠️ Detect Anomalies', endpoint: '/agent/anomaly', param: null },
  { id: 'report', label: '📄 Generate Report', endpoint: '/agent/report', param: 'country' },
  { id: 'rag', label: '📚 Ask Past Reports', endpoint: '/agent/rag', param: 'question' },
];

const API_BASE = 'http://localhost:8000';

function App() {
  const [view, setView] = useState('chat');
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi! I\'m the Atlas Bank AI Assistant. Pick an agent and ask away!' }
  ]);
  const [input, setInput] = useState('');
  const [agent, setAgent] = useState(AGENTS[0]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() && agent.param) return;

    const userText = input.trim() || `(${agent.label})`;
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setInput('');
    setLoading(true);

    try {
      let url = `${API_BASE}${agent.endpoint}`;
      if (agent.param) {
        url += `?${agent.param}=${encodeURIComponent(userText)}`;
      }

      const res = await fetch(url);
      const data = await res.json();

      let replyText = '';
      if (data.error) {
        replyText = `❌ Error: ${data.error}`;
      } else if (data.summary) {
        replyText = data.summary;
      } else if (data.anomalies) {
        replyText = data.anomalies;
      } else if (data.report) {
        replyText = data.report;
      } else if (data.answer) {
        replyText = data.answer;
      } else {
        replyText = JSON.stringify(data, null, 2);
      }

      setMessages(prev => [...prev, { sender: 'bot', text: replyText }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: `❌ Failed to reach API: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="app">
      <div className="header">
        <h1>🏦 Atlas Bank AI Assistant</h1>
        <div className="view-switcher">
          <button className={view === 'chat' ? 'view-btn active' : 'view-btn'} onClick={() => setView('chat')}>💬 Chat</button>
          <button className={view === 'dashboard' ? 'view-btn active' : 'view-btn'} onClick={() => setView('dashboard')}>📊 Dashboard</button>
        </div>
      </div>

      {view === 'dashboard' && <Dashboard />}

      {view === 'chat' && (
        <div className="chat-container">
          <div className="agent-selector">
            {AGENTS.map(a => (
              <button
                key={a.id}
                className={a.id === agent.id ? 'agent-btn active' : 'agent-btn'}
                onClick={() => setAgent(a)}
              >
                {a.label}
              </button>
            ))}
          </div>

          <div className="chat-window">
            {messages.map((m, i) => (
              <div key={i} className={`message ${m.sender}`}>
                <pre>{m.text}</pre>
              </div>
            ))}
            {loading && <div className="message bot"><pre>Thinking...</pre></div>}
          </div>

          <div className="input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                agent.param === 'question' ? 'Ask a question...' :
                agent.param === 'country' ? 'Enter country (USA, UK, Germany, Singapore, UAE) or leave blank' :
                'Press send (no input needed for this agent)'
              }
            />
            <button onClick={sendMessage}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

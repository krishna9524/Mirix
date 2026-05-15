import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import FilePreviewer from './components/FilePreviewer'; 

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [previewFile, setPreviewFile] = useState(null); 

  useEffect(() => {
    try {
      const storedSessions = JSON.parse(localStorage.getItem('chatSessions')) || [];
      setSessions(storedSessions);
      if (storedSessions.length > 0 && !currentSessionId) {
        setCurrentSessionId(storedSessions[0].id); 
      }
    } catch (error) {
      console.error("Failed to load sessions:", error);
      setSessions([]);
    }
  }, []); 

  const saveSessions = (newSessions) => {
    setSessions(newSessions);
    localStorage.setItem('chatSessions', JSON.stringify(newSessions));
  };

  // --- THIS FUNCTION IS NOW FIXED ---
  const handleNewChat = () => {
    // 1. Search for an *existing* empty chat.
    let existingEmptySession = null;
    for (const session of sessions) {
      try {
        const storedMessages = JSON.parse(localStorage.getItem(`messages_${session.id}`)) || [];
        if (storedMessages.length === 0) {
          existingEmptySession = session;
          break; // Found one!
        }
      } catch (e) {
        console.error("Could not read message storage:", e);
      }
    }

    // 2. If we found an existing empty chat...
    if (existingEmptySession) {
      console.log(`Found existing empty chat: ${existingEmptySession.id}. Switching to it.`);
      // ...just switch to it.
      setCurrentSessionId(existingEmptySession.id);
    } else {
      // 3. If no empty chats exist, create a new one.
      console.log("No empty chats found. Creating a new one.");
      const newSession = {
        id: Date.now().toString(),
        title: `New Chat - ${new Date().toLocaleTimeString()}`,
      };
      const newSessions = [newSession, ...sessions];
      saveSessions(newSessions);
      setCurrentSessionId(newSession.id);
    }
  };
  // --- END OF FIX ---

  const handleSelectChat = (id) => {
    setCurrentSessionId(id);
  };

  const handleDeleteChat = (idToDelete) => {
    const newSessions = sessions.filter(s => s.id !== idToDelete);
    saveSessions(newSessions);
    localStorage.removeItem(`messages_${idToDelete}`);

    if (currentSessionId === idToDelete) {
      setCurrentSessionId(newSessions.length > 0 ? newSessions[0].id : null);
    }
  };

  const handleUpdateSessionTitle = (sessionId, newTitle) => {
    const newSessions = sessions.map(session => {
      if (session.id === sessionId) {
        return { ...session, title: newTitle };
      }
      return session;
    });
    saveSessions(newSessions);
  };

  const handlePreviewFile = (fileId, fileName) => {
    setPreviewFile({ id: fileId, name: fileName });
  };
  const handleClosePreview = () => {
    setPreviewFile(null);
  };

  return (
    <div className="app-container">
      <aside className="sidebar">
        <button className="new-chat-button" onClick={handleNewChat}>
          + New Chat
        </button>
        <div className="chat-history-list">
          {sessions.map((session) => (
            <div
              key={session.id} 
              className={`chat-session-item ${session.id === currentSessionId ? 'active' : ''}`}
              onClick={() => handleSelectChat(session.id)}
            >
              <span className="session-title">{session.title}</span>
              <span className="session-actions">
                <button onClick={(e) => { e.stopPropagation(); handleDeleteChat(session.id); }}>
                  🗑️
                </button>
              </span>
            </div>
          ))}
        </div>
      </aside>

      <main className="main-content">
        <div className="chat-window-container">
          {sessions.map(session => (
            <div 
              key={session.id}
              className="chat-window-wrapper"
              style={{ display: session.id === currentSessionId ? 'flex' : 'none' }}
            >
              <ChatWindow
                sessionId={session.id}
                sessionTitle={session.title}
                onPreviewFile={handlePreviewFile}
                onUpdateTitle={handleUpdateSessionTitle} 
              />
            </div>
          ))}
        </div>

        {!currentSessionId && (
          <div className="empty-chat">
            <span className="empty-chat-logo">M</span>
            <h2>Select a chat or start a new one.</h2>
          </div>
        )}
      </main>

      {previewFile && (
        <FilePreviewer
          fileId={previewFile.id}
          fileName={previewFile.name}
          onClose={handleClosePreview}
        />
      )}
    </div>
  );
}

export default App;
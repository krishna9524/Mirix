import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/v1';

const CodeBlock = ({ node, inline, className, children, ...props }) => {
  const match = /language-(\w+)/.exec(className || '');
  const [copied, setCopied] = useState(false);

  let codeText = '';
  if (Array.isArray(children)) {
    codeText = children[0] || ''; 
  } else if (typeof children === 'string') {
    codeText = children;
  } else if (children) {
    codeText = String(children);
  }

  const safeCode = codeText.replace(/\n$/, '');

  const handleCopy = () => {
    navigator.clipboard.writeText(safeCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return !inline && match ? (
    <div className="code-block-wrapper">
      <button className="copy-code-button" onClick={handleCopy}>
        {copied ? 'Copied!' : 'Copy'}
      </button>
      <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="pre" {...props}>
        {safeCode}
      </SyntaxHighlighter>
    </div>
  ) : (
    <code className={className} {...props}>
      {children}
    </code>
  );
};

const cleanMessage = (msg) => ({
  id: msg.id,
  sender: msg.sender,
  text: msg.text,
  fileId: msg.fileId || null,
  fileName: msg.fileName || null,
  type: msg.type || null,
});

function ChatWindow({ sessionId, sessionTitle, onUpdateTitle, onPreviewFile }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [editingId, setEditingId] = useState(null); 
  const [editText, setEditText] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
 
  const currentStreamController = useRef(null);

  const textareaRef = useRef(null);
  const MAX_TEXTAREA_HEIGHT = 200;

  useEffect(() => {
    if (!sessionId) return;
    try {
      const storedMessages = JSON.parse(localStorage.getItem(`messages_${sessionId}`)) || [];
      const cleanedMessages = storedMessages.map(cleanMessage);
      setMessages(cleanedMessages);
    } catch (error) {
      console.error("Failed to load messages:", error);
      setMessages([]);
    }
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; 
      const scrollHeight = textareaRef.current.scrollHeight;
      
      if (scrollHeight > MAX_TEXTAREA_HEIGHT) {
        textareaRef.current.style.height = `${MAX_TEXTAREA_HEIGHT}px`;
        textareaRef.current.style.overflowY = 'auto';
      } else {
        textareaRef.current.style.height = `${scrollHeight}px`;
        textareaRef.current.style.overflowY = 'hidden';
      }
    }
  }, [input]);

  const setMessagesState = (newMessages) => {
    setMessages(newMessages);
  };
  
  const saveMessagesToStorage = (messagesToSave) => {
    localStorage.setItem(`messages_${sessionId}`, JSON.stringify(messagesToSave));
  }

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error) {
      console.error("File upload failed:", error);
      throw new Error("File upload failed. " + (error.response?.data?.detail || error.message));
    }
  };

  const handleSend = async () => {
    if (isLoading) return; 
    if (!input.trim() && !selectedFile) return;

    setIsLoading(true);
    let userMessageText = input;
    let fileId = null;
    let fileName = null;
    let currentMessages = [...messages]; 

    try {
      if (selectedFile) {
        const fileMessageId = Date.now().toString();
        const fileMessage = cleanMessage({
          id: fileMessageId,
          sender: 'user',
          type: 'file',
          text: `Uploading ${selectedFile.name}...`,
          fileName: selectedFile.name,
        });
        currentMessages.push(fileMessage);
        setMessagesState(currentMessages); 
        saveMessagesToStorage(currentMessages); 
       
        const uploadResponse = await uploadFile(selectedFile);
        fileId = uploadResponse.file_id;
        fileName = uploadResponse.filename;

        const messageToUpdate = currentMessages.find(m => m.id === fileMessageId);
        if (messageToUpdate) {
          messageToUpdate.text = `Uploaded ${fileName}`;
          messageToUpdate.fileId = fileId; 
        }
        setMessagesState([...currentMessages]); 
        saveMessagesToStorage([...currentMessages]); 
        setSelectedFile(null);
      }
    } catch (error) {
      const errorMessage = cleanMessage({
        id: Date.now().toString(), sender: 'ai', text: error.message
      });
      saveMessagesToStorage([...currentMessages, errorMessage]); 
      setMessagesState([...currentMessages, errorMessage]); 
      setIsLoading(false);
      return;
    }

    if (!input.trim() && fileId) {
      userMessageText = `Uploaded ${fileName}. Please analyze it.`;
    }
   
    if (!userMessageText.trim()) {
        setIsLoading(false);
        return;
    }

    const userMessage = cleanMessage({
      id: (Date.now() + 1).toString(),
      sender: 'user',
      text: userMessageText,
      fileId: fileId,
      fileName: fileName,
    });
   
    const newMessages = [...currentMessages, userMessage]; 
    setMessagesState(newMessages); 
    saveMessagesToStorage(newMessages); 
    setInput('');

    let aiMessageId = null;
    let finalAiMessageText = ""; 
   
    try {
      const controller = new AbortController();
      currentStreamController.current = controller;
     
      const response = await fetch(`${API_URL}/chat-stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMessages }),
        signal: controller.signal
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      if (!response.body) throw new Error("Response body is empty.");
     
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
     
      let messagesWithNewBubble = [...newMessages]; 

      while (true) {
        const { done, value } = await reader.read();
       
        if (done) {
          if (aiMessageId) {
            setMessagesState(prevMessages => { 
              const finalMessages = prevMessages.map(msg => 
                msg.id === aiMessageId ? { ...msg, text: finalAiMessageText } : msg
              );
              saveMessagesToStorage(finalMessages); 
              return finalMessages; 
            });
          }
          break; 
        }

        buffer += decoder.decode(value, { stream: true });
       
        while (buffer.includes("\n\n")) {
          const eventEndIndex = buffer.indexOf("\n\n");
          const eventData = buffer.substring(0, eventEndIndex);
          buffer = buffer.substring(eventEndIndex + 2);

          if (eventData.startsWith("data: ")) {
            const data = eventData.substring(6);

            if (data === "[DONE]") {
              reader.cancel();
              continue;
            }
            if (data.startsWith("[ERROR]")) {
              throw new Error(data.replace("[ERROR] ", ""));
            }

            const parsedData = JSON.parse(data);

            // --- THE FIXES IMPLEMENTED HERE ---
            if (parsedData.type === 'error') {
              throw new Error(parsedData.content);
            } 
            else if (parsedData.type === 'token') {
              if (!aiMessageId) {
                aiMessageId = Date.now().toString();
                finalAiMessageText = parsedData.content;
                const aiMessage = cleanMessage({
                  id: aiMessageId, sender: 'ai', text: finalAiMessageText
                });
                messagesWithNewBubble = [...newMessages, aiMessage];
                setMessagesState(messagesWithNewBubble);
                saveMessagesToStorage(messagesWithNewBubble);
              } else {
                finalAiMessageText += parsedData.content;
                setMessagesState(prevMessages => 
                  prevMessages.map(msg => 
                    msg.id === aiMessageId ? { ...msg, text: finalAiMessageText } : msg
                  )
                );
              }
            } 
            else if (parsedData.type === 'tool_start') {
              const toolMessage = `\n\n*${parsedData.content}*\n\n`;
              if (!aiMessageId) {
                aiMessageId = Date.now().toString();
                finalAiMessageText = toolMessage;
                const aiMessage = cleanMessage({
                  id: aiMessageId, sender: 'ai', text: finalAiMessageText
                });
                messagesWithNewBubble = [...newMessages, aiMessage];
                setMessagesState(messagesWithNewBubble);
                saveMessagesToStorage(messagesWithNewBubble);
              } else {
                finalAiMessageText += toolMessage;
                setMessagesState(prevMessages => 
                  prevMessages.map(msg => 
                    msg.id === aiMessageId ? { ...msg, text: finalAiMessageText } : msg
                  )
                );
              }
            }
            // --- END OF FIXES ---
          }
        }
      }
     
      if (
        aiMessageId && 
        newMessages.length === 1 && 
        sessionTitle && sessionTitle.startsWith("New Chat")
      ) {
        console.log("Generating title for new chat...");
        const finalAiMsg = cleanMessage({
           id: aiMessageId, sender: 'ai', text: finalAiMessageText
        });
        window.mirixApi.generateTitle([userMessage, finalAiMsg])
          .then(titleResponse => {
            if (titleResponse.title) {
              onUpdateTitle(sessionId, titleResponse.title);
            }
          });
      }

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log("Stream stopped by user.");
      } else {
        console.error('Failed to send message:', error);
        const errorMessage = cleanMessage({
          id: Date.now().toString(), sender: 'ai', text: `⚠️ Error: ${error.message}`
        });
        saveMessagesToStorage([...newMessages, errorMessage]);
        setMessagesState([...newMessages, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      currentStreamController.current = null;
    }
  };

  const handleStopGeneration = () => {
    console.log("User clicked STOP");
    if (currentStreamController.current) {
      currentStreamController.current.abort(); 
      currentStreamController.current = null;
    }
    setIsLoading(false);
   
    const stopMessage = cleanMessage({
      id: Date.now().toString(),
      sender: 'system',
      text: 'Generation stopped by user.',
      type: 'system'
    });
    saveMessagesToStorage([...messages, stopMessage]);
    setMessagesState([...messages, stopMessage]);
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text).catch(err => {
      console.error('Failed to copy text: ', err);
    });
  };

  const handleStartEdit = (message) => {
    setEditingId(message.id);
    setEditText(message.text);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditText('');
  };

  const handleSaveAndResend = (messageIdToEdit) => {
    const messageIndex = messages.findIndex(msg => msg.id === messageIdToEdit);
    if (messageIndex === -1) return;
   
    const updatedUserMessage = {
      ...cleanMessage(messages[messageIndex]),
      text: editText,
      fileId: null,
      fileName: null
    };
   
    const forkedMessages = messages.slice(0, messageIndex + 1);
    forkedMessages[messageIndex] = updatedUserMessage;
   
    saveMessagesToStorage(forkedMessages); 
    setMessagesState(forkedMessages); 
    setEditingId(null);
    setEditText('');
    resendToApi(forkedMessages); 
  };

  const resendToApi = async (history) => {
    if (isLoading) return;
    setIsLoading(true);

    const controller = new AbortController();
    currentStreamController.current = controller;
   
    let aiMessageId = null;
    let finalAiMessageText = "";

    try {
      const response = await fetch(`${API_URL}/chat-stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
        signal: controller.signal
      });
     
      if (!response.body) throw new Error("Response body is empty.");
     
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
     
      let messagesWithNewBubble = [...history];

      while (true) {
        const { done, value } = await reader.read();
       
        if (done) {
          if (aiMessageId) {
            setMessagesState(prevMessages => {
              const finalMessages = prevMessages.map(msg => 
                msg.id === aiMessageId ? { ...msg, text: finalAiMessageText } : msg
              );
              saveMessagesToStorage(finalMessages);
              return finalMessages;
            });
          }
          break;
        }
       
        buffer += decoder.decode(value, { stream: true });

        while (buffer.includes("\n\n")) {
          const eventEndIndex = buffer.indexOf("\n\n");
          const eventData = buffer.substring(0, eventEndIndex);
          buffer = buffer.substring(eventEndIndex + 2);

          if (eventData.startsWith("data: ")) {
            const data = eventData.substring(6);
            if (data === "[DONE]") {
              reader.cancel();
              continue;
            }
            if (data.startsWith("[ERROR]")) {
              throw new Error(data.replace("[ERROR] ", ""));
            }

            const parsedData = JSON.parse(data);
            
            // --- FIXES IMPLEMENTED HERE FOR RESEND ---
            if (parsedData.type === 'error') {
              throw new Error(parsedData.content);
            } 
            else if (parsedData.type === 'token') {
              if (!aiMessageId) {
                aiMessageId = Date.now().toString();
                finalAiMessageText = parsedData.content;
                const aiMessage = cleanMessage({
                  id: aiMessageId, sender: 'ai', text: finalAiMessageText
                });
                messagesWithNewBubble = [...history, aiMessage];
                setMessagesState(messagesWithNewBubble);
                saveMessagesToStorage(messagesWithNewBubble);
              } else {
                finalAiMessageText += parsedData.content;
                setMessagesState(prevMessages => 
                  prevMessages.map(msg => 
                    msg.id === aiMessageId ? { ...msg, text: finalAiMessageText } : msg
                  )
                );
              }
            }
            else if (parsedData.type === 'tool_start') {
              const toolMessage = `\n\n*${parsedData.content}*\n\n`;
              if (!aiMessageId) {
                aiMessageId = Date.now().toString();
                finalAiMessageText = toolMessage;
                const aiMessage = cleanMessage({
                  id: aiMessageId, sender: 'ai', text: finalAiMessageText
                });
                messagesWithNewBubble = [...history, aiMessage];
                setMessagesState(messagesWithNewBubble);
                saveMessagesToStorage(messagesWithNewBubble);
              } else {
                finalAiMessageText += toolMessage;
                setMessagesState(prevMessages => 
                  prevMessages.map(msg => 
                    msg.id === aiMessageId ? { ...msg, text: finalAiMessageText } : msg
                  )
                );
              }
            }
            // --- END OF FIXES ---
          }
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log("Resend stream stopped by user.");
      } else {
        console.error('Failed to resend message:', error);
        const errorMessage = cleanMessage({
          id: Date.now().toString(), sender: 'ai', text: `⚠️ Error: ${error.message}`
        });
        saveMessagesToStorage([...history, errorMessage]);
        setMessagesState([...history, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      currentStreamController.current = null;
    }
  };
 
  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
    event.target.value = null;
  };

  const handleClearFile = () => {
    setSelectedFile(null);
  };

  const renderMessageContent = (msg) => {
    if (msg.type === 'file') {
      if (msg.fileId) {
        return (
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault(); 
              onPreviewFile(msg.fileId, msg.fileName); 
            }}
            title={`Click to preview ${msg.fileName}`}
            className="file-link"
          >
            📁 {msg.text}
          </a>
        );
      }
      return `📁 ${msg.text}`;
    }

    if (msg.sender === 'system') {
      return <em>{msg.text}</em>;
    }

    if (msg.sender === 'ai') {
      return (
        <div className="markdown-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{ code: CodeBlock }}
          >
            {msg.text}
          </ReactMarkdown>
        </div>
      );
    } 
   
    return <>{msg.text}</>;
  };

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
            {editingId === msg.id ? (
              <div className="edit-area">
                <textarea
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  autoFocus 
                  onFocus={(e) => e.currentTarget.select()} 
                />
                <div className="edit-actions">
                  <button className="cancel-btn" onClick={handleCancelEdit}>Cancel</button>
                  <button className="save-btn" onClick={() => handleSaveAndResend(msg.id)}>
                    Save & Resend
                  </button>
                </div>
              </div>
            ) : (
              <div className={`message ${msg.sender} ${msg.type === 'file' ? 'file-message' : ''} ${msg.sender === 'system' ? 'system' : ''}`}>
                {renderMessageContent(msg)}
                <div className="message-actions">
                  {msg.sender === 'user' && msg.type !== 'file' && ( 
                    <button title="Edit" onClick={() => handleStartEdit(msg)}>✏️</button>
                  )}
                  {msg.sender === 'ai' && (
                    <button title="Copy" onClick={() => handleCopy(msg.text)}>📋</button>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        {selectedFile && (
          <div className="file-preview">
            <span>{selectedFile.name}</span>
            <button onClick={handleClearFile}>&times;</button>
          </div>
        )}
        <div className="chat-input">
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            style={{ display: 'none' }} 
          />
          <button className="upload-btn" title="Upload file" onClick={handleUploadClick} disabled={isLoading}>
            📎
          </button>
          
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault(); 
                if (!isLoading) handleSend();
              }
            }}
            placeholder="Type your message..."
            disabled={isLoading}
          />
         
          {isLoading ? (
            <button onClick={handleStopGeneration} className="stop-btn">
              ■ Stop
            </button>
          ) : (
            <button onClick={handleSend} disabled={!input.trim() && !selectedFile}>
              Send
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;
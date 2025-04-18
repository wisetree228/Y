import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';

const Chat = () => {
    const { userId } = useParams();
    const [messages, setMessages] = useState([]);
    const [recipient, setRecipient] = useState(null);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchChatData = async () => {
            try {
                await CheckAuthorization();
                const response = await axios.get(`${API_BASE_URL}/chat/${userId}`, {
                    withCredentials: true
                });
                setMessages(response.data.messages);
                setRecipient({
                    id: response.data.recipient_id,
                    username: response.data.recipient_username
                });
                setLoading(false);
            } catch (err) {
                setError(err.response?.data?.detail || 'Ошибка при загрузке чата');
                setLoading(false);
            }
        };

        fetchChatData();
    }, [userId]);

    const handleSendMessage = (e) => {
        e.preventDefault();
        console.log('Отправка сообщения:', newMessage);
        setNewMessage('');
    };

    // Функция для форматирования даты и времени
    const formatDateTime = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) return <div className="chat-loading">Загрузка чата...</div>;
    if (error) return <div className="chat-error">Ошибка: {error}</div>;

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h2>Чат с {recipient?.username}</h2>
            </div>
            
            <div className="messages-list">
                {messages.length === 0 ? (
                    <div className="no-messages">Нет сообщений</div>
                ) : (
                    messages.map((message) => (
                        <div 
                            key={message.id} 
                            className={`message ${message.author_id === recipient.id ? 'received' : 'sent'}`}
                        >
                            <div className="message-content">
                                <p>{message.text}</p>
                                <span className="message-time">
                                    {formatDateTime(message.created_at)}
                                </span>
                            </div>
                        </div>
                    ))
                )}
            </div>
            
            <form onSubmit={handleSendMessage} className="message-form">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Введите сообщение..."
                    className="message-input"
                />
                <button type="submit" className="send-button">
                    Отправить
                </button>
            </form>
        </div>
    );
};

// Стили остаются без изменений
const styles = `
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        max-width: 800px;
        margin: 0 auto;
        border: 1px solid #ccc;
        background-color: #f9f9f9;
    }
    
    .chat-header {
        padding: 15px;
        background-color: #4CAF50;
        color: white;
        text-align: center;
    }
    
    .messages-list {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
    }
    
    .message {
        margin-bottom: 15px;
        display: flex;
    }
    
    .message.sent {
        justify-content: flex-end;
    }
    
    .message.received {
        justify-content: flex-start;
    }
    
    .message-content {
        max-width: 70%;
        padding: 10px 15px;
        border-radius: 18px;
        position: relative;
    }
    
    .message.sent .message-content {
        background-color: #DCF8C6;
    }
    
    .message.received .message-content {
        background-color: #ECECEC;
    }
    
    .message-time {
        font-size: 0.8em;
        color: #666;
        display: block;
        text-align: right;
        margin-top: 5px;
    }
    
    .message-form {
        display: flex;
        padding: 10px;
        border-top: 1px solid #ccc;
        background-color: white;
    }
    
    .message-input {
        flex: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 20px;
        outline: none;
    }
    
    .send-button {
        margin-left: 10px;
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 20px;
        cursor: pointer;
    }
    
    .send-button:hover {
        background-color: #45a049;
    }
    
    .chat-loading, .chat-error, .no-messages {
        text-align: center;
        padding: 20px;
    }
    
    .chat-error {
        color: red;
    }
`;

// Добавляем стили в документ
const styleElement = document.createElement('style');
styleElement.innerHTML = styles;
document.head.appendChild(styleElement);

export default Chat;
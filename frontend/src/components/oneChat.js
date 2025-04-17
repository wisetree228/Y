import React, { useEffect, useState, useRef } from 'react';
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
    const [currentUserId, setCurrentUserId] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const socketRef = useRef(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        let isMounted = true;
        const wsUrl = API_BASE_URL.replace(/^http/, 'ws') + `/chatsocket/`;

        const initializeChat = async () => {
            try {
                await CheckAuthorization();

                const userResponse = await axios.get(`${API_BASE_URL}/my_id`, {
                    withCredentials: true
                });
                const myId = userResponse.data.id;
                if (!isMounted) return;
                setCurrentUserId(myId);

                const chatResponse = await axios.get(`${API_BASE_URL}/chat/${userId}`, {
                    withCredentials: true
                });
                if (!isMounted) return;
                setMessages(chatResponse.data.messages || []);
                setRecipient({
                    id: chatResponse.data.recipient_id,
                    username: chatResponse.data.recipient_username
                });

                socketRef.current = new WebSocket(`${wsUrl}${myId}`);

                socketRef.current.onopen = () => {
                    console.log('WebSocket connected');
                    if (!isMounted) return;
                    setIsConnected(true);
                    setLoading(false);
                };

                socketRef.current.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        alert(message)
                        
                        // Проверяем, что сообщение имеет нужный формат
                        if (message.author_id && message.text) {
                            setMessages(prev => [...prev, {
                                id: Date.now(), // Можем использовать Date.now() как временный ID
                                author_id: message.author_id,
                                text: message.text,
                                created_at: message.created_at
                            }]);
                        }
                    } catch (err) {
                        console.error('Error parsing message:', err);
                    }
                };

                socketRef.current.onclose = () => {
                    console.log('WebSocket disconnected');
                    if (!isMounted) return;
                    setIsConnected(false);
                };

                socketRef.current.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    if (!isMounted) return;
                    setError('Connection error');
                    setIsConnected(false);
                    setLoading(false);
                };

            } catch (err) {
                console.error('Initialization error:', err);
                if (!isMounted) return;
                setError(err.response?.data?.detail || 'Chat loading error');
                setLoading(false);
            }
        };

        initializeChat();

        return () => {
            isMounted = false;
            if (socketRef.current) {
                socketRef.current.close();
            }
        };
    }, [userId]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim() || !isConnected) return;

        const messageData = {
            recipient_id: parseInt(userId),
            message: newMessage
        };

        const tempMessage = {
            id: Date.now(),
            author_id: currentUserId,
            text: newMessage,
            created_at: new Date().toISOString(),
            isOptimistic: true
        };

        setMessages(prev => [...prev, tempMessage]);
        setNewMessage('');

        try {
            socketRef.current.send(JSON.stringify(messageData));
        } catch (err) {
            console.error('Send message error:', err);
            setError('Send message error');
            setMessages(prev => prev.filter(msg => msg.id !== tempMessage.id));
        }
    };

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
                <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
                    {isConnected ? 'Онлайн' : 'Оффлайн'}
                </div>
            </div>
            
            <div className="messages-list">
                {messages.length === 0 ? (
                    <div className="no-messages">Нет сообщений</div>
                ) : (
                    messages.map((message) => (
                        <div 
                            key={message.id} 
                            className={`message ${message.author_id === currentUserId ? 'sent' : 'received'}`}
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
                <div ref={messagesEndRef} />
            </div>
            
            <form onSubmit={handleSendMessage} className="message-form">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Введите сообщение..."
                    className="message-input"
                    disabled={!isConnected}
                />
                <button 
                    type="submit" 
                    className="send-button"
                    disabled={!isConnected || !newMessage.trim()}
                >
                    Отправить
                </button>
            </form>
        </div>
    );
};

export default Chat;
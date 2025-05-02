import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { Link } from 'react-router-dom';
import './css/Register.css';

const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [surname, setSurname] = useState('');
    const [confirmation, setConfirmation] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!username || !email || !password || !name || !surname || !confirmation) {
            setError('Пожалуйста, заполните все поля');
            return;
        }

        if (password !== confirmation) {
            setError('Пароли не совпадают');
            return;
        }

        try {
            const response = await axios.post(`${API_BASE_URL}/register`, {
                username,
                email,
                password,
                name,
                surname,
            });
            alert('Успешная регистрация! Теперь войдите в свой аккаунт!')
            navigate('/login');
        } catch (err) {
            if (err.response && err.response.data) {
                setError(err.response.data.detail || 'Ошибка регистрации');
            } else {
                setError('Произошла ошибка. Попробуйте еще раз');
            }
        }
    };

    return (
        <div className="register-page">
            <div className="background-shapes">
                <div className="shape shape-1"></div>
                <div className="shape shape-2"></div>
                <div className="shape shape-3"></div>
            </div>
            
            <main className="register-main">
                <div className="auth-container">
                    <div className="logo-container">
                        <h1 className="logo">Y</h1>
                        <div className="logo-pulse"></div>
                    </div>
                    
                    <div className="auth-card glass-effect">
                        <h2 className="auth-title">Создать аккаунт</h2>
                        {error && <div className="error-message">{error}</div>}
                        
                        <form onSubmit={handleSubmit} className="auth-form">
                            <div className="form-grid">
                                <div className="input-group">
                                    <input
                                        type="text"
                                        placeholder="Имя пользователя"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        className="auth-input"
                                        required
                                    />
                                    <span className="input-icon">👤</span>
                                </div>
                                
                                <div className="input-group">
                                    <input
                                        type="email"
                                        placeholder="Email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="auth-input"
                                        required
                                    />
                                    <span className="input-icon">✉️</span>
                                </div>
                                
                                <div className="input-group">
                                    <input
                                        type="password"
                                        placeholder="Пароль"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="auth-input"
                                        required
                                    />
                                    <span className="input-icon">🔒</span>
                                </div>
                                
                                <div className="input-group">
                                    <input
                                        type="password"
                                        placeholder="Подтвердите пароль"
                                        value={confirmation}
                                        onChange={(e) => setConfirmation(e.target.value)}
                                        className="auth-input"
                                        required
                                    />
                                    <span className="input-icon">🔏</span>
                                </div>
                                
                                <div className="input-group">
                                    <input
                                        type="text"
                                        placeholder="Имя"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        className="auth-input"
                                        required
                                    />
                                    <span className="input-icon">🆔</span>
                                </div>
                                
                                <div className="input-group">
                                    <input
                                        type="text"
                                        placeholder="Фамилия"
                                        value={surname}
                                        onChange={(e) => setSurname(e.target.value)}
                                        className="auth-input"
                                        required
                                    />
                                    <span className="input-icon">👪</span>
                                </div>
                            </div>
                            
                            <button type="submit" className="auth-button">
                                Зарегистрироваться
                            </button>
                        </form>
                        
                        <p className="auth-switch">
                            Уже есть аккаунт? <Link to="/login" className="auth-link">Войти</Link>
                        </p>
                    </div>
                </div>
            </main>
            
            <footer className="register-footer">
                <div className="footer-content">
                    <p>© 2025 Y. Все права защищены</p>
                    <div className="tech-lights"></div>
                </div>
            </footer>
        </div>
    );
};

export default Register;
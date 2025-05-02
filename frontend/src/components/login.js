import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import './css/Login.css';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true); 
            const response = await axios.post(API_BASE_URL + '/login', {
                email,
                password,
            }, { withCredentials: true });

            if (response.status === 200) {
                navigate('/posts'); 
            } else {
                setError("При входе произошла ошибка! Проверьте корректность email и пароля.");
            }
        } catch (err) {
            setError('Ошибка! Проверьте корректность введённых данных и попробуйте ещё раз!');
            console.error('Ошибка:', err); 
            
            
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="background-shapes">
                <div className="shape shape-1"></div>
                <div className="shape shape-2"></div>
                <div className="shape shape-3"></div>
            </div>
    
            <main className="login-main">
                <div className="auth-container">
                    <div className="logo-container">
                        <h1 className="logo">Y</h1>
                        <div className="logo-pulse"></div>
                    </div>
                    <div className="auth-card glass-effect">
                        <h2 className="auth-title">Вход в систему</h2>
                        <form onSubmit={handleSubmit} className="auth-form">
                            <div className="input-group">
                                <input
                                    type="text"
                                    placeholder="Email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="auth-input"
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
                                />
                                <span className="input-icon">🔒</span>
                            </div>
                            <button type="submit" className="auth-button" disabled={loading}>
                                {loading ? 'Загрузка...' : 'Войти'}
                            </button>
                        </form>
                        {error && <p className="error-message">{error}</p>}
                        <p className="auth-switch">
                            Нет аккаунта? <Link to="/register" className="auth-link">Зарегистрироваться</Link>
                        </p>
                    </div>
                </div>
            </main>
    
            <footer className="login-footer">
                <div className="footer-content">
                    <p>© 2025 Y. Все права защищены</p>
                    <div className="tech-lights"></div>
                </div>
            </footer>
        </div>
    );
};

export default Login;

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('Отправка данных:', { email, password });
        try {
            setLoading(true); 
            const response = await axios.post(API_BASE_URL + '/login', {
                email,
                password,
            }, { withCredentials: true });
    
            if (response.status === 200) {
                
    
                navigate('/posts'); 
                setLoading(false); 
            } else {
                
                setError("При входе произошла ошибка! Проверьте корректность email и пароля.");
                 setLoading(false); 
                console.error('Ошибка:', response.status, response.data); 
            }
        } catch (err) {
            alert('Ошибка! Проверьте корректность введённых данных и попробуйте ещё раз!')
            setLoading(false); 
            console.error('Ошибка:', err); 
        }
    };

    return (
        <div className="container">
            <div className="background-shapes">
                <div className="shape shape-1"></div>
                <div className="shape shape-2"></div>
                <div className="shape shape-3"></div>
            </div>
    
            <main>
                <div className="auth-container">
                    <h1 className="logo">Y</h1>
                    <div className="auth-card">
                        <h2 className="auth-title">Вход</h2>
                        <form onSubmit={handleSubmit}>
                            <input
                                type="text"
                                placeholder="Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                            <input
                                type="password"
                                placeholder="Пароль"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                            <button type="submit">Войти</button>
                        </form>
                        {error && <p className="error-message">{error}</p>}
                        <p className="auth-switch">
                            Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
                        </p>
                    </div>
                </div>
            </main>
    
            <footer>
                <div className="footer-content">
                    <p>© 2025 Y. Все права защищены</p>
                </div>
            </footer>
        </div>
    );
};

export default Login;

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const styleElement = document.createElement('style');
        styleElement.innerHTML = `
      .container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: #396687;
    color: white;
    position: relative;
    overflow: hidden;
}

.background-shapes {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.shape {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
}

.shape-1 {
    width: 200px;
    height: 200px;
    background: #3c91cf;
    top: -50px;
    left: -50px;
}

.shape-2 {
    width: 300px;
    height: 300px;
    background: #3c91cf;
    bottom: -100px;
    right: -100px;
}

.shape-3 {
    width: 150px;
    height: 150px;
    background: #3c91cf;
    top: 50%;
    right: 20%;
}

.auth-container {
    width: 100%;
    max-width: 400px;
    padding: 20px;
    z-index: 1;
}

.logo {
    text-align: center;
    font-size: 3rem;
    margin-bottom: 20px;
}

.auth-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.auth-title {
    text-align: center;
    margin-bottom: 25px;
    font-size: 1.8rem;
}

form {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

input {
    padding: 12px 15px;
    border: none;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    font-size: 1rem;
}

input::placeholder {
    color: rgba(255, 255, 255, 0.7);
}

button {
    padding: 12px;
    border: none;
    border-radius: 8px;
    background: #3c91cf;
    color: white;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.3s;
}

button:hover {
    background: #2a7bb9;
}

.error-message {
    color: #ff6b6b;
    text-align: center;
    margin-top: 15px;
}

.auth-switch {
    text-align: center;
    margin-top: 20px;
}

.auth-switch a {
    color: #3c91cf;
    text-decoration: none;
}

.auth-switch a:hover {
    text-decoration: underline;
}

footer {
    margin-top: 30px;
    text-align: center;
    opacity: 0.7;
    font-size: 0.9rem;
    z-index: 1;
}
    `;

        // Добавляем в head документа
        document.head.appendChild(styleElement);
        return () => {
            document.head.removeChild(styleElement);
        };
    }, []);


    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('Отправка данных:', { email, password });
        try {
            setLoading(true);
            const response = await axios.post(API_BASE_URL + '/login', {
                email,
                password,
            }, { withCredentials: true });

            navigate('/posts')
        } catch (err) {
            setLoading(true);
            try {
                const response = await axios.get(API_BASE_URL + '/my_id', { withCredentials: true });
                navigate('/posts')
            } catch (err) {
                alert('Ошибка! Проверьте корректность введённых данных и попробуйте ещё раз!')
            }

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

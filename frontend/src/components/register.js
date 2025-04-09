import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { Link } from 'react-router-dom';

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
        if (password !== confirmation) {
            setError('Пароли не совпадают');
            return;
        }
        try {
            const response = await axios.post(API_BASE_URL + '/register', {
                username,
                email,
                password, 
                name, 
                surname
            }, { 
                withCredentials: true 
            });
            
            console.log('Ответ от сервера:', response.data);
            
            if (response.status === 200) {
                console.log('Регистрация успешна:', response.data);
                navigate('/posts');
            } else {
                setError(response.data.message || 'Ошибка при регистрации'); 
            }
        } catch (err) {
            console.error('Ошибка при регистрации:', err);
            if (err.response) {
                setError(err.response.data.detail || 'Произошла ошибка при регистрации');
            } else {
                setError('Произошла ошибка при регистрации');
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
                        <h2 className="auth-title">Регистрация</h2>
                        {error && <p className="error-message">{error}</p>}
                        <form onSubmit={handleSubmit}>
                            <input
                                type="email"
                                placeholder="Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                            <input
                                type="text"
                                placeholder="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                            <input
                                type="password"
                                placeholder="Пароль"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <input
                                type="password"
                                placeholder="Подтверждение пароля"
                                value={confirmation}
                                onChange={(e) => setConfirmation(e.target.value)}
                                required
                            />
                            <input
                                type="text"
                                placeholder="Имя"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                            <input
                                type="text"
                                placeholder="Фамилия"
                                value={surname}
                                onChange={(e) => setSurname(e.target.value)}
                                required
                            />
                            <button type="submit">Зарегистрироваться</button>
                        </form>
                        <p className="auth-switch">
                            Уже есть аккаунт? <Link to="/login">Войти</Link>
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

export default Register;
import React, { useState, useEffect } from 'react';
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

    useEffect(() => {
        const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      div {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: #396687;
    color: white;
    padding: 20px;
    position: relative;
    overflow: hidden;
}

h2 {
    font-size: 1.8rem;
    margin-bottom: 25px;
    text-align: center;
}

form {
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 15px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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
    margin-top: 10px;
}

button:hover {
    background: #2a7bb9;
}

.error {
    color: #ff6b6b;
    text-align: center;
    margin-bottom: 15px;
}

p {
    margin-top: 20px;
    text-align: center;
}

a {
    color: #3c91cf;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
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

        // Простая проверка на наличие всех необходимых полей
        if (!username || !email || !password || !name || !surname || !confirmation) {
            setError('Пожалуйста, заполните все поля');
            return;
        }

        // Проверка соответствия паролей
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
            // Перенаправление на страницу после успешной регистрации
            alert('Успешная регистрация! Теперь войдите в свой аккаунт!')
            navigate('/login');
        } catch (err) {
            // Обработка ошибок от сервера
            if (err.response && err.response.data) {
                setError(err.response.data.detail || 'Ошибка регистрации');
            } else {
                setError('Произошла ошибка. Попробуйте еще раз');
            }
        }
    };

    return (
        <div>
            <h2>Регистрация</h2>
            <form onSubmit={handleSubmit}>
                {error && <div className="error">{error}</div>}
                <input
                    type="text"
                    placeholder="Имя пользователя"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
                    placeholder="Подтвердите пароль"
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
            <p>
                Уже есть аккаунт? <Link to="/login">Войти</Link>
            </p>
        </div>
    );
};

export default Register;
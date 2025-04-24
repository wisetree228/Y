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
                setError(err.response.data.message || 'Ошибка регистрации');
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
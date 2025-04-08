import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [Confirmation, confirmPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== Confirmation) {
          setError('Пароли не совпадают');
          return;
        }
        try {
          const response = await axios.post('https://jsonplaceholder.typicode.com/posts', {
            title: "Register",
            body: JSON.stringify({ username, password }),
          });
          if (response.status !== 201) {
            throw new Error('Ошибка при регистрации');
          }
          console.log('Ответ от сервера:', response.data);
        if (response.status === 201) {
          console.log('Регистрация успешна (тестовый ответ):', response.data);
          navigate('/posts');
          } else {
            setError(response.message || 'Ошибка при регистрации'); 
          }
        } catch (err) {
          console.error('Ошибка при регистрации:', err);
          setError('Произошла ошибка при регистрации');
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
                    <form onSubmit={handleSubmit}>
                        <input
                          type="text"
                          placeholder="Логин"
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
                          value={Confirmation}
                          onChange={(e) => confirmPassword(e.target.value)}
                          required
                        />
                        <button type="submit">Зарегистрироваться</button>
                      </form>
                      <p className="auth-switch">
                              Уже есть аккаунт? <Link to="/login">
                        Войти
                          </Link>
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
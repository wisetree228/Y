import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Link } from 'react-router-dom';



const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();


  
    const handleSubmit = async (e) => {
      e.preventDefault();
      console.log('Отправка данных:', { username, password });
      try {
        const response = await axios.post('https://jsonplaceholder.typicode.com/posts', {
          title: "Login",
          body: JSON.stringify({ username, password }),
        });
        if (response.status !== 'ok') {
          throw new Error('Ошибка при регистрации');
        }
        console.log('Ответ от сервера:', response.data);
      if (response.status === 'ok') {
        console.log('Авторизация успешна (тестовый ответ):', response.data);
        navigate('/posts');
        } else {
          setError(response.message || 'Ошибка при регистрации'); 
        }
      } catch (err) {
        console.error('Ошибка при авторизации:', err);
        setError('Произошла ошибка при авторизации');
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
                                placeholder="Логин"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                              />
                              <input
                                type="password"
                                placeholder="Пароль"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                              />
                              <button type="submit">Войти</button>
                            </form>
                          <p className="auth-switch">
                              Нет аккаунта? <Link to="/register">
                        Зарегистрироваться
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
  
  export default Login;
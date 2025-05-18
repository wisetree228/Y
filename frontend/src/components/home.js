import React, { useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { Link, useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const idResponse = await axios.get(`${API_BASE_URL}/my_id`, {
          withCredentials: true
        });
        if (idResponse.data.id) {
          navigate('/posts');
        }
      } catch (error) {
        // Всё в порядке, пользователь не авторизован
      }
    };
    fetchData();
    const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      /* Base styles */
:root {
    --primary-color: #3c91cf;
    --primary-dark: #2d7cb6;
    --secondary-color: #ffffff;
    --bg-color: #396687;
    --text-color: #ffffff;
    --blur-color-1: rgba(60, 145, 207, 0.3);
    --blur-color-2: rgba(57, 102, 135, 0.4);
  }
  
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  
  body {
    background-color: var(--bg-color);
  }
  
  /* Container styles */
  .pp-container {
    position: relative;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-color);
    overflow: hidden;
  }
  
  .pp-content {
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 400px;
    padding: 2rem;
    text-align: center;
  }
  
  /* Background elements */
  .pp-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
  }
  
  .pp-blur-circle {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
  }
  
  .pp-blur-circle--1 {
    width: 400px;
    height: 400px;
    background-color: var(--blur-color-1);
    top: -150px;
    left: -150px;
  }
  
  .pp-blur-circle--2 {
    width: 500px;
    height: 500px;
    background-color: var(--blur-color-2);
    bottom: -200px;
    right: -200px;
  }
  
  /* Header styles */
  .pp-header {
    margin-bottom: 3rem;
  }
  
  .pp-logo {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--secondary-color);
    margin-bottom: 0.8rem;
    letter-spacing: 1px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  
  .pp-logo-underline {
    width: 100px;
    height: 4px;
    background: var(--secondary-color);
    margin: 0 auto;
    border-radius: 2px;
    opacity: 0.8;
  }
  
  /* Button styles */
  .pp-buttons {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    margin-top: 2rem;
  }
  
  .pp-button {
    display: block;
    padding: 0.9rem 1.8rem;
    border-radius: 30px;
    font-size: 1.1rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  .pp-button--primary {
    background-color: var(--primary-color);
    color: var(--secondary-color);
  }
  
  .pp-button--primary:hover {
    background-color: var(--primary-dark);
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
  }
  
  .pp-button--secondary {
    background-color: transparent;
    color: var(--secondary-color);
    border: 2px solid var(--secondary-color);
  }
  
  .pp-button--secondary:hover {
    background-color: rgba(255, 255, 255, 0.1);
    transform: translateY(-3px);
  }
  
  /* Footer styles */
  .pp-footer {
    position: absolute;
    bottom: 1.5rem;
    width: 100%;
    text-align: center;
    z-index: 2;
  }
  
  .pp-copyright {
    color: var(--secondary-color);
    font-size: 0.9rem;
    opacity: 0.8;
  }
  
  /* Responsive adjustments */
  @media (max-width: 480px) {
    .pp-content {
      padding: 1.5rem;
    }
    
    .pp-logo {
      font-size: 2rem;
    }
    
    .pp-button {
      padding: 0.8rem 1.5rem;
      font-size: 1rem;
    }
  }
    `;

    // Добавляем в head документа
    document.head.appendChild(styleElement);
    return () => {
      document.head.removeChild(styleElement);
    };
  }, []);

  return (
    <div className="pp-container">
      <div className="pp-background">
        <div className="pp-blur-circle pp-blur-circle--1"></div>
        <div className="pp-blur-circle pp-blur-circle--2"></div>
      </div>

      <div className="pp-content">
        <header className="pp-header">
          <h1 className="pp-logo">Y</h1>
          <div className="pp-logo-underline"></div>
        </header>

        <main className="pp-main">
          <div className="pp-buttons">
            <Link to="/login" className="pp-button pp-button--primary">
              Войти
            </Link>
            <Link to="/register" className="pp-button pp-button--secondary">
              Зарегистрироваться
            </Link>
          </div>
        </main>
      </div>

      <footer className="pp-footer">
        <p className="pp-copyright">© 2025 Y. Все права защищены</p>
      </footer>
    </div>
  );
};

export default Home;
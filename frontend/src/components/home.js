import React, { useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { Link, useNavigate } from 'react-router-dom';
import './css/main_page.css';

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
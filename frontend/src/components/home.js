import React, { useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { Link, useNavigate } from 'react-router-dom';

const Home = () => {
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {

            try {
                // Если это своя страница редиректим на свой профиль
                const idResponse = await axios.get(`${API_BASE_URL}/my_id`, {
                    withCredentials: true
                });
                if (idResponse.data.id){
                    navigate('/posts')
                }
                
            } catch (error) {
                // всё ок
            }

        };

        fetchData();
    }, []);



  return (
        <div className="container">
            <div className="background-shapes">
                <div className="shape shape-1"></div>
                <div className="shape shape-2"></div>
                <div className="shape shape-3"></div>
            </div>
            
            <header>
                <h1 className="title">Y</h1>
                <div className="title-underline"></div>
            </header>
            
            <main>
                <div className="buttons">
                    <Link to="/login">
                        <button>Войти</button>
                      </Link>
                      <Link to="/register">
                        <button>Зарегистрироваться</button>
                      </Link>
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

export default Home;
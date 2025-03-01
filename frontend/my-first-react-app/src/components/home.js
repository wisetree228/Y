import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
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
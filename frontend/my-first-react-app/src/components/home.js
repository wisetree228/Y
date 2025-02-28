import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div>
      <h1>Добро пожаловать!</h1>
      <Link to="/login">
        <button>Войти</button>
      </Link>
      <Link to="/register">
        <button>Зарегистрироваться</button>
      </Link>
    </div>
  );
};

export default Home;
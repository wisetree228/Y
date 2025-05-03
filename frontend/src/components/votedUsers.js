import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';

const VotedUsers = () => {
  const { votingVariantId } = useParams();
  const navigate = useNavigate();
  const [votedUsers, setVotedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [noVotesMessage, setNoVotesMessage] = useState(null);


  useEffect(() => {
    CheckAuthorization();
    fetchVotedUsers();
    const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      /* Основные стили */
body {
  background-color: #396687;
  color: #e0e0e0;
  font-family: Arial, sans-serif;
  padding: 20px;
}

/* Контейнер */
div[style*="max-width: '800px'"] {
  background-color: #2d4d66;
  border: 1px solid #3c91cf;
  border-radius: 8px;
  padding: 20px;
  margin: 20px auto;
  color: #fff;
}

/* Заголовок */
h1 {
  color: #fff;
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

/* Сообщение о пустом списке */
p[style*="color: 'gray'"] {
  color: #aaa !important;
  text-align: center;
  margin: 20px 0;
}

/* Список пользователей */
ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* Элементы списка */
li {
  margin-bottom: 10px;
}

/* Ссылки на пользователей */
a {
  display: block;
  padding: 12px;
  background-color: rgba(60, 145, 207, 0.2);
  border: 1px solid #3c91cf;
  border-radius: 6px;
  color: #fff;
  text-decoration: none;
  transition: background-color 0.2s;
}

a:hover {
  background-color: rgba(60, 145, 207, 0.4);
}

/* Индикатор загрузки */
div[style*="textAlign: 'center'"] {
  background-color: #2d4d66;
  border: 1px solid #3c91cf;
  border-radius: 8px;
  padding: 20px;
  margin: 50px auto;
  max-width: 300px;
}

div[style*="textAlign: 'center'"] p {
  color: #aaa;
}

/* Сообщение об ошибке */
p[style*="color: 'red'"] {
  color: #ff6b6b !important;
  background-color: #2d4d66;
  padding: 15px;
  border-radius: 6px;
  text-align: center;
  border: 1px solid #e53935;
  max-width: 500px;
  margin: 20px auto;
}
    `;
    
    // Добавляем в head документа
    document.head.appendChild(styleElement);
    return () => {
        document.head.removeChild(styleElement);
      };
  }, [votingVariantId]);


  const fetchVotedUsers = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/voted_users/${votingVariantId}?t=${Date.now()}`,
        { withCredentials: true }
      );

      if (response.data.users.length === 0) {
        setNoVotesMessage("За этот вариант никто не проголосовал.");
      } else {
        setVotedUsers(response.data.users);
        setNoVotesMessage(null);
      }
      setLoading(false);
    } catch (err) {
      setError('Ошибка при загрузке данных.');
      console.error('Ошибка при загрузке данных:', err);
      setLoading(false);
    }
  };


  if (loading) {
    return <div style={{textAlign: 'center', paddingTop: '100px'}}>
    <div style={{display: 'flex', justifyContent: 'center'}}>
    <div style={{backgroundColor: 'lightgray', padding: '20px', borderRadius: '8px'}}>
    <p style={{color: 'gray'}}>Загрузка...</p>
    </div>
    </div>
    </div>;
  }


  if (error) {
    return <p style={{ color: 'red', textAlign: 'center', marginTop: '50px' }}>{error}</p>;
  }

  return (
    <div style={{ maxWidth: '800px', margin: '50px auto', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '20px', color: '#000' }}>Проголосовавшие за вариант {votingVariantId}</h1>

      {noVotesMessage && (
        <p style={{ color: 'gray', textAlign: 'center', marginBottom: '10px' }}>{noVotesMessage}</p>
      )}

      {!noVotesMessage && votedUsers.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {votedUsers.map(user => (
            <li key={user.id} style={{ marginBottom: '10px' }}>
              <Link
                to={`/users/${user.id}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  textDecoration: 'none',
                  color: '#333',
                  fontSize: '16px',
                  padding: '10px',
                  borderRadius: '5px',
                  backgroundColor: '#fff',
                  border: '1px solid #eee',
                  transition: 'background-color 0.3s',
                  "&:hover": { backgroundColor: "#e0e0e0" }
                }}
              >
                  <div>
                  {user.username}
                  </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default VotedUsers;
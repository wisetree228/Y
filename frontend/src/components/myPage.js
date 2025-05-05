import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';

const MainProfile = () => {
    const [user, setUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [friends, setFriends] = useState([]);
    const [showFriends, setShowFriends] = useState(false);
    const [friendsLoading, setFriendsLoading] = useState(false);
    const navigate = useNavigate();
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({
        email: '',
        username: '',
        name: '',
        surname: '',
        password: ''
    });
    const [friendRequests, setFriendRequests] = useState([]);
    const [showRequests, setShowRequests] = useState(false);
    const [requestsLoading, setRequestsLoading] = useState(false);
    const fileInputRef = useRef(null);


    const handleAvatarChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Проверка типа файла
        if (!file.type.match('image.*')) {
            alert('Пожалуйста, выберите файл изображения (JPEG, PNG и т.д.)');
            return;
        }

        // Проверка размера файла (например, не более 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Файл слишком большой. Максимальный размер - 5MB');
            return;
        }

        const formData = new FormData();
        formData.append('uploaded_file', file);

        try {
            await axios.post(`${API_BASE_URL}/avatar`, formData, {
                withCredentials: true,
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            
            // Обновляем аватар, добавляя timestamp для избежания кеширования
            setUser(prev => ({
                ...prev,
                avatar: `${API_BASE_URL}/mypage/avatar?t=${Date.now()}`
            }));
            
            alert('Аватар успешно обновлен!');
        } catch (error) {
            console.error('Ошибка при обновлении аватара:', error);
            //setError(error.response?.data?.detail || 'Ошибка при обновлении аватара');
        }
    };

    const triggerFileInput = () => {
        fileInputRef.current.click();
    };


    const fetchFriendRequests = async () => {
        try {
            setRequestsLoading(true);
            const response = await axios.get(`${API_BASE_URL}/friendship_requests`, {
                withCredentials: true
            });
            setFriendRequests(response.data.friendship_requests || []);
            setShowRequests(!showRequests);
        } catch (error) {
            console.error('Ошибка при загрузке запросов дружбы:', error);
        } finally {
            setRequestsLoading(false);
        }
    };


    const handleAcceptRequest = async (authorId) => {
        try {
            await axios.post(
                `${API_BASE_URL}/friendship_request/${authorId}`,
                {},
                { withCredentials: true }
            );
            // Обновляем список запросов и друзей
            fetchFriendRequests();
            fetchFriends();
        } catch (error) {
            console.error('Ошибка при принятии запроса:', error);
        }
    };

    // Функция для отклонения запроса дружбы
    const handleRejectRequest = async (requestId) => {
        try {
            await axios.delete(
                `${API_BASE_URL}/friendship_request/${requestId}`,
                { withCredentials: true }
            );
            // Обновляем список запросов
            fetchFriendRequests();
        } catch (error) {
            console.error('Ошибка при отклонении запроса:', error);
        }
    };


    const fetchFriends = async () => {
        try {
            setFriendsLoading(true);
            const response = await axios.get(`${API_BASE_URL}/friends`, {
                withCredentials: true
            });
            setFriends(response.data.friends_list || []);
            setShowFriends(!showFriends);
        } catch (error) {
            console.error('Ошибка при загрузке друзей:', error);
        } finally {
            setFriendsLoading(false);
        }
    };


    const handleDeletePost = async (postId) => {
        // Подтверждение удаления
        const isConfirmed = window.confirm('Вы уверены, что хотите удалить этот пост?');
        
        if (!isConfirmed) return;
    
        try {
            await axios.delete(`${API_BASE_URL}/post/${postId}`, {
                withCredentials: true
            });
            
            // Обновляем список постов после удаления
            const response = await axios.get(`${API_BASE_URL}/mypage`, {
                withCredentials: true
            });
            setPosts(response.data.posts || []);
            
            alert('Пост успешно удален');
        } catch (error) {
            console.error('Ошибка при удалении поста:', error);
            alert('Не удалось удалить пост');
        }
    };


    useEffect(() => {
        const fetchData = async () => {
            try {
                // Загрузка данных пользователя
                await CheckAuthorization();
                const userResponse = await axios.get(`${API_BASE_URL}/mypage`, {
                    withCredentials: true
                });
                setUser(userResponse.data);
                
                // Загрузка постов пользователя
                if (userResponse.data.posts) {
                    setPosts(userResponse.data.posts);
                }


                fetchFriendRequests();
                

                setLoading(false);
            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
                setError('Ошибка при загрузке данных');
                setLoading(false);
            }
        };


        fetchData();

        const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      /* Основные стили */
body {
  background-color: #396687;
  color: #fff;
  font-family: Arial, sans-serif;
  line-height: 1.6;
  margin: 0;
  padding: 20px;
}

/* Контейнер */
div[style*="max-width: '800px'"] {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  margin: 0 auto;
}

/* Заголовки */
h1, h2, h3 {
  color: white;
  margin-top: 0;
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

h2 {
  font-size: 1.5rem;
  margin: 20px 0 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 8px;
}

h3 {
  font-size: 1.3rem;
  margin: 15px 0 10px;
}

/* Карточки */
div[style*="border: '1px solid #ccc'"],
div[style*="border: '1px solid #e0e0e0'"] {
  background-color: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 10px !important;
  padding: 20px !important;
  margin-bottom: 20px !important;
  backdrop-filter: blur(5px);
}

/* Аватар */
img[alt^="Аватар"] {
  border: 2px solid #3c91cf !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Кнопки (общие) */
button {
  background-color: #3c91cf !important;
  color: white !important;
  border: none !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  font-weight: 500;
}

button:hover {
  background-color: #2e7ab3 !important;
  transform: translateY(-1px);
}

/* Специальные кнопки */
button[style*="background: none"] {
  background: transparent !important;
  color: #a8d4ff !important;
  padding: 5px 10px !important;
}

button[style*="color: red"] {
  color: #ff8a8a !important;
}

button[style*="background-color: #4CAF50"] {
  background-color: #4CAF50 !important;
}

button[style*="background-color: #f44336"] {
  background-color: #e53935 !important;
}

button[style*="background-color: #FF9800"] {
  background-color: #FF9800 !important;
}

/* Формы и инпуты */
input {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: white !important;
  border-radius: 6px;
  padding: 8px 12px;
  width: 100%;
  margin-bottom: 10px;
}

input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

/* Ссылки */
a {
  color: #a8d4ff;
  text-decoration: none;
  transition: color 0.2s;
}

a:hover {
  color: #fff;
}

/* Списки */
div[style*="gridTemplateColumns"] {
  gap: 15px;
  margin: 15px 0;
}

/* Варианты голосования */
div[style*="marginBottom: '15px'"] > div {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  border: none !important;
  border-radius: 6px !important;
  transition: all 0.2s;
}

div[style*="marginBottom: '15px'"] > div:hover {
  background-color: rgba(60, 145, 207, 0.3) !important;
}

div[style*="backgroundColor: '#f0f0f0'"] {
  background-color: rgba(60, 145, 207, 0.4) !important;
}

/* Изображения в постах */
img[alt="Изображение поста"] {
  max-height: 300px;
  object-fit: cover;
  border-radius: 8px !important;
}

/* Текст */
p {
  margin: 10px 0;
  color: rgba(255, 255, 255, 0.9);
}

p[style*="color: #666"] {
  color: rgba(255, 255, 255, 0.6) !important;
}

/* Мелкий текст */
small {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
}

/* Адаптивность */
@media (max-width: 600px) {
  div[style*="max-width: '800px'"] {
    padding: 15px;
  }
  
  div[style*="gridTemplateColumns"] {
    grid-template-columns: 1fr !important;
  }
}
    `;
    
    // Добавляем в head документа
    document.head.appendChild(styleElement);
    return () => {
        document.head.removeChild(styleElement);
      };
    }, []);



    const handleLike = async (postId) => {
        try {
            const response = await axios.post(
                `${API_BASE_URL}/post/${postId}/like`,
                {},
                { withCredentials: true }
            );
            
            setPosts(posts.map(post => {
                if (post.id === postId) {
                    return {
                        ...post,
                        likes_count: response.data.likes_count,
                        liked_status: response.data.status === 'liked'
                    };
                }
                return post;
            }));
        } catch (err) {
            console.error('Ошибка при лайке:', err);
        }
    };

    const handleVote = async (variantId, postId) => {
        try {
            await axios.post(
                `${API_BASE_URL}/vote/${variantId}`,
                {},
                { withCredentials: true }
            );
            // Обновляем данные постов после голосования
            const updatedPosts = await axios.get(`${API_BASE_URL}/mypage`, {
                withCredentials: true
            });
            setPosts(updatedPosts.data.posts || []);
        } catch (err) {
            console.error('Ошибка при голосовании:', err);
        }
    };

    const handleEditPost = async (postId) => {
        navigate(`/edit_post/${postId}`);
    };

    const handleLogout = async () => {
        try {
            await axios.post(`${API_BASE_URL}/logout`, {}, {
                withCredentials: true
            });
            await CheckAuthorization();
        } catch (error) {
            console.error('Ошибка при выходе:', error);
            setError('Не удалось выйти из аккаунта');
        }
    };


    const handleEditToggle = () => {
      setIsEditing(!isEditing);
  };

  const handleEditChange = (e) => {
      const { name, value } = e.target;
      setEditData(prev => ({
          ...prev,
          [name]: value
      }));
  };

  const handleDeleteVote = async (postId) => {
    try {
      await axios.delete(
        `${API_BASE_URL}/vote/${postId}`,
        { withCredentials: true }
      );
      const updatedPosts = await axios.get(`${API_BASE_URL}/mypage`, {
        withCredentials: true
    });
    setPosts(updatedPosts.data.posts || []);
    } catch (err) {
      console.error('Ошибка при удалении голоса:', err);
    }
  };

  const handleSaveProfile = async () => {
      try {
          // Подготавливаем данные для отправки (удаляем пустые поля)
          const dataToSend = Object.fromEntries(
              Object.entries(editData).filter(([_, v]) => v !== '')
          );

          const response = await axios.put(
              `${API_BASE_URL}/profile`,
              dataToSend,
              { withCredentials: true }
          );

          // Обновляем данные пользователя
          setUser(prev => ({
              ...prev,
              ...dataToSend
          }));
          
          setIsEditing(false);
          alert('Профиль успешно обновлен');
      } catch (error) {
          console.error('Ошибка при обновлении профиля:', error);
          setError(error.response?.data?.detail || 'Ошибка при обновлении профиля');
      }
  };

    if (loading) {
        return <p>Загрузка...</p>;
    }

    if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
    }

    if (!user) {
        return <p>Данные пользователя не загружены</p>;
    }

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
            <button
                onClick={() => navigate(-1)}
                style={{
                    padding: '10px 20px',
                    backgroundColor: '#007bff',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    marginBottom: '20px',
                }}
            >Вернуться назад</button>
            {/* Добавляем кнопку выхода в верхний правый угол */}
            <div style={{ 
                display: 'flex', 
                justifyContent: 'flex-end',
                marginBottom: '20px'
            }}>
                <button 
                    onClick={handleLogout}
                    style={{ 
                        padding: '8px 16px',
                        backgroundColor: '#f44336',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Выйти из аккаунта
                </button>
            </div>
            {/* Шапка профиля */}
            <div style={{ 
                border: '1px solid #ccc', 
                padding: '20px', 
                marginBottom: '20px',
                borderRadius: '8px',
                backgroundColor: '#5aabe5',
                textAlign: 'center'
            }}>
                <div style={{ position: 'relative', display: 'inline-block' }}>
                    <img
                        src={`${API_BASE_URL}/mypage/avatar?t=${Date.now()}`}
                        alt={`Аватар ${user.username}`}
                        style={{ 
                            width: '100px', 
                            height: '100px', 
                            borderRadius: '50%',
                            objectFit: 'cover',
                            cursor: 'pointer'
                        }}
                        onClick={triggerFileInput}
                        onError={(e) => {
                            e.target.src = '/default-avatar.png';
                            console.error('Ошибка загрузки аватарки');
                        }}
                    />
                    <button 
                        onClick={triggerFileInput}
                        style={{
                            position: 'absolute',
                            bottom: '0',
                            right: '0',
                            background: '#2196F3',
                            color: 'white',
                            border: 'none',
                            borderRadius: '50%',
                            width: '30px',
                            height: '30px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        ✏️
                    </button>
                </div>
                
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleAvatarChange}
                    accept="image/*"
                    style={{ display: 'none' }}
                />

                {/* Кнопка для показа/скрытия списка друзей */}
                <div style={{ marginTop: '15px' }}>
                    <button 
                        onClick={fetchFriends}
                        disabled={friendsLoading}
                        style={{ 
                            padding: '8px 16px',
                            backgroundColor: '#2196F3',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            marginRight: '10px'
                        }}
                    >
                        {friendsLoading ? 'Загрузка...' : (showFriends ? 'Скрыть друзей' : 'Показать друзей')}
                    </button>
                
                {isEditing ? (
                    <div style={{ marginTop: '20px' }}>
                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Email:</label>
                            <input
                                type="email"
                                name="email"
                                value={editData.email}
                                onChange={handleEditChange}
                                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                            />
                        </div>
                        
                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Username:</label>
                            <input
                                type="text"
                                name="username"
                                value={editData.username}
                                onChange={handleEditChange}
                                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                            />
                        </div>
                        
                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Имя:</label>
                            <input
                                type="text"
                                name="name"
                                value={editData.name}
                                onChange={handleEditChange}
                                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                            />
                        </div>
                        
                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Фамилия:</label>
                            <input
                                type="text"
                                name="surname"
                                value={editData.surname}
                                onChange={handleEditChange}
                                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                            />
                        </div>
                        
                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Новый пароль (оставьте пустым, чтобы не менять):</label>
                            <input
                                type="password"
                                name="password"
                                value={editData.password}
                                onChange={handleEditChange}
                                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                            />
                        </div>
                        
                        <div style={{ display: 'flex', justifyContent: 'center', gap: '10px' }}>
                            <button 
                                onClick={handleSaveProfile}
                                style={{ 
                                    padding: '8px 16px',
                                    backgroundColor: '#4CAF50',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer'
                                }}
                            >
                                Сохранить
                            </button>
                            <button 
                                onClick={handleEditToggle}
                                style={{ 
                                    padding: '8px 16px',
                                    backgroundColor: '#f44336',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer'
                                }}
                            >
                                Отмена
                            </button>
                        </div>
                    </div>
                ) : (
                    <>
                        <h1>{user.username}</h1>
                        <p>{user.name} {user.surname}</p>
                        <p>{user.email}</p>
                        
                        <button 
                            onClick={handleEditToggle}
                            style={{ 
                                marginTop: '15px',
                                padding: '8px 16px',
                                backgroundColor: '#2196F3',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}
                        >
                            Редактировать профиль
                        </button>
                    </>
                )}
            </div>


            {/* Кнопка для запросов дружбы */}
            <button 
                    onClick={fetchFriendRequests}
                    disabled={requestsLoading}
                    style={{ 
                        padding: '8px 16px',
                        backgroundColor: '#FF9800',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        margin: '10px',
                        position: 'relative'
                    }}
                >
                    {requestsLoading ? 'Загрузка...' : `Запросы дружбы (${friendRequests.length})`}
                </button>

                {/* Список запросов дружбы */}
                {showRequests && (
                    <div style={{ 
                        marginTop: '20px',
                        borderTop: '1px solid #eee',
                        paddingTop: '15px'
                    }}>
                        <h3>Входящие запросы дружбы</h3>
                        {friendRequests.length === 0 ? (
                            <p>Нет входящих запросов</p>
                        ) : (
                            <div style={{ 
                                display: 'grid',
                                gridTemplateColumns: '1fr',
                                gap: '10px',
                                marginTop: '10px'
                            }}>
                                {friendRequests.map(request => (
                                    <div 
                                        key={request.id}
                                        style={{ 
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                            padding: '10px',
                                            border: '1px solid #eee',
                                            borderRadius: '5px'
                                        }}
                                    >
                                        <Link 
                                            to={`/users/${request.author_id}`}
                                            style={{ 
                                                display: 'flex',
                                                alignItems: 'center',
                                                textDecoration: 'none',
                                                color: 'inherit',
                                                flexGrow: 1
                                            }}
                                        >
                                            <img
                                                src={`${API_BASE_URL}/user/${request.author_id}/avatar?t=${Date.now()}`}
                                                alt={`Аватар ${request.author_username}`}
                                                style={{ 
                                                    width: '40px', 
                                                    height: '40px', 
                                                    borderRadius: '50%',
                                                    objectFit: 'cover',
                                                    marginRight: '10px'
                                                }}
                                                onError={(e) => {
                                                    e.target.src = '/default-avatar.png';
                                                }}
                                            />
                                            <span>{request.author_username}</span>
                                        </Link>
                                        <div>
                                            <button 
                                                onClick={() => handleAcceptRequest(request.author_id)}
                                                style={{ 
                                                    padding: '5px 10px',
                                                    backgroundColor: '#4CAF50',
                                                    color: 'white',
                                                    border: 'none',
                                                    borderRadius: '4px',
                                                    cursor: 'pointer',
                                                    marginRight: '5px'
                                                }}
                                            >
                                                Принять
                                            </button>
                                            <button 
                                                onClick={() => handleRejectRequest(request.id)}
                                                style={{ 
                                                    padding: '5px 10px',
                                                    backgroundColor: '#f44336',
                                                    color: 'white',
                                                    border: 'none',
                                                    borderRadius: '4px',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                Отклонить
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}


            {/* Список друзей */}
            {showFriends && (
                    <div style={{ 
                        marginTop: '20px',
                        borderTop: '1px solid #eee',
                        paddingTop: '15px'
                    }}>
                        <h3>Друзья</h3>
                        {friends.length === 0 ? (
                            <p>У вас пока нет друзей</p>
                        ) : (
                            <div style={{ 
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
                                gap: '10px',
                                marginTop: '10px'
                            }}>
                                {friends.map(friend => (
                                    <Link 
                                        to={`/users/${friend.id}`} 
                                        key={friend.id}
                                        style={{ 
                                            textDecoration: 'none',
                                            color: 'inherit',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            alignItems: 'center',
                                            padding: '10px',
                                            borderRadius: '5px',
                                            border: '1px solid #eee',
                                            transition: 'background-color 0.2s'
                                        }}
                                    >
                                        <img
                                            src={`${API_BASE_URL}/user/${friend.id}/avatar?t=${Date.now()}`}
                                            alt={`Аватар ${friend.username}`}
                                            style={{ 
                                                width: '50px', 
                                                height: '50px', 
                                                borderRadius: '50%',
                                                objectFit: 'cover',
                                                marginBottom: '5px'
                                            }}
                                            onError={(e) => {
                                                e.target.src = '/default-avatar.png';
                                            }}
                                        />
                                        <span style={{ 
                                            fontSize: '0.9rem',
                                            textAlign: 'center',
                                            wordBreak: 'break-word'
                                        }}>
                                            {friend.username}
                                        </span>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>

            

            {/* Посты пользователя */}
            <div>
                <h2>Мои посты</h2>
                {posts.length === 0 ? (
                    <p>У вас пока нет постов</p>
                ) : (
                    posts.map(post => (
                        <div 
                            key={post.id} 
                            style={{ 
                                border: '1px solid #e0e0e0',
                                padding: '20px',
                                marginBottom: '20px',
                                borderRadius: '8px',
                                backgroundColor: '#5aabe5',
                                boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                                <img
                                    src={`${API_BASE_URL}/user/${post.author_id}/avatar?t=${Date.now()}`}
                                    alt={`Аватар ${post.author_username}`}
                                    style={{ 
                                        width: '40px', 
                                        height: '40px', 
                                        borderRadius: '50%',
                                        marginRight: '10px'
                                    }}
                                    onError={(e) => {
                                        e.target.src = '/default-avatar.png';
                                    }}
                                />
                                    <div>
                                        <p style={{ fontWeight: 'bold', margin: 0 }}>{user.username}</p>
                                        <p style={{ color: '#666', fontSize: '0.8rem', margin: 0 }}>
                                            {new Date(post.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                                
                                {/* Кнопки управления постом */}
                                <div>
                                    <button 
                                        onClick={() => handleEditPost(post.id)}
                                        style={{ 
                                            marginRight: '10px',
                                            padding: '5px 10px',
                                            backgroundColor: '#f0f0f0',
                                            border: '1px solid #ccc',
                                            borderRadius: '4px',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        Редактировать
                                    </button>
                                    <button 
                                        onClick={() => handleDeletePost(post.id)}
                                        style={{ 
                                            padding: '5px 10px',
                                            backgroundColor: '#ffebee',
                                            border: '1px solid #ffcdd2',
                                            borderRadius: '4px',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        Удалить
                                    </button>
                                </div>
                            </div>
                            
                            
                            <div style={{ width: '100%', overflowWrap: 'break-word', wordBreak: 'break-all' }}>
                  <p style={{ marginBottom: '15px', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>{post.text}</p>
                </div>
                            
                            {post.images_id && post.images_id.length > 0 && (
                                <div style={{ 
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                                    gap: '10px',
                                    marginBottom: '15px'
                                }}>
                                    {post.images_id.map(imageId => (
                                        <img
                                            key={imageId}
                                            src={`${API_BASE_URL}/posts/image/${imageId}?t=${Date.now()}`}
                                            alt="Изображение поста"
                                            style={{
                                                width: '100%',
                                                borderRadius: '5px',
                                                objectFit: 'cover'
                                            }}
                                        />
                                    ))}
                                </div>
                            )}
                            
                            {post.voting_variants && post.voting_variants.length > 0 && (
                                <div style={{ marginBottom: '15px' }}>
                                    {post.voting_variants.map(variant => (
                                        <div 
                                            key={variant.id}
                                            onClick={() => handleVote(variant.id, post.id)}
                                            style={{
                                                marginBottom: '8px',
                                                padding: '10px',
                                                border: '1px solid #e0e0e0',
                                                borderRadius: '5px',
                                                cursor: 'pointer',
                                                backgroundColor: variant.user_voted ? '#f0f0f0' : 'transparent'
                                            }}
                                        >
                                            {variant.text} {`${variant.percent} % (${variant.votes_count} голосов)`}
                                        </div>
                                    ))}
                                </div>
                            )}
                            
                            <div style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between',
                                color: '#666',
                                fontSize: '0.9rem'
                            }}>
                                <button 
                                    onClick={() => handleLike(post.id)}
                                    style={{ 
                                        background: 'none',
                                        border: 'none',
                                        cursor: 'pointer',
                                        color: post.liked_status ? 'red' : '#666'
                                    }}
                                >
                                    ❤️ {post.likes_count} лайков
                                </button>
                                
                                <Link to={`/posts/${post.id}`}>
                                    <button style={{ 
                                        background: 'none',
                                        border: 'none',
                                        cursor: 'pointer',
                                        color: '#666'
                                    }}>
                                        💬 {post.comments_count} комментариев
                                    </button>
                                </Link>

                                {post.voting_variants.length > 0 && (
              <button 
              onClick={() => handleDeleteVote(post.id)}
              style={{
                backgroundColor: '#f44336',
                color: 'white',
                border: 'none',
                padding: '5px 10px',
                borderRadius: '4px',
                margintop: '10px',
                cursor: 'pointer'
              }}
            >
              Удалить мой голос
            </button>
            )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MainProfile;
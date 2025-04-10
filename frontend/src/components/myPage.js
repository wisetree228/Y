import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const MainProfile = () => {
    const [user, setUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({
        email: '',
        username: '',
        name: '',
        surname: '',
        password: ''
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Загрузка данных пользователя
                const userResponse = await axios.get(`${API_BASE_URL}/mypage`, {
                    withCredentials: true
                });
                setUser(userResponse.data);
                
                // Загрузка постов пользователя
                if (userResponse.data.posts) {
                    setPosts(userResponse.data.posts);
                }

                

                setLoading(false);
            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
                setError('Ошибка при загрузке данных');
                setLoading(false);
            }
        };

        fetchData();
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

    const handleDeletePost = async (postId) => {
        // Заглушка для удаления поста
        console.log(`Удаление поста с ID: ${postId}`);
        alert('Функция удаления поста будет реализована позже');
    };

    const handleEditPost = async (postId) => {
        // Заглушка для редактирования поста
        console.log(`Редактирование поста с ID: ${postId}`);
        alert('Функция редактирования поста будет реализована позже');
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
            {/* Шапка профиля */}
            <div style={{ 
                border: '1px solid #ccc', 
                padding: '20px', 
                marginBottom: '20px',
                borderRadius: '8px',
                backgroundColor: '#fff',
                textAlign: 'center'
            }}>
                <img
                    src={`${API_BASE_URL}/mypage/avatar`}
                    alt={`Аватар ${user.username}`}
                    style={{ 
                        width: '100px', 
                        height: '100px', 
                        borderRadius: '50%',
                        objectFit: 'cover'
                    }}
                />
                
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
                                backgroundColor: '#fff',
                                boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                                    <img
                                        src={`${API_BASE_URL}/mypage/avatar`}
                                        alt={`Аватар ${user.username}`}
                                        style={{ 
                                            width: '40px', 
                                            height: '40px', 
                                            borderRadius: '50%',
                                            marginRight: '10px'
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
                            
                            <p style={{ marginBottom: '15px', lineHeight: '1.5' }}>{post.text}</p>
                            
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
                                            src={`${API_BASE_URL}/posts/image/${imageId}`}
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
                                            {variant.text} {variant.percent && `(${variant.percent}%)`}
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
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MainProfile;
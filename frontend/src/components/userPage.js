import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';

const UserChannel = () => {
    const [user, setUser] = useState(null);
    const { authorId } = useParams(); 
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isFriend, setIsFriend] = useState(false);
    const [friendshipLoading, setFriendshipLoading] = useState(false);
    const [friendRequestSent, setFriendRequestSent] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            await CheckAuthorization();
            try {
                // Если это своя страница редиректим на свой профиль
                const idResponse = await axios.get(`${API_BASE_URL}/my_id`, {
                    withCredentials: true
                });
                if (idResponse.data.id===Number(authorId)){
                    navigate('/home')
                }
                
            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
                setError('Ошибка при загрузке данных');
                setLoading(false);
            }

            try {
                // Загрузка данных пользователя
                const userResponse = await axios.get(`${API_BASE_URL}/users/${authorId}`, {
                    withCredentials: true
                });
                setUser(userResponse.data);
                
                // Загрузка постов пользователя
                if (userResponse.data.posts) {
                    setPosts(userResponse.data.posts);
                }

                // Проверка статуса дружбы
                const friendStatusResponse = await axios.get(
                    `${API_BASE_URL}/isfriend/${authorId}`,
                    { withCredentials: true }
                );
                setIsFriend(friendStatusResponse.data.isFriend);


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
  color: #e0e0e0;
  font-family: Arial, sans-serif;
  padding: 20px;
}

/* Контейнер */
div[style*="max-width: '800px'"] {
  max-width: 700px;
  margin: 0 auto;
}

/* Карточка профиля */
div[style*="border: '1px solid #ccc'"] {
  background-color: #2d4d66;
  border: 1px solid #3c91cf !important;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  color: #fff;
  text-align: center;
}

/* Аватар */
img[alt^="Аватар"] {
  border: 2px solid #3c91cf;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Заголовки */
h1, h2 {
  color: #fff;
  margin: 15px 0 10px;
}

/* Текст */
p {
  margin: 8px 0;
  color: #e0e0e0;
}

/* Кнопки */
button {
  background-color: #3c91cf;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin: 5px;
  font-size: 14px;
}

button:hover {
  background-color: #2e7ab3;
}

/* Специальные кнопки */
button[style*="background: none"] {
  background: transparent !important;
  color: #a8d4ff !important;
  padding: 0 !important;
}

button[style*="color: red"] {
  color: #ff6b6b !important;
}

button[style*="background-color: '#f44336'"] {
  background-color: #e53935 !important;
}

button[style*="background-color: '#4CAF50'"] {
  background-color: #4caf50 !important;
}

button[style*="background-color: '#ff9800'"] {
  background-color: #ff9800 !important;
}

/* Карточки постов */
div[style*="border: '1px solid #e0e0e0'"] {
  background-color: #2d4d66;
  border: 1px solid #3c91cf !important;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  color: #fff;
}

/* Изображения в постах */
img[alt="Изображение поста"] {
  max-width: 100%;
  border-radius: 6px;
  border: 1px solid #3c91cf;
}

/* Варианты голосования */
div[style*="marginBottom: '15px'"] > div {
  background-color: rgba(60, 145, 207, 0.2) !important;
  border: 1px solid #3c91cf !important;
  color: #fff !important;
  border-radius: 4px !important;
}

div[style*="backgroundColor: '#f0f0f0'"] {
  background-color: rgba(60, 145, 207, 0.4) !important;
}

/* Ссылки */
a {
  color: #a8d4ff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Мелкий текст */
small {
  color: #aaa;
}

/* Сообщения об ошибках */
p[style*="color: red"] {
  color: #ff6b6b !important;
  text-align: center;
}
    `;
    
    // Добавляем в head документа
    document.head.appendChild(styleElement);
    return () => {
        document.head.removeChild(styleElement);
      };
    }, [authorId, navigate]);

    const handleAddFriend = async () => {
        try {
            setFriendshipLoading(true);
            await axios.post(
                `${API_BASE_URL}/friendship_request/${authorId}`,
                {},
                { withCredentials: true }
            );
            setFriendRequestSent(true); // Только отмечаем что запрос отправлен
        } catch (err) {
            alert(err.response.data.detail || 'Ошибка на стороне сервера, попробуйте ещё раз!')
        } finally {
            setFriendshipLoading(false);
        }
    };

    const handleRemoveFriend = async () => {
        try {
            setFriendshipLoading(true);
            await axios.delete(
                `${API_BASE_URL}/friend/${authorId}`,
                { withCredentials: true }
            );
            setIsFriend(false);
        } catch (err) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        } finally {
            setFriendshipLoading(false);
        }
    };

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
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
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
            const updatedPosts = await axios.get(`${API_BASE_URL}/users/${authorId}`, {
                withCredentials: true
            });
            setPosts(updatedPosts.data.posts || []);
        } catch (err) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
    };

    const handleDeleteVote = async (postId) => {
        try {
          await axios.delete(
            `${API_BASE_URL}/vote/${postId}`,
            { withCredentials: true }
          );
          const updatedPosts = await axios.get(`${API_BASE_URL}/users/${authorId}/posts`, {
            withCredentials: true
        });
        setPosts(updatedPosts.data.posts || []);
        } catch (err) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
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
                backgroundColor: '#1b99b5',
                textAlign: 'center'
            }}>
                <img
                    src={`${API_BASE_URL}/user/${authorId}/avatar?t=${Date.now()}`}
                    alt={`Аватар ${user.username}`}
                    style={{ 
                        width: '100px', 
                        height: '100px', 
                        borderRadius: '50%',
                        objectFit: 'cover'
                    }}
                />
                <h1>{user.username}</h1>
                <p>{user.name} {user.surname}</p>
                <p>{user.email}</p>
            </div>

            <div style={{ marginTop: '15px' }}>
            {isFriend ? (
        <>
            <button onClick={handleRemoveFriend}>
                Удалить из друзей
            </button>
            {/* Кнопка для чата */}
            <Link to={`/chat/${authorId}`} style={{ marginLeft: '10px' }}>
                <button>
                    Чат
                </button>
            </Link>
        </>
    ) : (
        <button 
            onClick={handleAddFriend}
            disabled={friendRequestSent || friendshipLoading}
            style={{
                backgroundColor: friendRequestSent ? '#ff9800' : '#4CAF50'
            }}
        >
            {friendRequestSent ? 'Запрос отправлен' : 'Добавить в друзья'}
        </button>
    )}
            </div>
       
            {/* Посты пользователя */}
            <div>
                <h2>Посты пользователя</h2>
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
                                backgroundColor: '#1b99b5',
                                boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                                    <img
                                        src={`${API_BASE_URL}/user/${post.author_id}/avatar?t=${Date.now()}`}
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

export default UserChannel;
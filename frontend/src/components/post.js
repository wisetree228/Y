import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';

const Posts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const limit = 20;
  const navigate = useNavigate();
  
    useEffect(() => {
      CheckAuthorization();
      fetchPosts();
      const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      /* Основные стили */
body {
  background-color: #396687;
  color: #fff;
  font-family: Arial, sans-serif;
  line-height: 1.6;
  padding: 20px;
}

/* Контейнер */
div {
  max-width: 800px;
  margin: 0 auto;
}

/* Заголовок */
h1 {
  color: white;
  text-align: center;
  margin-bottom: 20px;
}

/* Карточка поста */
div > div[style*="border: '1px solid #e0e0e0'"] {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 10px !important;
  padding: 20px !important;
  margin-bottom: 20px !important;
  color: white;
}

/* Текст поста */
p[style*="line-height: '1.5'"] {
  color: #fff !important;
  margin: 15px 0 !important;
}

/* Информация об авторе */
div[style*="display: 'flex'"] p {
  color: #fff !important;
}

div[style*="display: 'flex'"] p[style*="color: #666"] {
  color: rgba(255, 255, 255, 0.7) !important;
}

/* Кнопки (общие стили) */
button {
  background-color: #3c91cf !important;
  color: white !important;
  border: none !important;
  border-radius: 6px !important;
  padding: 10px 15px !important;
  cursor: pointer !important;
  transition: background-color 0.2s !important;
  margin: 5px 0 !important;
}

button:hover {
  background-color: #2e7ab3 !important;
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

/* Варианты голосования */
div[style*="marginBottom: '15px'"] > div {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  border: none !important;
  border-radius: 6px !important;
  transition: background-color 0.2s;
}

div[style*="marginBottom: '15px'"] > div:hover {
  background-color: rgba(60, 145, 207, 0.3) !important;
}

div[style*="backgroundColor: '#f0f0f0'"] {
  background-color: rgba(60, 145, 207, 0.4) !important;
}

/* Изображения */
img {
  border-radius: 8px !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

img[alt^="Аватар"] {
  border: 2px solid #3c91cf !important;
}

/* Сообщения */
p[style*="color: red"] {
  color: #ff6b6b !important;
  text-align: center;
}

p[style*="color: #666"] {
  color: rgba(255, 255, 255, 0.6) !important;
  text-align: center;
}

/* Мелкий текст */
small {
  color: rgba(255, 255, 255, 0.5) !important;
  display: block;
  margin-top: 15px;
}
    `;
    
    // Добавляем в head документа
    document.head.appendChild(styleElement);
    return () => {
        document.head.removeChild(styleElement);
      };
    }, []);


    const fetchPosts = async (loadMore = false) => {
      const currentSkip = loadMore ? skip : 0;
      
      try {
        loadMore ? setLoadingMore(true) : setLoading(true);
        
        const response = await axios.get(
          `${API_BASE_URL}/posts?limit=${limit}&skip=${currentSkip}`, 
          { withCredentials: true }
        );

        const newPosts = response.data.posts || [];
        
        if (loadMore) {
          setPosts(prevPosts => [...prevPosts, ...newPosts]);
        } else {
          setPosts(newPosts);
        }

        setHasMore(newPosts.length === limit);
        setSkip(currentSkip + newPosts.length);
      } catch (err) {
        console.error('Ошибка при загрузке постов:', err);
        setError('Ошибка при загрузке постов');
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    };

    const loadMorePosts = () => {
      if (hasMore && !loadingMore) {
        fetchPosts(true);
      }
    };

    const fetchSinglePost = async (postId) => {
      try {
        const response = await axios.get(`${API_BASE_URL}/posts/${postId}`, { 
          withCredentials: true 
        });
        return response.data.post;
      } catch (err) {
        console.error('Ошибка при загрузке поста:', err);
        return null;
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

        await new Promise(resolve => setTimeout(resolve, 250)); //Небольшая задержка чтобы бэкенд успел обработать голосовалку
        const updatedPost = await fetchSinglePost(postId);
        if (updatedPost) {
          setPosts(posts.map(post => 
            post.id === postId ? updatedPost : post
          ));
        }
      } catch (err) {
        alert('Ошибка при голосовании, попробуйте ещё раз!');
      }
    };

    const handleDeleteVote = async (postId) => {
      try {
        await axios.delete(
          `${API_BASE_URL}/vote/${postId}`,
          { withCredentials: true }
        );
        
        // Получаем обновленные данные только для этого поста
        const updatedPost = await fetchSinglePost(postId);
        if (updatedPost) {
          setPosts(posts.map(post => 
            post.id === postId ? updatedPost : post
          ));
        }
      } catch (err) {
        alert('Ошибка при удалении голоса, попробуйте ещё раз!');
      }
    };
  
    if (loading) {
      return <p>Загрузка...</p>;
    }
    if (error) {
      return <p style={{ color: 'red' }}>{error}</p>;
    }

    return (
      <div>
        <h1>Посты</h1>
        <Link to="/home">
          <button style={{ marginTop: '10px' }}>Профиль</button>
        </Link><br></br>
        <Link to="/create-post">
              <button style={{ 
                backgroundColor: '#4CAF50',
                color: 'white',
                border: 'none',
                padding: '10px 15px',
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                Создать пост
              </button>
            </Link>
        
        {posts.map(post => (
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
              />
              <div>
                <p style={{ fontWeight: 'bold', margin: 0 }}>{post.author_username}</p>
                <p style={{ color: '#666', fontSize: '0.8rem', margin: 0 }}>
                  {new Date(post.created_at).toLocaleString()}
                </p>
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
                      backgroundColor: variant.selected ? '#f0f0f0' : 'transparent'
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
            </div>
            
            <div style={{ marginTop: '10px' }}>
              <Link to={`/users/${post.author_id}`}>
                <button style={{ marginRight: '10px' }}>Перейти в канал</button>
              </Link>
              <Link to={`/posts/${post.id}`}>
                <button>Комментарии</button>
              </Link>
            </div>

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
            

            
            <small>{new Date(post.created_at).toLocaleDateString()}</small>
          </div>
        ))}

{hasMore && (
          <div style={{ textAlign: 'center', margin: '20px 0' }}>
            <button 
              onClick={loadMorePosts}
              disabled={loadingMore}
              style={{
                padding: '10px 20px',
                backgroundColor: '#2196F3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              {loadingMore ? 'Загрузка...' : 'Загрузить ещё'}
            </button>
          </div>
        )}
        
        {!hasMore && posts.length > 0 && (
          <p style={{ textAlign: 'center', color: '#fff' }}>Вы достигли конца списка</p>
        )}

      </div>
    )
};

export default Posts;
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const Posts = () => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();
  
    useEffect(() => {
      checkAuthorization();
      fetchPosts();
    }, []);

    const checkAuthorization = async () => {
      try {
        const response = await axios.get(API_BASE_URL + '/my_id', { withCredentials: true });
      } catch (err) {
        navigate('/')
      }
    };


    const fetchPosts = async () => {
      try {
        const response = await axios.get(API_BASE_URL + '/posts', { withCredentials: true });
        setPosts(response.data.posts);
        setLoading(false);
      } catch (err) {
        console.error('Ошибка при загрузке постов:', err);
        setError('Ошибка при загрузке постов');
        setLoading(false);
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
        fetchPosts();
      } catch (err) {
        console.error('Ошибка при голосовании:', err);
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
        </Link>
        
        {posts.map(post => (
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
                      backgroundColor: variant.selected ? '#f0f0f0' : 'transparent'
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
            
            <div style={{ marginTop: '10px' }}>
              <Link to={`/users/${post.author_id}`}>
                <button style={{ marginRight: '10px' }}>Перейти в канал</button>
              </Link>
              <Link to={`/posts/${post.id}`}>
                <button>Комментарии</button>
              </Link>
            </div>
            
            <small>{new Date(post.created_at).toLocaleDateString()}</small>
          </div>
        ))}
      </div>
    )
};

export default Posts;
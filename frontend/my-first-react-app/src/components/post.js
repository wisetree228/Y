
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from './config';


const Posts = () => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
  
    useEffect(() => {
      axios.get(API_BASE_URL+'/posts')
        .then(response => {
          setPosts(response.data.posts);
          setLoading(false);
        })
        .catch(error => {
          console.error('Ошибка при загрузке постов:', error);
          setError('Ошибка при загрузке постов');
          setLoading(false);
        });
    }, []);
  
    if (loading) {
      return <p>Загрузка...</p>;
    }
    if (error) {
      return <p style={{ color: 'red' }}>{error}</p>;
    }
    return (
    <body>
      
        <div>
        <h1>Посты</h1>
        <Link
          to={{
          pathname: `/home`,
          }}
        >
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
                  src={`https://i.pravatar.cc/50?u=${post.author_id}`}
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
              <div>
            <Link
              to={{
              pathname: `/users/${post.author_id}`,
              state: { author_id: post.author_id }, 
              }}
            >
              <button style={{ marginTop: '10px' }}>Перейти в канал</button>
            </Link>
          </div>
            <small>{new Date(post.created_at).toLocaleDateString()}</small>
            <div>
            <Link
              to={{
              pathname: `/posts/${post.id}/comments`,
              state: { post }, 
              }}
            >
              <button style={{ marginTop: '10px' }}>Комментарии</button>
            </Link>
          </div>
              
              {/* Блок с изображениями */}
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
                      src={`/api/images/${imageId}`}
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
              
              {/* Блок с вариантами голосования */}
              {post.voting_variants && post.voting_variants.length > 0 && (
                <div style={{ marginBottom: '15px' }}>
                  {post.voting_variants.map(variant => (
                    <div 
                      key={variant.id}
                      style={{
                        marginBottom: '8px',
                        padding: '10px',
                        border: '1px solid #e0e0e0',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        ':hover': {
                          backgroundColor: '#f8f9fa'
                        }
                      }}
                    >
                      {variant.text}
                    </div>
                  ))}
                </div>
              )}
              
              {/* Блок с лайками и комментариями */}
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                color: '#666',
                fontSize: '0.9rem'
              }}>
                <span>❤️ {post.likes_count} лайков</span>
                <span>💬 {post.comments_count} комментариев</span>
              </div>
            </div>
          ))}
        </div>
    </body>
    );
  };
  
  export default Posts;
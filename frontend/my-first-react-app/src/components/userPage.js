import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const UserChannel = () => {
    const [user, setUser] = useState({}); // Исправлено на объект
    const location = useLocation(); 
    const user_id = location.state?.author_id || 1; // По умолчанию user_id = 1
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isFriend, setFriend] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
          try {
            const userResponse = await axios.get(API_BASE_URL+`/user/${user_id}`);
            setUser(userResponse.data.user);
            setFriend(postsResponse.data.friendship)
            const postsResponse = await axios.get(API_BASE_URL+`/posts`, {
              params: {
                userId: user_id, 
              },
            });
            setPosts(postsResponse.data.posts);

            setLoading(false); 
          } catch (error) {
            console.error('Ошибка при загрузке данных:', error);
            setError('Ошибка при загрузке данных');
            setLoading(false);
          }
        };
    
        fetchData(); 
      }, [user_id]); 
      
      const handleFriendship = async () => {
        try {
            const friendshipResponse = await axios.post(``);
            setFriend(friendshipResponse.data);
            console.lognewisFrinedStatus( ? 'Подписан' : 'Отписан');
        } catch (error) {
            console.error('Ошибка при добавлении в друзья', error);
            setError('Ошибка при добавлении в друзья');
        }
    };
    
      if (loading) {
        return <p>Загрузка...</p>;
      }
    
      if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
      }
    
      return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
          {/* Профиль пользователя */}
          <div style={{ 
            border: '1px solid #e0e0e0', 
            padding: '25px', 
            marginBottom: '30px', 
            borderRadius: '10px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            textAlign: 'center',
            backgroundColor: '#fff'
          }}>
            <img
              src={`https://i.pravatar.cc/150?u=${user.id}`}
              alt={`Аватар ${user.name}`}
              style={{ 
                width: '120px', 
                height: '120px', 
                borderRadius: '50%',
                border: '3px solid #f0f0f0',
                marginBottom: '15px'
              }}
            />
            <h2 style={{ margin: '10px 0', color: '#333' }}>{user.name}</h2>
            <div style={{ marginTop: '15px' }}>
              <button 
                onClick={handleFriendship}
                style={{ 
                  margin: '0 10px', 
                  padding: '10px 25px', 
                  backgroundColor: isFriend ? '#dc3545' : '#007bff', 
                  color: '#fff', 
                  border: 'none', 
                  borderRadius: '25px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  transition: 'all 0.3s',
                  ':hover': {
                    opacity: 0.9
                  }
                }}
              >
                {isFriend ? 'Добавить в друзья' : 'Удалить из друзей'}
              </button>
              <button 
                style={{ 
                  margin: '0 10px', 
                  padding: '10px 25px', 
                  backgroundColor: '#28a745', 
                  color: '#fff', 
                  border: 'none', 
                  borderRadius: '25px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  transition: 'all 0.3s',
                  ':hover': {
                    opacity: 0.9
                  }
                }}
              >
                Добавить в друзья
              </button>
            </div>
          </div>
      
          {/* Список постов пользователя */}
          <h1 style={{ 
            color: '#333',
            borderBottom: '2px solid #f0f0f0',
            paddingBottom: '10px',
            marginBottom: '20px'
          }}>
            Посты пользователя
          </h1>
          
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
      );
};
    
export default UserChannel;
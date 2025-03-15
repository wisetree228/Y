import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';

const UserChannel = () => {
    const [user, setUser] = useState({}); // Исправлено на объект
    const location = useLocation(); 
    const user_id = location.state?.author_id || 1; // По умолчанию user_id = 1
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isSubscribed, setIsSubscribed] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
          try {
            const userResponse = await axios.get(`https://jsonplaceholder.typicode.com/users/${user_id}`);
            setUser(userResponse.data);
            const postsResponse = await axios.get(`https://jsonplaceholder.typicode.com/posts`, {
              params: {
                userId: user_id, 
              },
            });
            setPosts(postsResponse.data);

            const subscriptionStatus = localStorage.getItem(`isSubscribed_${user_id}`) === 'true';
            setIsSubscribed(subscriptionStatus);

            setLoading(false); 
          } catch (error) {
            console.error('Ошибка при загрузке данных:', error);
            setError('Ошибка при загрузке данных');
            setLoading(false);
          }
        };
    
        fetchData(); 
      }, [user_id]); 

      const handleSubscribe = async () => {
        try {
            const newSubscriptionStatus = !isSubscribed;
            setIsSubscribed(newSubscriptionStatus);

            localStorage.setItem(`isSubscribed_${user_id}`, newSubscriptionStatus);
            console.log(newSubscriptionStatus ? 'Подписан' : 'Отписан');
        } catch (error) {
            console.error('Ошибка при подписке:', error);
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
        <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '20px', textAlign: 'center' }}>
            <img
                src={`https://i.pravatar.cc/150?u=${user.id}`} 
                alt={`Аватар ${user.name}`}
                style={{ width: '100px', height: '100px', borderRadius: '50%' }}
            />
            <h2>{user.name}</h2> {/* Имя пользователя */}
            <div>
                <button 
                    onClick={handleSubscribe}
                    style={{ 
                        margin: '5px', 
                        padding: '10px 20px', 
                        backgroundColor: isSubscribed ? '#dc3545' : '#007bff', 
                        color: '#fff', 
                        border: 'none', 
                        borderRadius: '5px' 
                    }}
                >
                    {isSubscribed ? 'Отписаться' : 'Подписаться'}
                </button>
                <button style={{ margin: '5px', padding: '10px 20px', backgroundColor: '#28a745', color: '#fff', border: 'none', borderRadius: '5px' }}>
                    Добавить в друзья
                </button>
            </div>
        </div>

        {/* Список постов пользователя */}
        <h1>Посты пользователя</h1>
        {posts.map(post => (
            <div key={post.id} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
                <h2>{post.title}</h2> {/* Заголовок поста */}
                <p>{post.body}</p> {/* Содержание поста */}
            </div>
        ))}
    </div>
);
};
    
export default UserChannel;
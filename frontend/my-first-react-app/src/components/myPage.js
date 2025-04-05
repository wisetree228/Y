import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';

const MainProfile = () => {
    const [user, setUser] = useState([])
    const [subscriptions, setSubscriptons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
          try {
            const userResponse = await axios.get(`/`, {
            });
            console.log(userResponse.data[1]);
            setUser(userResponse.data);
            const mockSubscriptions = [
              { id: 1, username: 'user1', image: 'https://i.pravatar.cc/150?u=1' },
              { id: 2, username: 'user2', image: 'https://i.pravatar.cc/150?u=2' },
              { id: 3, username: 'user3', image: 'https://i.pravatar.cc/150?u=3' },
          ];
          setSubscriptons(mockSubscriptions);
    
            setLoading(false); 
          } catch (error) {
            console.error('Ошибка при загрузке данных:', error);
            setError('Ошибка при загрузке данных');
            setLoading(false);
          }
        };
    
        fetchData(); 
      }, []); 
    
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
                alt={`Аватар ${user.username}`}
                style={{ width: '100px', height: '100px', borderRadius: '50%' }}   
            />
            <h1>{user.username}</h1> 
        </div>

        {/* Список подписок */}
        <h1>Подписки</h1>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {subscriptions.map(subscription => (
                <div key={subscription.id} style={{ border: '1px solid #ccc', padding: '10px', borderRadius: '5px', textAlign: 'center' }}>
                    <img
                        src={subscription.image}
                        alt={`Аватар ${subscription.username}`}
                        style={{ width: '50px', height: '50px', borderRadius: '50%' }}
                    />
                    <p>{subscription.username}</p>
                    <Link
                      to={{
                        pathname: `/users/${subscription.id}`,
                        state: { author_id: subscription.id }, 
                        }}
                    >
                    <button style={{ marginTop: '10px' }}>Перейти в канал</button>
                    </Link>
                </div>
            ))}
        </div>
    </div>
  );
};
    
    export default MainProfile;
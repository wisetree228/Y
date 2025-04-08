import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../config';


const Chats = () => {
    const [user, setUser] = useState({}); 
    const [friends, setFriens] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    useEffect(() => {
        const fetchData = async () => {
          try {
            const userResponse = await axios.get(API_BASE_URL+``);
            setUser(userResponse.data);
            const friendsResponse = await axios.get(API_BASE_URL+``);
            setFriens(friendsResponse.data);
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
        
    );
};
export default Chats

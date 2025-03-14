
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Posts = () => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
  
    useEffect(() => {
      axios.get('')//add ssilka
        .then(response => {
          setPosts(response.data);
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
        {posts.map(post => (
          <div key={post.id} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }//potom pomenat stil 
          }>
            <h2>{post.title}</h2>
            <p>{post.content}</p>
            <p><strong>Автор:</strong> {post.author}</p>
            <small>{new Date(post.created_at).toLocaleDateString()}</small>
            <div>
            <Link
              to={{
              pathname: `/posts/${post.id}/comments`,
              state: { post }, // Передаем данные поста
              }}
            >
              <button style={{ marginTop: '10px' }}>Комментарии</button>
            </Link>
          </div>
          </div>
        ))}
      </div>
    </body>
      
    );
  };
  
  export default Posts;
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useLocation, useNavigate } from 'react-router-dom';

const PostComments = () => {
    const { postId } = useParams(); 
    const location = useLocation(); 
    const post = location.state?.post; 
    const navigate = useNavigate();
    const [comments, setComments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        axios.get('https://jsonplaceholder.typicode.com/posts')
          .then(response => {
            setComments(response.data.post['comments']);
            setLoading(false);
          })
          .catch(error => {
            console.error('Ошибка при загрузке комментариев:', error);
            setError('Ошибка при загрузке комментариев');
            setLoading(false);
          });
        },[postId]);
    if (loading) {
        return <p>Загрузка...</p>;
        }
    if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
    }

return (
    <div>
      <button
        onClick={() => navigate(-1)} 
        style={{
          padding: '10px 20px',
          backgroundColor: '#007bff',
          color: '#fff',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          marginBottom: '20px',
        }}
      >
        Назад
      </button>

        {post && (
        <div style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
            <h2>{post.author_username}</h2>
            <p>{post.text}</p>
            <p><strong>Автор:</strong> {post.author}</p>
            <small>{new Date(post.created_at).toLocaleDateString()}</small>
        </div>
        )}
    
        <h1>Комментарии к посту #{postId}</h1>
        {comments.map(comment => (
        <div key={comment.id} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
            <p><strong>{comment.name}</strong> ({comment.email})</p>
            <p>{comment.body}</p>
        </div>
        ))}
    </div>
    );
};
    
export default PostComments;
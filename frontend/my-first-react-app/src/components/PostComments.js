import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const PostComments = () => {
    const { postId } = useParams(); 
    const location = useLocation(); 
    const post = location.state?.post; 
  
    const [comments, setComments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        axios.get('')//add ssilka
          .then(response => {
            setComments(response.data);
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
        {post && (
        <div style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
            <h2>{post.title}</h2>
            <p>{post.body}</p>
            <p><strong>Автор:</strong> {post.author}</p>
            <small>{new Date(post.created_at).toLocaleDateString()}</small>
        </div>
        )}
    
        {/* Отображаем комментарии */}
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
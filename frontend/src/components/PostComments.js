import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';

const PostComments = () => {
    const { postId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const [post, setPost] = useState(location.state?.post || null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [newComment, setNewComment] = useState('');
    const [images, setImages] = useState([]);
    const [currentUserId, setCurrentUserId] = useState(null);

    useEffect(() => {
        const fetchPost = async () => {
            try {
                await CheckAuthorization();
                const response = await axios.get(`${API_BASE_URL}/posts/${postId}`, {
                    withCredentials: true
                });
                const postData = response.data.post;
                setPost(postData);

                if (postData.images_id && postData.images_id.length > 0) {
                    const imageUrls = postData.images_id.map(id =>
                        `${API_BASE_URL}/posts/image/${id}`
                    );
                    setImages(imageUrls);
                }

                setLoading(false);
            } catch (error) {
                alert('Ошибка на стороне сервера, попробуйте ещё раз!')
            }
        };

        const fetchId = async () => {
            try {
                await CheckAuthorization();
                const response = await axios.get(`${API_BASE_URL}/my_id`, {
                    withCredentials: true
                });
                const Id = response.data.id;
                setCurrentUserId(Id);

                
                }

                
             catch (error) {
                alert('Ошибка на стороне сервера, попробуйте ещё раз!')
            }
        };

        fetchPost();
        fetchId();
        const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      /* Основные стили */
body {
  background-color: #396687;
  color: #e0e0e0;
  font-family: Arial, sans-serif;
  padding: 20px;
  line-height: 1.5;
}

/* Контейнер */
div[style*="max-width: '800px'"] {
  max-width: 700px;
  margin: 0 auto;
}

/* Карточка поста */
div[style*="border: '1px solid #ccc'"] {
  background-color: #2d4d66;
  border: 1px solid #3c91cf !important;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  color: #fff;
}

/* Заголовки */
h1, h2, h3 {
  color: #fff;
  margin: 15px 0 10px;
}

/* Текст */
p {
  margin: 10px 0;
  color: #e0e0e0;
}

/* Кнопки */
button {
  background-color: #3c91cf;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin: 5px 0;
  font-size: 14px;
}

button:hover {
  background-color: #2e7ab3;
}

/* Специальные кнопки */
button[style*="background: none"] {
  background: transparent !important;
  padding: 0 !important;
  color: #ff6b6b !important;
}

button[style*="background-color: '#f44336'"] {
  background-color: #e53935 !important;
}

/* Форма комментария */
textarea {
  width: 100%;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #3c91cf;
  background-color: #2d4d66;
  color: white;
  min-height: 100px;
  margin-bottom: 10px;
}

textarea::placeholder {
  color: #aaa;
}

/* Комментарии */
div[style*="border: '1px solid #eee'"] {
  background-color: #2d4d66;
  border: 1px solid #3c91cf !important;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  color: #fff;
}

/* Изображения */
img {
  max-width: 100%;
  border-radius: 6px;
  border: 1px solid #3c91cf;
}

/* Ссылки */
a {
  color: #a8d4ff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Варианты голосования */
button[style*="width: '100%'"] {
  background-color: #2d4d66 !important;
  color: white !important;
  border: 1px solid #3c91cf !important;
  margin-bottom: 8px;
}

/* Полоса прогресса голосования */
div[style*="height: '10px'"] {
  background-color: #3c91cf !important;
}

/* Мелкий текст */
small {
  color: #aaa;
}

/* Предупреждения */
span[style*="color: '#666'"] {
  color: #aaa !important;
}
    `;
    
    // Добавляем в head документа
    document.head.appendChild(styleElement);
    return () => {
        document.head.removeChild(styleElement);
      };

    }, [postId]);

    const handleLike = async () => {
        try {
            const response = await axios.post(`${API_BASE_URL}/post/${postId}/like`, {}, {
                withCredentials: true
            });
            setPost(prev => ({
                ...prev,
                liked_status: response.data.status === 'liked',
                likes_count: response.data.likes_count
            }));
        } catch (error) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
    };

    const handleVote = async (variantId) => {
        try {
            await axios.post(`${API_BASE_URL}/vote/${variantId}`, {}, {
                withCredentials: true
            });

            const response = await axios.get(`${API_BASE_URL}/posts/${postId}`, {
                withCredentials: true
            });
            setPost(response.data.post);
        } catch (error) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
    };

    const handleCommentSubmit = async (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;

        try {
            await axios.post(`${API_BASE_URL}/post/${postId}/comment`, {
                text: newComment
            }, {
                withCredentials: true
            });

            const response = await axios.get(`${API_BASE_URL}/posts/${postId}`, {
                withCredentials: true
            });
            setPost(response.data.post);
            setNewComment('');
        } catch (error) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
    };

    const handleDeleteVote = async (postId) => {
        try {
            await axios.delete(
                `${API_BASE_URL}/vote/${postId}`,
                { withCredentials: true }
            );
        } catch (err) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
        const response = await axios.get(`${API_BASE_URL}/posts/${postId}`, {
            withCredentials: true
        });
        const postData = response.data.post;
        setPost(postData);
    };


    const handleDeleteComment = async (commentId) => {
        try {
            await axios.delete(`${API_BASE_URL}/comment/${commentId}`, {
                withCredentials: true
            });

            // Обновляем данные поста
            const response = await axios.get(`${API_BASE_URL}/posts/${postId}`, {
                withCredentials: true
            });
            setPost(response.data.post);
        } catch (error) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
    };


    if (loading) {
        return <p>Загрузка...</p>;
    }

    if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
    }

    if (!post) {
        return <p>Пост не найден</p>;
    }

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
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

            <div style={{
                border: '1px solid #ccc',
                padding: '20px',
                marginBottom: '20px',
                borderRadius: '8px',
                backgroundColor: '#1b99b5'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                    <h2 style={{ margin: 0 }}>{post.author_username}</h2>
                    <span style={{
                        marginLeft: '10px',
                        fontSize: '14px',
                        color: '#666'
                    }}>
                        {new Date(post.created_at).toLocaleString()}
                    </span>
                </div>

                <p style={{ fontSize: '16px', marginBottom: '15px' }}>{post.text}</p>

                {images.length > 0 && (
                    <div style={{ marginBottom: '15px' }}>
                        {images.map((imgUrl, index) => (
                            <img
                                key={index}
                                src={imgUrl}
                                alt={`Прикрепленное изображение ${index + 1}`}
                                style={{
                                    maxWidth: '100%',
                                    maxHeight: '400px',
                                    marginBottom: '10px',
                                    display: 'block'
                                }}
                                onError={(e) => {
                                    e.target.style.display = 'none';
                                }}
                            />
                        ))}
                    </div>
                )}

                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                    <button
                        onClick={handleLike}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: post.liked_status ? '#ff0000' : '#666',
                            fontSize: '20px',
                            marginRight: '5px'
                        }}
                    >
                        {post.liked_status ? '❤️' : '🤍'}
                    </button>
                    <span>{post.likes_count}</span>
                </div>

                {post.voting_variants && post.voting_variants.length > 0 && (
                    <div style={{ marginBottom: '20px' }}>
                        <h3>Голосование:</h3>
                        {post.voting_variants.map(variant => (
                            <div key={variant.id} style={{ marginBottom: '10px' }}>
                                <button
                                    onClick={() => handleVote(variant.id)}
                                    disabled={variant.user_voted}
                                    style={{
                                        width: '100%',
                                        padding: '10px',
                                        textAlign: 'left',
                                        border: `1px solid ${variant.user_voted ? '#4CAF50' : '#ddd'}`,
                                        borderRadius: '4px',
                                        backgroundColor: variant.user_voted ? '#e8f5e9' : '#166e82',
                                        cursor: variant.user_voted ? 'default' : 'pointer',
                                        opacity: variant.user_voted ? 0.8 : 1
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span>{variant.text}</span>
                                        <span>{variant.percent}% ({variant.votes?.length || 0})</span>
                                    </div>
                                    <div
                                        style={{
                                            height: '10px',
                                            width: `${variant.percent}%`,
                                            backgroundColor: variant.user_voted ? '#4CAF50' : '#81c784',
                                            marginTop: '5px',
                                            borderRadius: '5px',
                                            transition: 'width 0.3s ease'
                                        }}
                                    />
                                </button>
                                <Link
                                            to={`/voted_users/${variant.id}`}
                                            style={{
                                                textDecoration: 'none',
                                                color: 'blue',
                                                marginLeft: '10px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            Кто голосовал?
                                        </Link>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <button
                onClick={() => handleDeleteVote(postId)}
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

            <div style={{ marginBottom: '30px' }}>
                <h3>Добавить комментарий:</h3>
                <form onSubmit={handleCommentSubmit}>
                    <textarea
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        style={{
                            width: '100%',
                            minHeight: '100px',
                            padding: '10px',
                            marginBottom: '10px',
                            border: '1px solid #ccc',
                            borderRadius: '4px'
                        }}
                        placeholder="Напишите ваш комментарий..."
                    />
                    <button
                        type="submit"
                        style={{
                            padding: '10px 20px',
                            backgroundColor: '#007bff',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer'
                        }}
                    >
                        Отправить
                    </button>
                </form>
            </div>

            <div>
                <h3>Комментарии ({post.comments_count || 0}):</h3>
                {post.comments && post.comments.length === 0 ? (
                    <p>Пока нет комментариев</p>
                ) : (
                    post.comments?.map(comment => (
                        <div
                            key={comment.id}
                            style={{
                                border: '1px solid #eee',
                                padding: '15px',
                                marginBottom: '15px',
                                borderRadius: '8px',
                                backgroundColor: '#1b99b5'
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>

                                <Link
                                    to={`/users/${comment.author_id}`}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        marginBottom: '10px',
                                        textDecoration: 'none',
                                        color: 'inherit'
                                    }}
                                >
                                    <strong style={{ marginRight: '10px' }}>{comment.author_username}</strong>
                                    <small style={{ color: '#666' }}>
                                        {new Date(comment.created_at).toLocaleString()}
                                    </small>
                                </Link>
                            </div>
                            <p style={{ margin: 0 }}>{comment.text}</p>
                            {currentUserId === comment.author_id && (
                                <button onClick={() => handleDeleteComment(comment.id)}>
                                    Удалить
                                </button>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default PostComments;
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';

const EditPost = () => {
    const [postText, setPostText] = useState('');
    const [options, setOptions] = useState([]);
    const [originalOptions, setOriginalOptions] = useState([]);
    const [images, setImages] = useState([]);
    const [newImage, setNewImage] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const { postId } = useParams();

    const fetchPost = async () => {
        try {
            await CheckAuthorization();
            const Idresponse = await axios.get(`${API_BASE_URL}/my_id`, {
                withCredentials: true
            });
            const response = await axios.get(`${API_BASE_URL}/posts/${postId}`, {
                withCredentials: true
            });
            const post = response.data.post;
            if (post.author_id!==Idresponse.data.id){
                navigate('/posts')
            }
            
            setPostText(post.text);
            
            if (post.voting_variants && post.voting_variants.length > 0) {
                const variantTexts = post.voting_variants.map(v => v.text);
                setOptions([...variantTexts]);
                setOriginalOptions([...variantTexts]);
            }
            
            if (post.images_id && post.images_id.length > 0) {
                const imagesData = await Promise.all(
                    post.images_id.map(id => 
                        axios.get(`${API_BASE_URL}/posts/image/${id}`, {
                            responseType: 'blob',
                            withCredentials: true
                        }).then(res => ({
                            id,
                            url: URL.createObjectURL(res.data)
                        }))
                ));
                setImages(imagesData);
            }
            
            setLoading(false);
        } catch (err) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
    };

    useEffect(() => {
        fetchPost();
    }, [postId]);

    const handlePostTextChange = (e) => {
        setPostText(e.target.value);
    };

    const handleOptionChange = (index, e) => {
        const newOptions = [...options];
        newOptions[index] = e.target.value;
        setOptions(newOptions);
    };

    const addOption = () => {
        setOptions([...options, '']);
    };

    const removeOption = (index) => {
        const newOptions = options.filter((_, i) => i !== index);
        setOptions(newOptions);
    };

    const handleImageChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setNewImage(e.target.files[0]);
        }
    };

    const handleDeleteImage = async (imageId) => {
        if (!window.confirm('Удалить это изображение?')) return;
        
        try {
            await axios.delete(`${API_BASE_URL}/posts/image/${imageId}`, {
                withCredentials: true
            });
            setImages(images.filter(img => img.id !== imageId));
        } catch (err) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            // Подготовка данных для отправки
            const postData = {
                text: postText,
                options: JSON.stringify(options) === JSON.stringify(originalOptions) 
                    ? null 
                    : options.length > 0 ? options : []
            };

            // Отправка изменений поста
            await axios.put(`${API_BASE_URL}/post/${postId}`, postData, {
                withCredentials: true
            });

            // Добавление нового изображения, если есть
            if (newImage) {
                const formData = new FormData();
                formData.append('uploaded_file', newImage);
                
                await axios.post(`${API_BASE_URL}/posts/${postId}/media`, formData, {
                    withCredentials: true,
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });
            }

            navigate(`/posts/${postId}`);
        } catch (err) {
            alert('Ошибка на стороне сервера, попробуйте ещё раз!')
        }
    };

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div style={{ color: 'red' }}>{error}</div>;

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
            <h1>Редактировать пост</h1>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '8px' }}>Текст поста:</label>
                    <textarea
                        value={postText}
                        onChange={handlePostTextChange}
                        required
                        minLength={3}
                        maxLength={10000}
                        style={{ width: '100%', minHeight: '100px', padding: '8px' }}
                    />
                </div>

                {originalOptions.length > 0 && (
                    <div style={{ 
                        marginBottom: '20px',
                        padding: '15px',
                        backgroundColor: '#fff3cd',
                        borderRadius: '4px'
                    }}>
                        <strong>Внимание!</strong> Если вы измените варианты голосования, 
                        все текущие голоса будут сброшены.
                    </div>
                )}

                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '8px' }}>Варианты голосования:</label>
                    {options.map((option, index) => (
                        <div key={index} style={{ display: 'flex', marginBottom: '8px' }}>
                            <input
                                type="text"
                                value={option}
                                onChange={(e) => handleOptionChange(index, e)}
                                minLength={3}
                                maxLength={100}
                                style={{ flex: 1, padding: '8px' }}
                            />
                            <button 
                                type="button" 
                                onClick={() => removeOption(index)}
                                style={{ 
                                    marginLeft: '8px',
                                    padding: '8px 12px',
                                    backgroundColor: '#dc3545',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer'
                                }}
                            >
                                Удалить
                            </button>
                        </div>
                    ))}
                    <button 
                        type="button" 
                        onClick={addOption}
                        style={{ 
                            padding: '8px 12px',
                            backgroundColor: '#28a745',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        Добавить вариант
                    </button>
                </div>

                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '8px' }}>Изображения:</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
                        {images.map(img => (
                            <div key={img.id} style={{ position: 'relative' }}>
                                <img 
                                    src={img.url} 
                                    alt="Изображение поста" 
                                    style={{ 
                                        width: '150px', 
                                        height: '150px',
                                        objectFit: 'cover',
                                        borderRadius: '4px'
                                    }} 
                                />
                                <button
                                    type="button"
                                    onClick={() => handleDeleteImage(img.id)}
                                    style={{
                                        position: 'absolute',
                                        top: '5px',
                                        right: '5px',
                                        backgroundColor: 'rgba(220, 53, 69, 0.8)',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '50%',
                                        width: '25px',
                                        height: '25px',
                                        cursor: 'pointer'
                                    }}
                                >
                                    ×
                                </button>
                            </div>
                        ))}
                    </div>
                    <input 
                        type="file" 
                        onChange={handleImageChange}
                        accept="image/*"
                    />
                </div>

                <button 
                    type="submit"
                    style={{ 
                        padding: '10px 20px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginRight: '10px'
                    }}
                >
                    Сохранить изменения
                </button>
                <Link 
                    to={`/home`}
                    style={{ 
                        padding: '10px 20px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        textDecoration: 'none',
                        borderRadius: '4px',
                        display: 'inline-block'
                    }}
                >
                    Отмена
                </Link>
            </form>
        </div>
    );
};

export default EditPost;
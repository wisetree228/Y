import React, { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const CreatePost = () => {
    const [postText, setPostText] = useState('');
    const [options, setOptions] = useState(['']); // Начальное состояние с одним пустым полем
    const navigate = useNavigate();

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

    const handleSubmit = async (e) => {
        e.preventDefault();
        const postData = {
            text: postText,
            options: options.length > 0 ? options : undefined
        };

        try {
            await axios.post(`${API_BASE_URL}/post`, postData, { withCredentials: true });
            navigate('/'); // Перенаправление на главную страницу после успешной публикации
        } catch (error) {
            console.error('Ошибка при создании поста:', error);
        }
    };

    return (
        <div>
            <h1>Создать пост</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Текст поста:</label>
                    <textarea
                        value={postText}
                        onChange={handlePostTextChange}
                        required
                        minLength={3}
                        maxLength={10000}
                    />
                </div>
                <div>
                    <label>Варианты голосования:</label>
                    {options.map((option, index) => (
                        <div key={index}>
                            <input
                                type="text"
                                value={option}
                                onChange={(e) => handleOptionChange(index, e)}
                                minLength={3}
                                maxLength={100}
                            />
                            <button type="button" onClick={() => removeOption(index)}>Удалить</button>
                        </div>
                    ))}
                    <button type="button" onClick={addOption}>Добавить вариант</button>
                </div>
                <button type="submit">Опубликовать пост</button>
            </form>
            <Link to="/">Вернуться на главную</Link>
        </div>
    );
};

export default CreatePost;

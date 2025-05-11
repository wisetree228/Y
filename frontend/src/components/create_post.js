import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';

const CreatePost = () => {
  const [postText, setPostText] = useState('');
  const [options, setOptions] = useState(['']); // Начальное состояние с одним пустым полем
  const navigate = useNavigate();

  useEffect(() => {
    CheckAuthorization();
    const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      body {
  background-color: #396687;
  color: white;
  font-family: Arial, sans-serif;
  padding: 20px;
  text-align: center;
}

div {
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  color: white;
  margin-bottom: 30px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

textarea, input[type="text"] {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #3c91cf;
  border-radius: 4px;
  background-color: rgba(255,255,255,0.1);
  color: white;
}

textarea {
  min-height: 120px;
  resize: vertical;
}

button {
  background-color: #3c91cf;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  margin: 5px;
}

button[type="button"] {
  background-color: #e53935;
}

a {
  display: inline-block;
  margin-top: 20px;
  color: #a8d4ff;
  text-decoration: none;
}
  .inputtext{
     width: 100%
  }
    `;

    // Добавляем в head документа
    document.head.appendChild(styleElement);
    return () => {
      document.head.removeChild(styleElement);
    };

  }, []);

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
      alert('Ошибка на стороне сервера, попробуйте ещё раз! Возможные причины ошибки: некорректный формат данных')
    }
  };

  return (
    <div>
      <h1>Создать пост</h1>
      <form onSubmit={handleSubmit}>
        <div className='inputtext'>
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
          <button type="button" style={{ backgroundColor: '#4db5ff' }} onClick={addOption}>Добавить вариант</button>
        </div>
        <button type="submit">Опубликовать пост</button>
      </form>
      <Link to="/">Вернуться на главную</Link>
    </div>
  );
};

export default CreatePost;

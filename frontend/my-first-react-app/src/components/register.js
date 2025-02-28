import React from 'react';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [Confirmation, confirmPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const handleSubmit = async (e) => {
        e.preventDefault();
    
        // Проверка совпадения паролей
        if (password !== confirmation) {
          setError('Пароли не совпадают');
          return;
        }
    
        try {
          // Отправляем данные на сервер
          const response = await fetch('https://example.com/api/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }), // Преобразуем данные в JSON
          });
    
          // Проверяем статус ответа
          if (!response.ok) {
            throw new Error('Ошибка при регистрации');
          }
    
          // Парсим JSON-ответ
          const data = await response.json();
    
          // Если регистрация успешна
          if (data.success) {
            console.log('Регистрация успешна:', data);
            navigate('/posts');//поменять на название нужной страницы 
          } else {
            setError(data.message || 'Ошибка при регистрации'); 
          }
        } catch (err) {
          console.error('Ошибка при регистрации:', err);
          setError('Произошла ошибка при регистрации');
        }
      };
  return (
    <div>
      <h1>Страница регистрации</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>} {/* Отображение ошибки */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Логин"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Подтверждение пароля"
          value={confirmation}
          onChange={(e) => setConfirmation(e.target.value)}
          required
        />
        <button type="submit">Зарегистрироваться</button>
      </form>
    </div>
  );
};

export default Register;
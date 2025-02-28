const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        // Отправляем данные на сервер
        const response = await fetch('https://example.com/api/login', {
            //указать ссылку куда отправлять
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }), 
        });
  
        if (!response.ok) {
          throw new Error('Ошибка при авторизации');
        }
  
        const data = await response.json();
  
        if (data.success) {
          navigate('/dashboard'); //поменяит ссылку на нужную страницу
        } else {
          setError('Неверный логин или пароль');
        }
      } catch (err) {
        console.error('Ошибка при авторизации:', err);
        setError('Произошла ошибка при авторизации');
      }
    };
  
    return (
      <div>
        <h1>Страница авторизации</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Логин"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Войти</button>
        </form>
      </div>
    );
  };
  
  export default Login;
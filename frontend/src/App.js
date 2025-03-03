import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [data, setData] = useState([]);
  const base_url = 'http://localhost:8000';

  useEffect(() => {
    fetch(base_url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Сетевая ошибка');
        }
        return response.json();
      })
      .then(json => setData(json))
      .catch(error => {
        console.error('Ошибка:', error);
        setData({ ok: 'no' });  // Устанавливаем данные в случае ошибки
      });
  }, []);

  return (
    <div className="App">
      <h1>Привет, мир!</h1>
      <p>
        Это моё первое React-приложение. Статус запроса: {data.status || 'загрузка...'}
      </p>
      <p>
        Если в конце верхней строки вы видите "ok", значит запрос к API сработал. Если "no", то нет.
      </p>
    </div>
  );
}

export default App;
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import CheckAuthorization from '../utils';
import './css/Posts.css';

const Posts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const limit = 20;
  const navigate = useNavigate();
  
    useEffect(() => {
      CheckAuthorization();
      fetchPosts();
    }, []);



    const fetchPosts = async (loadMore = false) => {
      const currentSkip = loadMore ? skip : 0;
      
      try {
        loadMore ? setLoadingMore(true) : setLoading(true);
        
        const response = await axios.get(
          `${API_BASE_URL}/posts?limit=${limit}&skip=${currentSkip}`, 
          { withCredentials: true }
        );

        const newPosts = response.data.posts || [];
        
        if (loadMore) {
          setPosts(prevPosts => [...prevPosts, ...newPosts]);
        } else {
          setPosts(newPosts);
        }

        setHasMore(newPosts.length === limit);
        setSkip(currentSkip + newPosts.length);
      } catch (err) {
        console.error('Ошибка при загрузке постов:', err);
        setError('Ошибка при загрузке постов');
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    };

    const loadMorePosts = () => {
      if (hasMore && !loadingMore) {
        fetchPosts(true);
      }
    };

    const fetchSinglePost = async (postId) => {
      try {
        const response = await axios.get(`${API_BASE_URL}/posts/${postId}`, { 
          withCredentials: true 
        });
        return response.data.post;
      } catch (err) {
        console.error('Ошибка при загрузке поста:', err);
        return null;
      }
    };

    const handleLike = async (postId) => {
      try {
        const response = await axios.post(
          `${API_BASE_URL}/post/${postId}/like`,
          {},
          { withCredentials: true }
        );
        
        setPosts(posts.map(post => {
          if (post.id === postId) {
            return {
              ...post,
              likes_count: response.data.likes_count,
              liked_status: response.data.status === 'liked'
            };
          }
          return post;
        }));
      } catch (err) {
        alert('Ошибка на стороне сервера, попробуйте ещё раз!')
      }
    };

    const handleVote = async (variantId, postId) => {
      try {
        await axios.post(
          `${API_BASE_URL}/vote/${variantId}`,
          {},
          { withCredentials: true }
        );

        await new Promise(resolve => setTimeout(resolve, 250)); //Небольшая задержка чтобы бэкенд успел обработать голосовалку
        const updatedPost = await fetchSinglePost(postId);
        if (updatedPost) {
          setPosts(posts.map(post => 
            post.id === postId ? updatedPost : post
          ));
        }
      } catch (err) {
        alert('Ошибка при голосовании, попробуйте ещё раз!');
      }
    };

    const handleDeleteVote = async (postId) => {
      try {
        await axios.delete(
          `${API_BASE_URL}/vote/${postId}`,
          { withCredentials: true }
        );
        
        // Получаем обновленные данные только для этого поста
        const updatedPost = await fetchSinglePost(postId);
        if (updatedPost) {
          setPosts(posts.map(post => 
            post.id === postId ? updatedPost : post
          ));
        }
      } catch (err) {
        alert('Ошибка при удалении голоса, попробуйте ещё раз!');
      }
    };
  
    if (loading) {
      return <p>Загрузка...</p>;
    }
    if (error) {
      return <p style={{ color: 'red' }}>{error}</p>;
    }

    return (
      <div className="posts-container">
        <header className="posts-header">
          <h1 className="posts-title">Посты</h1>
          <div className="posts-header-actions">
            <Link to="/home" className="posts-nav-button">
              Профиль
            </Link>
            <Link to="/create-post" className="posts-create-button">
              Создать пост
            </Link>
          </div>
        </header>
        
        <main className="posts-list">
          {posts.map(post => (
            <article key={post.id} className="post-card">
              <div className="post-header">
                <img
                  src={`${API_BASE_URL}/user/${post.author_id}/avatar?t=${Date.now()}`}
                  alt={`Аватар ${post.author_username}`}
                  className="post-avatar"
                />
                <div className="post-author">
                  <h3 className="post-username">{post.author_username}</h3>
                  <time className="post-date">{new Date(post.created_at).toLocaleString()}</time>
                </div>
              </div>
              
              <div className="post-content">
                <p className="post-text">{post.text}</p>
                
                {post.images_id?.length > 0 && (
                  <div className="post-images">
                    {post.images_id.map(imageId => (
                      <img
                        key={imageId}
                        src={`${API_BASE_URL}/posts/image/${imageId}?t=${Date.now()}`}
                        alt="Изображение поста"
                        className="post-image"
                      />
                    ))}
                  </div>
                )}
                
                {post.voting_variants?.length > 0 && (
                  <div className="post-voting">
                    {post.voting_variants.map(variant => (
                      <div 
                        key={variant.id}
                        onClick={() => handleVote(variant.id, post.id)}
                        className={`vote-option ${variant.selected ? 'selected' : ''}`}
                      >
                        {variant.text} {variant.percent && <span className="vote-percent">({variant.percent}%)</span>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="post-footer">
                <div className="post-actions">
                  <button 
                    onClick={() => handleLike(post.id)}
                    className={`like-button ${post.liked_status ? 'liked' : ''}`}
                  >
                    ❤️ {post.likes_count} лайков
                  </button>
                  
                  <Link to={`/posts/${post.id}`} className="comments-link">
                    💬 {post.comments_count} комментариев
                  </Link>
                </div>
                
                <div className="post-links">
                  <Link to={`/users/${post.author_id}`} className="post-link">
                    Перейти в канал
                  </Link>
                  <Link to={`/posts/${post.id}`} className="post-link">
                    Комментарии
                  </Link>
                </div>
                
                {post.voting_variants?.length > 0 && (
                  <button 
                    onClick={() => handleDeleteVote(post.id)}
                    className="delete-vote-button"
                  >
                    Удалить мой голос
                  </button>
                )}
              </div>
            </article>
          ))}
          
          {hasMore && (
            <div className="load-more-container">
              <button 
                onClick={loadMorePosts}
                disabled={loadingMore}
                className="load-more-button"
              >
                {loadingMore ? 'Загрузка...' : 'Загрузить ещё'}
              </button>
            </div>
          )}
          
          {!hasMore && posts.length > 0 && (
            <p className="end-of-list">Вы достигли конца списка</p>
          )}
        </main>
      </div>
    );
};

export default Posts;
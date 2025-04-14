import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/home';
import Login from './components/login';
import Register from './components/register';
import Posts from './components/post';
import PostComments from './components/PostComments';
import UserChannel from './components/userPage';
import MainProfile from './components/myPage';
import CreatePost from './components/create_post';
import Chat from './components/oneChat';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/posts" element={<Posts />} />
        <Route path="/posts/:postId" element={<PostComments />} />
        <Route path="/users/:authorId" element={<UserChannel />} />
        <Route path="/home" element={<MainProfile />} />
        <Route path="/create-post" element={<CreatePost />} />
        <Route path="/chat/:userId" element={<Chat />} />
      </Routes>
    </Router>
  );
};

export default App;
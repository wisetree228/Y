// Sample post data
const samplePosts = [
    {
        id: 1,
        author: 'Александр',
        date: '15 февраля 2025',
        content: 'Будущее уже здесь. Технологии меняют мир быстрее, чем мы успеваем это осознать.',
        likes: 42,
        comments: 8
    },
    {
        id: 2,
        author: 'Мария',
        date: '15 февраля 2025',
        content: 'Искусственный интеллект становится неотъемлемой частью нашей жизни. Как вы относитесь к этому?',
        likes: 127,
        comments: 23
    },
    {
        id: 3,
        author: 'Дмитрий',
        date: '15 февраля 2025',
        content: 'Виртуальная реальность открывает новые горизонты для творчества и самовыражения.',
        likes: 85,
        comments: 15
    }
];

// Function to create a post element
function createPostElement(post) {
    const postElement = document.createElement('div');
    postElement.className = 'post';
    postElement.innerHTML = `
        <div class="post-header">
            <span class="post-author">${post.author}</span>
            <span class="post-date">${post.date}</span>
        </div>
        <div class="post-content">
            ${post.content}
        </div>
        <div class="post-actions">
            <button class="action-btn like-btn" data-post-id="${post.id}">
                <span class="action-icon">♥</span>
                <span class="action-count">${post.likes}</span>
            </button>
            <button class="action-btn comment-btn" data-post-id="${post.id}">
                <span class="action-icon">💬</span>
                <span class="action-count">${post.comments}</span>
            </button>
        </div>
    `;
    return postElement;
}

// Function to initialize the feed
function initializeFeed() {
    const feed = document.querySelector('.feed');
    const createPost = document.querySelector('.create-post');
    
    // Add sample posts after the create-post element
    samplePosts.forEach(post => {
        feed.appendChild(createPostElement(post));
    });
}

// Initialize the feed when the page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeFeed();

    // Add event listeners for buttons
    document.querySelector('.channels-btn').addEventListener('click', () => {
        console.log('Channels button clicked');
    });

    document.querySelector('.profile-btn').addEventListener('click', () => {
        console.log('Profile button clicked');
    });

    // Add event listener for search
    const searchInput = document.querySelector('.search-input');
    searchInput.addEventListener('input', (e) => {
        console.log('Searching for:', e.target.value);
    });

    // Add event listener for post creation
    const postInput = document.querySelector('.post-input');
    const postBtn = document.querySelector('.post-btn');
    
    postBtn.addEventListener('click', () => {
        const content = postInput.value.trim();
        if (content) {
            const newPost = {
                id: samplePosts.length + 1,
                author: 'Вы',
                date: new Date().toLocaleDateString('ru-RU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                }),
                content: content,
                likes: 0,
                comments: 0
            };
            
            const feed = document.querySelector('.feed');
            feed.insertBefore(createPostElement(newPost), feed.children[1]);
            postInput.value = '';
        }
    });

    // Add event listeners for post actions
    document.addEventListener('click', (e) => {
        if (e.target.closest('.like-btn')) {
            const btn = e.target.closest('.like-btn');
            const countElement = btn.querySelector('.action-count');
            let count = parseInt(countElement.textContent);
            countElement.textContent = count + 1;
            btn.style.color = '#4a90e2';
        }
        if (e.target.closest('.comment-btn')) {
            const postId = e.target.closest('.comment-btn').dataset.postId;
            console.log('Comment clicked for post:', postId);
        }
    });
});
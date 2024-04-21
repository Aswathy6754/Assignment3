// static/feed-scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const tweetContainer = document.getElementById('tweet-container');

    // Simulated tweet data
    const tweets = [
        { username: 'user1', message: 'This is a text tweet.' },
        { username: 'user2', message: 'This is an image tweet.', mediaType: 'image', mediaUrl: 'image_url_here' },
        { username: 'user3', message: 'This is a video tweet.', mediaType: 'video', mediaUrl: 'video_url_here' },
        { username: 'user1', message: 'This is a text tweet.' },
        { username: 'user2', message: 'This is an image tweet.', mediaType: 'image', mediaUrl: 'image_url_here' },
        { username: 'user3', message: 'This is a video tweet.', mediaType: 'video', mediaUrl: 'video_url_here' },
        { username: 'user1', message: 'This is a text tweet.' },
        { username: 'user2', message: 'This is an image tweet.', mediaType: 'image', mediaUrl: 'image_url_here' },
        { username: 'user3', message: 'This is a video tweet.', mediaType: 'video', mediaUrl: 'video_url_here' },
    ];

    // Function to render tweets
    function renderTweets(tweets) {
        tweets.forEach(tweet => {
            const tweetElement = document.createElement('div');
            tweetElement.classList.add('tweet');

            tweetElement.innerHTML = `
                <div class="avatar"></div>
                <div class="content">
                    <div class="user-info">
                        <span class="username">${tweet.username}</span>
                        <span class="timestamp">10m ago</span>
                    </div>
                    <div class="message">${tweet.message}</div>
                    ${tweet.mediaType === 'image' ? `<div class="media"><img src="${tweet.mediaUrl}" alt="Image"></div>` : ''}
                    ${tweet.mediaType === 'video' ? `<div class="media"><video controls><source src="${tweet.mediaUrl}" type="video/mp4"></video></div>` : ''}
                    <div class="actions">
                        <span class="like-button">&#10084;</span>
                    </div>
                </div>
            `;

            const likeButton = tweetElement.querySelector('.like-button');
            likeButton.addEventListener('click', () => {
                likeButton.style.color = '#ff6b6b'; // Change color to red when liked
            });

            tweetContainer.appendChild(tweetElement);
        });
    }

    // Render tweets
    renderTweets(tweets);
});

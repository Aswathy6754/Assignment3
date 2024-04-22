

window.addEventListener('load',()=>{
    function getDataCookie(cookieName) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.startsWith(cookieName + '=')) {
            const token = cookie.substring(cookieName.length + 1);
            return token;
          }
        }
        return null;
      }

      function decodeJWT(string){
        var arr = string.split('.');
         return { header: JSON.parse(atob(arr[0])), payload: JSON.parse(atob(arr[1])), secret: arr[2] }
      }

      const token = getDataCookie('token');

      if (token) {
        const userCredentials = decodeJWT(token)
        document.cookie = "email=" + userCredentials.payload.email + ';path=/;Samesite=Strict';
        document.cookie = "uid=" + userCredentials.payload.user_id + ';path=/;Samesite=Strict';
      }

})


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


async function handleSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    const response = await fetch('/post/tweets/', {
        method: 'POST',
        body: formData,
        headers: {
            'user_id': 'user_id_here' // Replace with the actual user ID
        }
    });

    if (response.ok) {
        const data = await response.json();
        console.log('Tweet created successfully:', data);
        event.target.reset();
    } else {
        console.error('Failed to create tweet:', response.statusText);
    }
}

document.getElementById('tweetForm').addEventListener('submit', handleSubmit);
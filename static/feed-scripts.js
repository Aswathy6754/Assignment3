

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
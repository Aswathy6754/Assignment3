const toggleFollow = async (userId) => {
    try {
        const response = await fetch(`/user/follow/${userId}`, {
            method: "POST"
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "Failed to toggle follow/unfollow");
        }
        const responseData = await response.json();
        console.log(responseData.message); // Success message
        const followButton = document.getElementById(`follow_${responseData.user_id}`);
        if(responseData.action === 'followed'){
            followButton.textContent = "Unfollow";
        }else{
            followButton.textContent = "follow";
        }
        // You can update the UI or perform other actions based on the response
    } catch (error) {
        console.error(error);
        // Handle errors (e.g., display error message to the user)
    }
};


window.addEventListener('load',()=>{

    let searchButton =document.getElementById('search')
    let username =document.getElementById('search-input')
  

    if(searchButton){
        
        searchButton.addEventListener('click',()=>{
            if(username.value.trim() !==""){
                window.location =`/user/?username=${username.value}`
            }
            
        })
    }
})
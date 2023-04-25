# Backend API Routes for My Fitness Odyssey

# # Add User
    this route allows a user to be created storing their Id, username, password, 
    and creating a foreign key for a users blogs

  EndPoint: '/user/add'
  Method: 'POST'

  Expected JSON Response:

  {
    'id': INT
    'username': STR
    'password': STR
    'blogs': []
  }

# # Verify User
    this route allows a user to verify themselves on the login page

  EndPoint: '/user/verify'
  Method: 'POST'

  Expected JSON Response:

  {
    'access_token': STR
  }

# # LogOut User
    this route allows a user to be log themselves out and delete thier token, thus ending their session

  EndPoint: '/user/logOut'
  Method: 'POST'

  Expected JSON Response:

  {
    'Log Out Sucessful'
  }

# # Update User
    this route allows a user to be update an id's username and password

  EndPoint: '/user/update/id'
  Method: 'POST'

  Expected JSON Response:

  {
    'username': STR
    'password': STR
  }

# # Get All Users
    this route allows all users to be shown with corresponding JSON

  EndPoint: '/user/get'
  Method: 'GET'

  Expected JSON Response:

  {
    {
      'id': INT
      'username': STR
      'password': STR
      'blogs': []
    }
  }

# # Get User by username
    this route allows a user info to be read when the proper username is placed in

  EndPoint: '/user/get/username'
  Method: 'GET'

  Expected JSON Response:

  {
    {
      'id': INT
      'username': STR
      'password': STR
      'blogs': []
    }
  }

# # Delete User by id
    this route allows a user to be created storing their Id, username, password, 
    and creating a foreign key for a users blogs

  EndPoint: '/user/delete/id'
  Method: 'DELETE'

  Expected JSON Response:

  {
    'User Deleted!'
  }

# # Add Blog
    this route allows a user to add a blog to their blogs, through the use of a foreign key connecting to the Blog Schema

  EndPoint: '/blog/add'
  Method: 'POST'

  Expected JSON Response:

  {
    'id': INT
    'blog_name': STR
    'blog_text': STR
    'blog_user_id': INT
  }

# # Get All Blogs
    this route allows a user to grab all blogs a user has

  EndPoint: '/blog/get/user_id'
  Method: 'GET'

  Expected JSON Response:

  {
    'blog_name': STR
    'blog_text': STR
    'blog_user_id': INT
  }

# # Get Blog
    this route allows a user to read a specific blog post

  EndPoint: '/blog/get/blog_user_id/id'
  Method: 'GET'

  Expected JSON Response:

  {
    'blog_text': STR
    'blog_user_id': INT
  }

# # Delete Blog
    this route allows a user to delete thier blog by the specific id for said blog

  EndPoint: '/blog/delete/blog_user_id/id'
  Method: 'DELETE'

  Expected JSON Response:

  {
    'Blog Deleted!'
  }
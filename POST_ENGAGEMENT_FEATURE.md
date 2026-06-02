# Post Engagement Feature - Documentation

## Overview

A complete social media-style post engagement system has been added to your application. Users can create posts, like posts, comment on posts, and share posts with proper access control.

## Features Added

### 1. **Posts with Engagement Tracking**
- Create posts with text content
- Track likes, comments, and shares count
- Soft delete for posts (data preserved)
- Only post creator can delete their posts

### 2. **Like System**
- Users can like/unlike posts
- Real-time like count updates
- Visual feedback (filled heart for liked posts)
- Only active users can like (blocked users cannot)

### 3. **Comment System**
- Users can comment on posts
- Comments displayed with author and timestamp
- Comment count tracked
- Only active users can comment
- Users can delete their own comments
- Soft delete for comments

### 4. **Share System**
- Users can share posts
- Share count tracked
- Optional share message
- Only active users can share
- Share history maintained

### 5. **Access Control**
- ✅ Blocked users cannot create posts
- ✅ Blocked users cannot comment
- ✅ Blocked users cannot like posts
- ✅ Blocked users cannot share posts
- ✅ Only active users can engage
- ✅ Users can only delete their own content

## Database Models

### Post
```python
id: int (Primary Key)
user_id: int (Post creator)
content: Text (Post content)
created_at: DateTime
updated_at: DateTime
likes_count: int
comments_count: int
shares_count: int
is_deleted: bool (Soft delete)
```

### PostLike
```python
id: int (Primary Key)
post_id: int
user_id: int (Who liked)
created_at: DateTime
```

### PostComment
```python
id: int (Primary Key)
post_id: int
user_id: int (Comment author)
content: Text
likes_count: int
created_at: DateTime
updated_at: DateTime
is_deleted: bool (Soft delete)
```

### PostShare
```python
id: int (Primary Key)
post_id: int
user_id: int (Who shared)
share_message: Text (Optional)
created_at: DateTime
```

## API Endpoints

### Create Post
**Endpoint**: `POST /api/posts/create`

**Request**:
```json
{
    "user_id": 1,
    "content": "This is my first post!"
}
```

**Response**:
```json
{
    "id": 123,
    "user_id": 1,
    "content": "This is my first post!",
    "created_at": "2026-06-01T10:30:00",
    "likes_count": 0,
    "comments_count": 0,
    "shares_count": 0,
    "message": "Post created successfully"
}
```

### Get Feed
**Endpoint**: `GET /api/posts/feed?user_id=1&limit=20&offset=0`

**Response**:
```json
{
    "user_id": 1,
    "posts": [
        {
            "id": 123,
            "user_id": 2,
            "user_email": "user2@example.com",
            "content": "Check out this amazing post!",
            "created_at": "2026-06-01T10:30:00",
            "likes_count": 42,
            "comments_count": 5,
            "shares_count": 3,
            "is_liked": true
        }
    ],
    "total": 1
}
```

### Get Post Details
**Endpoint**: `GET /api/posts/{post_id}?user_id=1`

**Response**:
```json
{
    "id": 123,
    "user_id": 2,
    "user_email": "user2@example.com",
    "content": "Amazing post content",
    "created_at": "2026-06-01T10:30:00",
    "likes_count": 42,
    "comments_count": 5,
    "shares_count": 3,
    "is_liked": true,
    "comments": [
        {
            "id": 456,
            "post_id": 123,
            "user_id": 1,
            "user_email": "user1@example.com",
            "content": "Great post!",
            "likes_count": 2,
            "created_at": "2026-06-01T11:00:00"
        }
    ]
}
```

### Like Post
**Endpoint**: `POST /api/posts/{post_id}/like`

**Request**:
```json
{
    "post_id": 123,
    "user_id": 1
}
```

**Response**:
```json
{
    "post_id": 123,
    "user_id": 1,
    "action": "liked",
    "likes_count": 43,
    "message": "Post liked successfully"
}
```

### Add Comment
**Endpoint**: `POST /api/posts/{post_id}/comment`

**Request**:
```json
{
    "post_id": 123,
    "user_id": 1,
    "content": "Great post!"
}
```

**Response**:
```json
{
    "id": 456,
    "post_id": 123,
    "user_id": 1,
    "content": "Great post!",
    "created_at": "2026-06-01T11:00:00",
    "message": "Comment added successfully"
}
```

### Share Post
**Endpoint**: `POST /api/posts/{post_id}/share`

**Request**:
```json
{
    "post_id": 123,
    "user_id": 1,
    "share_message": "You should read this!"
}
```

**Response**:
```json
{
    "post_id": 123,
    "user_id": 1,
    "shares_count": 4,
    "message": "Post shared successfully"
}
```

### Delete Post
**Endpoint**: `DELETE /api/posts/{post_id}?user_id=1`

**Response**:
```json
{
    "post_id": 123,
    "message": "Post deleted successfully"
}
```

### Delete Comment
**Endpoint**: `DELETE /api/comments/{comment_id}?user_id=1`

**Response**:
```json
{
    "comment_id": 456,
    "message": "Comment deleted successfully"
}
```

### Get User's Posts
**Endpoint**: `GET /api/posts/user/{user_id}/posts?limit=20&offset=0`

**Response**:
```json
{
    "user_id": 1,
    "user_email": "user1@example.com",
    "posts": [
        {
            "id": 123,
            "user_id": 1,
            "content": "My post",
            "created_at": "2026-06-01T10:30:00",
            "likes_count": 10,
            "comments_count": 2,
            "shares_count": 1
        }
    ],
    "total": 1
}
```

## Frontend Usage

### Access Feed Page
Navigate to: `http://localhost:8000/feed`

### Creating a Post
1. Enter your user ID
2. Type your post content
3. Click "Post" button

### Engaging with Posts
- **Like**: Click the heart icon (❤️)
- **Comment**: Click comment button, type comment, click Reply
- **Share**: Click share button (📤)
- **Delete**: Click menu (⋮) on your own posts

## Security Features

### Access Control Rules
```python
# Only active users can:
✅ Create posts
✅ Like posts
✅ Comment on posts
✅ Share posts

# Blocked users cannot:
❌ Create posts
❌ Like posts
❌ Comment on posts
❌ Share posts

# User permissions:
✅ Can only delete their own posts
✅ Can only delete their own comments
✅ Can view all non-deleted posts
✅ Can see engagement counts
```

### Data Integrity
- Soft deletes preserve data
- Comment counts updated atomically
- Like counts tracked separately
- Share history maintained

## Database Queries

### Get Most Popular Posts (Last 7 days)
```sql
SELECT 
    p.id,
    p.content,
    p.user_id,
    p.likes_count,
    p.comments_count,
    p.shares_count,
    (p.likes_count + p.comments_count + p.shares_count) as engagement_score
FROM posts p
WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND p.is_deleted = FALSE
ORDER BY engagement_score DESC
LIMIT 10;
```

### Get User's Engagement
```sql
SELECT 
    pl.user_id,
    COUNT(DISTINCT pl.post_id) as likes_given,
    COUNT(DISTINCT pc.id) as comments_made,
    COUNT(DISTINCT ps.post_id) as posts_shared
FROM post_likes pl
LEFT JOIN post_comments pc ON pl.user_id = pc.user_id
LEFT JOIN post_shares ps ON pl.user_id = ps.user_id
WHERE pl.user_id = 1
GROUP BY pl.user_id;
```

### Get Post Performance
```sql
SELECT 
    p.id,
    p.content,
    COUNT(DISTINCT pl.id) as likes,
    COUNT(DISTINCT pc.id) as comments,
    COUNT(DISTINCT ps.id) as shares
FROM posts p
LEFT JOIN post_likes pl ON p.id = pl.post_id
LEFT JOIN post_comments pc ON p.id = pc.post_id
LEFT JOIN post_shares ps ON p.id = ps.post_id
WHERE p.id = 123
GROUP BY p.id;
```

## Usage Examples

### cURL Examples

**Create Post**:
```bash
curl -X POST http://localhost:8000/api/posts/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "content": "Hello community!"
  }'
```

**Get Feed**:
```bash
curl "http://localhost:8000/api/posts/feed?user_id=1&limit=10"
```

**Like Post**:
```bash
curl -X POST http://localhost:8000/api/posts/123/like \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 123,
    "user_id": 1
  }'
```

**Comment on Post**:
```bash
curl -X POST http://localhost:8000/api/posts/123/comment \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 123,
    "user_id": 1,
    "content": "Great post!"
  }'
```

**Share Post**:
```bash
curl -X POST http://localhost:8000/api/posts/123/share \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 123,
    "user_id": 1,
    "share_message": "Check this out!"
  }'
```

### Python Examples

```python
import requests

BASE_URL = "http://localhost:8000"

# Create post
def create_post(user_id, content):
    response = requests.post(
        f"{BASE_URL}/api/posts/create",
        json={"user_id": user_id, "content": content}
    )
    return response.json()

# Get feed
def get_feed(user_id):
    response = requests.get(f"{BASE_URL}/api/posts/feed?user_id={user_id}")
    return response.json()

# Like post
def like_post(post_id, user_id):
    response = requests.post(
        f"{BASE_URL}/api/posts/{post_id}/like",
        json={"post_id": post_id, "user_id": user_id}
    )
    return response.json()

# Comment on post
def comment_post(post_id, user_id, content):
    response = requests.post(
        f"{BASE_URL}/api/posts/{post_id}/comment",
        json={"post_id": post_id, "user_id": user_id, "content": content}
    )
    return response.json()

# Usage
post = create_post(1, "My first post!")
print(f"Created post {post['id']}")

feed = get_feed(1)
print(f"Feed has {feed['total']} posts")

like = like_post(post['id'], 1)
print(f"Post now has {like['likes_count']} likes")
```

## Testing

### Test Scenarios

1. **Post Creation**
   - Active user can create post ✅
   - Blocked user cannot create post ❌
   - Empty content rejected ✅

2. **Engagement (Like/Comment/Share)**
   - Active users can engage ✅
   - Blocked users cannot engage ❌
   - Like toggle works correctly ✅
   - Comment appears immediately ✅

3. **Feed Display**
   - Posts ordered by newest first ✅
   - Engagement counts accurate ✅
   - User's like status shown ✅

4. **Deletion**
   - Users can delete own posts ✅
   - Users cannot delete others' posts ❌
   - Post data preserved (soft delete) ✅
   - Comment count updated ✅

## Features Overview

| Feature | Active Users | Blocked Users | Guest |
|---------|---|---|---|
| View Feed | ✅ | ✅ | ❌ |
| Create Posts | ✅ | ❌ | ❌ |
| Like Posts | ✅ | ❌ | ❌ |
| Comment | ✅ | ❌ | ❌ |
| Share | ✅ | ❌ | ❌ |
| Delete Own | ✅ | ✅ | ❌ |
| Delete Others | ❌ | ❌ | ❌ |

## Limitations & Future Enhancements

### Current Limitations
- Comments don't support nested replies
- No comment liking
- No post editing (can only delete)
- No follow/unfollow system
- No recommendation algorithm

### Future Enhancements
- [ ] Edit posts (not just delete)
- [ ] Nested comment replies
- [ ] Like comments
- [ ] Follow/unfollow users
- [ ] User profiles
- [ ] Hashtag support
- [ ] Search functionality
- [ ] Trending posts
- [ ] Recommendation algorithm
- [ ] Post sharing to other platforms
- [ ] Analytics dashboard
- [ ] Spam detection

## Performance Notes

- Feed loads newest 20 posts by default
- Pagination supported via limit/offset
- Like/unlike is instant
- Comment counts updated in real-time
- Soft deletes prevent data loss
- Indexes recommended on user_id, post_id, created_at

## Troubleshooting

### Posts Not Loading
- Check user ID is valid
- Verify user exists in database
- Check database connection
- Review browser console for errors

### Cannot Post
- Check if account is blocked
- Verify content is not empty
- Ensure user ID is correct
- Check network connection

### Likes/Comments Not Working
- Verify user account is active
- Check post still exists (not deleted)
- Ensure network connection
- Clear browser cache

## Integration Notes

This feature integrates with:
- ✅ Existing user authentication
- ✅ User blocking system
- ✅ Database models
- ✅ FastAPI endpoints
- ✅ CORS middleware

---

**Status**: ✅ Implementation Complete
**Date**: June 2026
**Version**: 1.0

# Post Engagement Feature - Quick Start

## 🚀 Getting Started

### 1. Access the Feed
Navigate to: **`http://localhost:8000/feed`**

### 2. Create Your First Post
1. Enter your User ID (default: 1)
2. Type your message in the text area
3. Click **"Post"** button
4. Your post appears at the top of the feed!

## 📱 Features Overview

### Create Posts
```
📝 Post Content
  ├─ Text content only (for now)
  ├─ No character limit
  ├─ Auto-saves timestamp
  └─ Only active users can post
```

### Engage with Posts
```
❤️ Like
  ├─ Click heart to like/unlike
  ├─ See like count
  └─ Only active users can like

💬 Comment  
  ├─ Click to view/add comments
  ├─ See all comments on post
  ├─ Only active users can comment
  └─ Comments show author & timestamp

📤 Share
  ├─ Click to share post
  ├─ Share count tracked
  └─ Only active users can share
```

### Delete Content
```
⋮ Menu (Your Posts Only)
  ├─ Click three dots on your posts
  └─ Confirm deletion
```

## 🎯 Access Control

### Who Can Do What?

**Active Users** ✅
- View feed
- Create posts
- Like posts
- Comment on posts
- Share posts
- Delete own posts

**Blocked Users** ❌
- Cannot create posts
- Cannot like posts
- Cannot comment
- Cannot share posts
- CAN delete their own posts
- CAN view feed (read-only)

**Requirements**
- Valid user ID
- Account must be "active" status
- Only non-deleted content shown

## 📊 Real-time Stats

Each post shows:
- **❤️ Likes** - Number of users who liked
- **💬 Comments** - Total comments on post
- **📤 Shares** - How many times shared

## 💡 Tips & Tricks

### View Comments Without Scrolling
Click **"💬 Comment"** button to expand comments section

### Check Your Posts
View your profile posts:
```
GET /api/posts/user/{user_id}/posts
```

### Get Engagement Metrics
View post details:
```
GET /api/posts/{post_id}?user_id=1
```

## 🔒 Security Features

- Blocked users cannot engage
- Users can only delete own content
- All content moderated by threat detection
- Audit trail of actions
- Data preserved even when deleted (soft delete)

## 🐛 Troubleshooting

### "Can only create 1 post"
This is just a display limit - scroll to see more posts

### "Blocked users cannot create posts"
Your account is marked as blocked. Contact admin to unblock.

### Post not appearing
- Refresh the page
- Check user ID is correct
- Verify content wasn't empty
- Check database connection

### Cannot like/comment
- Check if account is active
- Verify you're using correct user ID
- Ensure post still exists
- Try refreshing page

## 📞 API Quick Reference

### Create Post
```bash
POST /api/posts/create
{
  "user_id": 1,
  "content": "Your post here"
}
```

### Like Post
```bash
POST /api/posts/{post_id}/like
{
  "post_id": 123,
  "user_id": 1
}
```

### Comment
```bash
POST /api/posts/{post_id}/comment
{
  "post_id": 123,
  "user_id": 1,
  "content": "Your comment"
}
```

### Share
```bash
POST /api/posts/{post_id}/share
{
  "post_id": 123,
  "user_id": 1,
  "share_message": "Check this out"
}
```

### Get Feed
```bash
GET /api/posts/feed?user_id=1
```

### Delete Post
```bash
DELETE /api/posts/{post_id}?user_id=1
```

## 🎨 UI Features

### Real-time Feedback
- Posts update instantly
- Like count changes immediately
- Comments appear right away
- Error messages shown clearly

### Responsive Design
- Works on desktop
- Works on tablet
- Works on mobile

### Dark Theme
- Eye-friendly dark UI
- Cyan (#00d4ff) accent color
- Green (#00ff88) highlights
- Red (#ff4444) errors

## 📈 Best Practices

1. **Keep Posts Clear** - Use simple language
2. **Engage Respectfully** - Positive comments only
3. **Share Appropriately** - Only share relevant content
4. **Monitor Engagement** - Check post performance
5. **Delete If Needed** - Remove outdated posts

## 🔄 Workflow Example

```
1. User A logs in (User ID: 1)
2. User A posts: "Check out my update!"
3. User B (User ID: 2) sees post in feed
4. User B likes the post
5. User B adds comment
6. User A sees engagement
7. User A shares post internally
8. Both see updated statistics
```

## 📝 Post Limits (Recommendations)

- Minimum content: 1 character
- Maximum effective: ~500 characters (for readability)
- Posts per day: No limit
- Comments per post: Unlimited
- Likes per post: Unlimited
- Shares per post: Unlimited

## 🔐 Privacy & Data

- All posts are visible to authenticated users
- Comments are public
- Likes are private (not shown to others)
- Share information tracked but private
- Deletion is soft (data preserved)

## ⚙️ Advanced Usage

### Get Post Details with Comments
```bash
GET /api/posts/123?user_id=1
```
Returns: Full post with all comments

### Get User's Posts
```bash
GET /api/posts/user/1/posts
```
Returns: All posts by user 1

### Pagination
```bash
GET /api/posts/feed?user_id=1&limit=10&offset=0
```
Supports: limit (default 20), offset (default 0)

## 💾 Data Persistence

- All posts, comments, and engagement data saved to database
- Changes are immediate
- No pending actions
- Data persists between sessions
- Backups recommended

## 🆘 Support

For issues:
1. Check troubleshooting section
2. Review browser console (F12)
3. Check user ID is correct
4. Verify account status
5. Check internet connection
6. Refresh page

## ✅ Feature Checklist

- [x] Create posts
- [x] Like posts (toggle)
- [x] Comment on posts
- [x] Share posts
- [x] View feed
- [x] Delete own posts
- [x] Access control
- [x] Real-time updates
- [x] Comment viewing
- [x] Engagement tracking

---

**Ready to start posting!** 📱

Navigate to `/feed` and create your first post now!

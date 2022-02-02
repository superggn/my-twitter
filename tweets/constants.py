class TweetPhotoStatus:
    PENDING = 0
    APPROVED = 1
    REJECTED = 2


# 这里的后半部分字符串会显示在 admin 界面中
TWEET_PHOTO_STATUS_CHOICES = (
    (TweetPhotoStatus.PENDING, 'Pending'),
    (TweetPhotoStatus.APPROVED, 'Approved'),
    (TweetPhotoStatus.REJECTED, 'Rejected'),
)

TWEET_PHOTOS_UPLOAD_LIMIT = 9

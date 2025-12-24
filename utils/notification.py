from django.utils import timezone
from apps.user.models import Notification, User
from apps.appreciation.models import Work, Comment


def create_notification(recipient, notification_type, content, sender=None, work=None, comment=None):
    """
    创建通知的工具函数

    Args:
        recipient: 接收通知的用户对象
        notification_type: 通知类型（like, comment, reply, follow, system）
        content: 通知内容
        sender: 发送通知的用户对象（可选，系统通知不需要）
        work: 关联的作品对象（可选）
        comment: 关联的评论对象（可选）
    """
    # 确保接收者是用户对象
    if not isinstance(recipient, User):
        return False

    # 确保发送者不是接收者自己（避免给自己发通知）
    if sender and sender == recipient:
        return False

    # 创建通知对象
    notification = Notification(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        content=content,
        work_id=work.id if work else None,
        comment_id=comment.id if comment else None
    )

    try:
        notification.save()
        return True
    except Exception as e:
        return False


# 以下是各种场景的通知创建函数

def create_like_notification(user, work):
    """创建点赞通知"""
    content = f"{user.name} 点赞了您的作品《{work.title}》"
    return create_notification(
        recipient=work.user,
        notification_type='like',
        content=content,
        sender=user,
        work=work
    )


def create_comment_notification(user, comment):
    """创建评论通知"""
    comment_content = comment.content[:50] + "..." if len(comment.content) > 50 else comment.content
    content = f"{user.name} 评论了您的作品《{comment.work.title}》：{comment_content}"
    return create_notification(
        recipient=comment.work.user,
        notification_type='comment',
        content=content,
        sender=user,
        work=comment.work,
        comment=comment
    )


def create_reply_notification(user, reply):
    """创建回复通知"""
    # 如果回复的是评论，通知评论作者
    if reply.parent:
        reply_content = reply.content[:50] + "..." if len(reply.content) > 50 else reply.content
        content = f"{user.name} 回复了您的评论：{reply_content}"
        return create_notification(
            recipient=reply.parent.user,
            notification_type='reply',
            content=content,
            sender=user,
            work=reply.work,
            comment=reply
        )
    return False


def create_follow_notification(follower, following):
    """创建关注通知"""
    content = f"{follower.name} 关注了您"
    return create_notification(
        recipient=following,
        notification_type='follow',
        content=content,
        sender=follower
    )


def create_system_notification(recipient, content):
    """创建系统通知"""
    return create_notification(
        recipient=recipient,
        notification_type='system',
        content=content
    )
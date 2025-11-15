import random
import string

from apps.user.models import User


def generate_random_name(length=8):
    """
    生成随机用户名，格式为"用户+随机字符串"

    Args:
        length: 随机字符串的长度，默认为8

    Returns:
        str: 生成的用户名
    """
    # 生成随机字符串，包含字母和数字
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    name = f"用户{random_chars}"

    # 检查用户名是否已存在，如果存在则重新生成
    while User.objects.filter(name=name).exists():
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        name = f"用户{random_chars}"

    return name
// 切换个人中心标签页
function switchProfileTab(tabId) {
  // 隐藏所有内容
  document.querySelectorAll('.profile-content').forEach(content => {
    content.classList.remove('active');
  });

  // 移除所有标签的活跃状态
  document.querySelectorAll('.profile-tab').forEach(tab => {
    tab.classList.remove('active');
  });

  // 显示选中的内容和激活对应的标签
  document.getElementById(tabId).classList.add('active');
  event.currentTarget.classList.add('active');

  // 如果切换到消息标签页，初始化通知
  if (tabId === 'messages') {
    initNotifications();
  }
}

// 编辑资料模态框功能
const editProfileBtn = document.getElementById('edit-profile-btn');
const closeModalBtn = document.getElementById('close-modal-btn');
const cancelEditBtn = document.getElementById('cancel-edit-btn');
const saveEditBtn = document.getElementById('save-edit-btn');
const editProfileModal = document.getElementById('edit-profile-modal');
const avatarUpload = document.getElementById('avatar-upload');
const currentAvatar = document.getElementById('current-avatar');
const avatarError = document.getElementById('avatar-error');
const profileMessage = document.getElementById('profile-message');

// 打开模态框
editProfileBtn.addEventListener('click', () => {
  editProfileModal.classList.remove('hidden');
  // 防止背景滚动
  document.body.style.overflow = 'hidden';
});

// 关闭模态框的函数
function closeModal() {
  editProfileModal.classList.add('hidden');
  // 恢复背景滚动
  document.body.style.overflow = '';
  // 重置头像上传错误提示
  avatarError.classList.add('hidden');
  // 重置顶部提示
  if (profileMessage) {
    profileMessage.classList.add('hidden');
    profileMessage.textContent = '';
    profileMessage.classList.remove('text-red-600', 'bg-red-50', 'border', 'border-red-200');
    profileMessage.classList.remove('text-green-600', 'bg-green-50', 'border', 'border-green-200');
  }
}

// 点击关闭按钮关闭模态框
closeModalBtn.addEventListener('click', closeModal);
// 点击取消按钮关闭模态框
cancelEditBtn.addEventListener('click', closeModal);

// 点击模态框外部关闭模态框
editProfileModal.addEventListener('click', (e) => {
  if (e.target === editProfileModal) {
    closeModal();
  }
});

// ESC键关闭模态框
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !editProfileModal.classList.contains('hidden')) {
    closeModal();
  }
});

// 头像预览功能
avatarUpload.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    // 检查文件类型
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      avatarError.textContent = '请上传JPG、PNG或GIF格式的图片';
      avatarError.classList.remove('hidden');
      return;
    }

    // 检查文件大小（限制为5MB）
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      avatarError.textContent = '文件大小不能超过5MB';
      avatarError.classList.remove('hidden');
      return;
    }

    avatarError.classList.add('hidden');

    // 创建预览
    const reader = new FileReader();
    reader.onload = (event) => {
      currentAvatar.src = event.target.result;
    };
    reader.readAsDataURL(file);
  }
});

// 获取 CSRF Token（来自 cookie）
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 顶部提示展示
function showProfileMessage(text, type = 'error') {
  if (!profileMessage) return;
  profileMessage.textContent = text;
  profileMessage.classList.remove('hidden');
  profileMessage.classList.add('border', 'rounded', 'px-3', 'py-2');

  // 清理旧样式
  profileMessage.classList.remove('text-red-600', 'bg-red-50', 'border-red-200');
  profileMessage.classList.remove('text-green-600', 'bg-green-50', 'border-green-200');

  if (type === 'success') {
    profileMessage.classList.add('text-green-600', 'bg-green-50', 'border-green-200');
  } else {
    profileMessage.classList.add('text-red-600', 'bg-red-50', 'border-red-200');
  }
}

// 保存修改按钮点击事件（Ajax 提交）
saveEditBtn.addEventListener('click', () => {
  const form = document.getElementById('edit-profile-form');

  // 简单验证
  const name = document.getElementById('edit-name').value.trim();
  if (!name) {
    showProfileMessage('请输入昵称', 'error');
    return;
  }

  const formData = new FormData(form);

  fetch('/user/profile/edit/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: formData
  })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
      if (status >= 200 && status < 300 && body.success) {
        showProfileMessage(body.message || '个人资料已更新', 'success');
        // 2秒后自动关闭模态框
        setTimeout(closeModal, 2000);
        // 更新页面上展示的用户名 / 头像等
        if (body.data && body.data.avatar_url) {
          currentAvatar.src = body.data.avatar_url;
        }
      } else {
        showProfileMessage(body.error || '保存失败，请稍后重试', 'error');
      }
    })
    .catch(() => {
      showProfileMessage('网络错误，请稍后重试', 'error');
    });
});

// ----------------------------- 
// 消息通知功能 
// ----------------------------- 

let currentNotificationType = '';
let currentNotificationPage = 1;
let hasMoreNotifications = true;

// 初始化消息通知
function initNotifications() {
  loadNotifications();
  
  // 绑定通知类型切换事件
  const typeButtons = document.querySelectorAll('.notification-type-btn');
  typeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      // 更新按钮状态
      typeButtons.forEach(b => {
        b.classList.remove('text-goldline', 'border-b-2', 'border-goldline');
        b.classList.add('text-gray-500');
      });
      btn.classList.remove('text-gray-500');
      btn.classList.add('text-goldline', 'border-b-2', 'border-goldline');
      
      // 加载对应类型的通知
      currentNotificationType = btn.getAttribute('data-type') || '';
      currentNotificationPage = 1;
      hasMoreNotifications = true;
      loadNotifications(true);
    });
  });
  
  // 绑定加载更多按钮事件
  const loadMoreBtn = document.getElementById('load-more-btn');
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', () => {
      currentNotificationPage++;
      loadNotifications(false);
    });
  }
}

// 加载通知
function loadNotifications(clear = false) {
  const notificationList = document.getElementById('notification-list');
  const loadMoreContainer = document.getElementById('load-more-container');
  
  if (!notificationList) return;
  
  // 显示加载状态
  if (clear) {
    notificationList.innerHTML = '<div class="text-center py-8">加载中...</div>';
  }
  
  fetch(`/user/notifications/?type=${currentNotificationType}&page=${currentNotificationPage}`, {
    method: 'GET'
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // 清空列表（如果是首次加载或切换类型）
      if (clear) {
        notificationList.innerHTML = '';
      }
      
      // 渲染通知
      if (data.notifications && data.notifications.length > 0) {
        data.notifications.forEach(notification => {
          const notificationElement = createNotificationElement(notification);
          notificationList.appendChild(notificationElement);
        });
        
        // 更新加载更多按钮状态
        hasMoreNotifications = data.has_next;
        if (hasMoreNotifications) {
          loadMoreContainer.classList.remove('hidden');
        } else {
          loadMoreContainer.classList.add('hidden');
        }
      } else {
        // 没有通知
        notificationList.innerHTML = '<div class="py-12 text-center text-gray-500">暂无通知</div>';
        loadMoreContainer.classList.add('hidden');
      }
    } else {
      notificationList.innerHTML = '<div class="py-12 text-center text-red-500">加载通知失败</div>';
    }
  })
  .catch(() => {
    notificationList.innerHTML = '<div class="py-12 text-center text-red-500">网络错误，请稍后重试</div>';
  });
}

// 创建通知元素
function createNotificationElement(notification) {
  const notificationDiv = document.createElement('div');
  notificationDiv.className = 'p-4 rounded-lg';

  // 根据通知类型设置基础样式
  if (notification.type === 'like' || notification.type === 'comment' || notification.type === 'reply' || notification.type === 'follow') {
    notificationDiv.classList.add('bg-bluewhite/5', 'border', 'border-bluewhite/10');
  } else {
    notificationDiv.classList.add('bg-gray-50');
  }

  // 为未读通知添加特殊样式
  if (!notification.is_read) {
    notificationDiv.classList.add('border-l-4', 'border-bluewhite', 'bg-bluewhite/10');
    notificationDiv.classList.add('font-medium');
  }

  // 构建通知内容
  const icon = getNotificationIcon(notification.type);
  const content = `
    <div class="flex gap-3">
      <div class="w-10 h-10 rounded-full ${notification.type === 'like' || notification.type === 'comment' || notification.type === 'reply' || notification.type === 'follow' ? 'bg-bluewhite/20 text-bluewhite' : 'bg-gray-200 text-gray-600'} flex items-center justify-center flex-shrink-0">
        <iconify-icon icon="${icon}"></iconify-icon>
      </div>
      <div class="flex-1">
        <p class="text-sm">${notification.content}</p>
        <p class="text-xs text-gray-500 mt-1">${notification.created_at}</p>
      </div>
    </div>
  `;

  notificationDiv.innerHTML = content;

  // 添加点击跳转（如果有URL）并标记为已读
  if (notification.url) {
    notificationDiv.style.cursor = 'pointer';
    notificationDiv.addEventListener('click', () => {
      // 标记通知为已读
      if (!notification.is_read) { // 修正：使用!notification.is_read而不是notification.is_unread
        fetch(`/user/notifications/mark-read/${notification.id}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken')
          }
        }).then(response => {
          if (response.ok) {
            // 移除未读样式
            notificationDiv.classList.remove('border-l-4', 'border-bluewhite', 'bg-bluewhite/10', 'font-medium');
            notification.is_read = true;
          }
        });
      }
      window.location.href = notification.url;
    });
  }

  return notificationDiv;
}

// 获取通知图标
function getNotificationIcon(type) {
  switch(type) {
    case 'like':
      return 'mdi:heart';
    case 'comment':
      return 'mdi:comment';
    case 'reply':
      return 'mdi:reply';
    case 'follow':
      return 'mdi:account-plus';
    case 'system':
      return 'mdi:information';
    default:
      return 'mdi:bell';
  }
}

// -----------------------------
// 我的作品：卡片点击 & 自定义删除确认
// -----------------------------

document.addEventListener('DOMContentLoaded', () => {

  // 1. 卡片点击跳转详情（编辑/删除按钮会阻止冒泡）
  const workCards = document.querySelectorAll('.work-card');
  workCards.forEach(card => {
    const detailUrl = card.getAttribute('data-detail-url');
    if (!detailUrl) return;

    card.addEventListener('click', () => {
      window.location.href = detailUrl;
    });
  });

  // 2. 防止编辑/删除按钮触发卡片点击
  document.querySelectorAll('.work-edit-btn, .work-delete-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  });

  // 3. 自定义删除模态框
  const deleteModal = document.getElementById('delete-work-modal');
  const deleteTitleSpan = document.getElementById('delete-work-title');
  const deleteCancelIcon = document.getElementById('delete-work-cancel-icon');
  const deleteCancelBtn = document.getElementById('delete-work-cancel-btn');
  const deleteConfirmBtn = document.getElementById('delete-work-confirm-btn');

  let pendingDeleteForm = null;

  function closeDeleteModal() {
    if (!deleteModal) return;
    deleteModal.classList.add('hidden');
    pendingDeleteForm = null;
    if (deleteTitleSpan) {
      deleteTitleSpan.textContent = '';
    }
  }

  function openDeleteModal(form) {
    if (!deleteModal) return;
    pendingDeleteForm = form;
    const title = form.getAttribute('data-work-title') || '';
    if (deleteTitleSpan) {
      deleteTitleSpan.textContent = title;
    }
    deleteModal.classList.remove('hidden');
  }

  // 绑定每个删除按钮
  document.querySelectorAll('.work-delete-form').forEach(form => {
    const btn = form.querySelector('.work-delete-btn');
    if (!btn) return;

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openDeleteModal(form);
    });
  });

  // 关闭模态框
  if (deleteCancelIcon) {
    deleteCancelIcon.addEventListener('click', () => closeDeleteModal());
  }
  if (deleteCancelBtn) {
    deleteCancelBtn.addEventListener('click', () => closeDeleteModal());
  }

  if (deleteModal) {
    deleteModal.addEventListener('click', (e) => {
      if (e.target === deleteModal) {
        closeDeleteModal();
      }
    });
  }

  // 确认删除
  if (deleteConfirmBtn) {
    deleteConfirmBtn.addEventListener('click', () => {
      if (pendingDeleteForm) {
        pendingDeleteForm.submit();
      }
      closeDeleteModal();
    });
  }

  // -----------------------------
  // 关注功能
  // -----------------------------

  // 关注按钮点击事件
  const followBtn = document.getElementById('follow-btn');
  if (followBtn) {
    followBtn.addEventListener('click', () => {
      const userId = followBtn.getAttribute('data-user-id');
      const isFollowing = followBtn.textContent.trim() === '已关注';
      
      // 显示加载状态
      followBtn.disabled = true;
      followBtn.textContent = '处理中...';
      
      // 构建请求URL
      const url = isFollowing ? `/user/unfollow/${userId}/` : `/user/follow/${userId}/`;
      
      // 发送请求
      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json().then(data => ({ status: response.status, body: data })))
      .then(({ status, body }) => {
        if (status >= 200 && status < 300 && body.success) {
          // 更新按钮状态
          if (body.following) {
            followBtn.textContent = '已关注';
            followBtn.classList.remove('border-bluewhite', 'text-bluewhite', 'hover:bg-bluewhite', 'hover:text-white');
            followBtn.classList.add('bg-bluewhite', 'text-white');
          } else {
            followBtn.textContent = '关注';
            followBtn.classList.remove('bg-bluewhite', 'text-white');
            followBtn.classList.add('border-bluewhite', 'text-bluewhite', 'hover:bg-bluewhite', 'hover:text-white');
          }
        } else {
          // 恢复原始状态
          followBtn.textContent = isFollowing ? '已关注' : '关注';
          // 显示错误提示
          alert(body.error || '操作失败，请稍后重试');
        }
      })
      .catch(() => {
        // 恢复原始状态
        followBtn.textContent = isFollowing ? '已关注' : '关注';
        alert('网络错误，请稍后重试');
      })
      .finally(() => {
        // 恢复按钮可用性
        followBtn.disabled = false;
      });
    });
  }
}); 
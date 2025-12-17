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
    
    // 检查文件大小（限制为2MB）
    const maxSize = 2 * 1024 * 1024; // 2MB
    if (file.size > maxSize) {
      avatarError.textContent = '文件大小不能超过2MB';
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

// 保存修改按钮点击事件
saveEditBtn.addEventListener('click', () => {
  // 这里可以添加表单验证和提交逻辑
  const form = document.getElementById('edit-profile-form');

  // 简单验证
  const name = document.getElementById('edit-name').value.trim();
  if (!name) {
    alert('请输入昵称');
    return;
  }

  // 在实际应用中，这里会使用AJAX提交表单数据
  console.log('提交表单数据');

  // 模拟保存成功
  alert('个人资料已更新');
  closeModal();
});
// 切换登录和注册表单
function switchTab(tabName) {
  // 隐藏所有表单
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const loginPrompt = document.getElementById('login-prompt');
  const registerPrompt = document.getElementById('register-prompt');
  const loginTab = document.getElementById('login-tab');
  const registerTab = document.getElementById('register-tab');
  
  if (loginForm) loginForm.classList.add('hidden');
  if (registerForm) registerForm.classList.add('hidden');
  if (loginPrompt) loginPrompt.classList.add('hidden');
  if (registerPrompt) registerPrompt.classList.add('hidden');

  // 移除所有选项卡的活跃状态
  if (loginTab) loginTab.classList.remove('active');
  if (registerTab) registerTab.classList.remove('active');

  // 显示选中的表单和提示
  if (tabName === 'login') {
    if (loginForm) loginForm.classList.remove('hidden');
    if (loginPrompt) loginPrompt.classList.remove('hidden');
    if (loginTab) loginTab.classList.add('active');
    history.pushState({}, '', '/user/login/');
  } else if (tabName === 'register') {
    if (registerForm) registerForm.classList.remove('hidden');
    if (registerPrompt) registerPrompt.classList.remove('hidden');
    if (registerTab) registerTab.classList.add('active');
    history.pushState({}, '', '/user/register/');
  }
}

// 切换密码可见性
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const eyeIcon = document.getElementById(inputId.replace('password', 'eye-icon'));

  if (input.type === 'password') {
    input.type = 'text';
    eyeIcon.icon = 'mdi:eye';
  } else {
    input.type = 'password';
    eyeIcon.icon = 'mdi:eye-off';
  }
}

// 显示错误信息
function showError(inputElement, errorMessage) {
  // 清除之前的错误信息
  const existingError = inputElement.parentNode.parentNode.querySelector('.error-message');
  if (existingError) {
    inputElement.parentNode.parentNode.removeChild(existingError);
  }
  
  // 添加错误样式到输入框
  inputElement.classList.add('error');
  
  // 创建错误信息元素
  const errorElement = document.createElement('div');
  errorElement.className = 'error-message';
  errorElement.textContent = errorMessage;
  
  // 将错误信息添加到输入框的祖父容器中（在label和输入框容器之间）
  inputElement.parentNode.parentNode.appendChild(errorElement);
}

// 清除错误信息
function clearError(inputElement) {
  inputElement.classList.remove('error');
  const errorElement = inputElement.parentNode.parentNode.querySelector('.error-message');
  if (errorElement) {
    inputElement.parentNode.parentNode.removeChild(errorElement);
  }
}

// 清除所有错误信息
function clearAllErrors() {
  document.querySelectorAll('.error').forEach(input => {
    clearError(input);
  });
  
  // 清除服务条款的错误提示
  const termsContainer = document.getElementById('terms')?.parentNode;
  if (termsContainer) {
    const existingError = termsContainer.querySelector('.error-message');
    if (existingError) {
      termsContainer.removeChild(existingError);
    }
  }
}

// 添加输入框实时验证
function addRealTimeValidation(inputElement, validationFunction) {
  inputElement.addEventListener('input', function() {
    clearError(this);
    const errorMessage = validationFunction(this.value);
    if (errorMessage) {
      showError(this, errorMessage);
    }
  });
  
  // 添加失去焦点时的验证
  inputElement.addEventListener('blur', function() {
    clearError(this);
    const errorMessage = validationFunction(this.value);
    if (errorMessage) {
      showError(this, errorMessage);
    }
  });
}

// 添加表单验证初始化
function initFormValidation() {
  // 获取注册表单元素
  const registerForm = document.querySelector('#register-form form');
  if (!registerForm) return;

  // 获取各个输入字段
  const usernameInput = document.getElementById('register-username');
  const emailInput = document.getElementById('register-email');
  const password1Input = document.getElementById('register-password1');
  const password2Input = document.getElementById('register-password2');
  const termsInput = document.getElementById('terms');

  // 账号验证：3-20字
  if (usernameInput) {
    addRealTimeValidation(usernameInput, function(value) {
      if (!value) {
        return '请输入账号';
      }
      if (value.length < 3) {
        return '账号长度不能少于3个字符';
      }
      if (value.length > 20) {
        return '账号长度不能超过20个字符';
      }
      return '';
    });
  }

  // 邮箱验证
  if (emailInput) {
    addRealTimeValidation(emailInput, function(value) {
      if (!value) {
        return '请输入邮箱地址';
      }
      // 简单的邮箱格式验证正则
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        return '请输入有效的邮箱地址';
      }
      return '';
    });
  }

  // 密码验证
  if (password1Input) {
    addRealTimeValidation(password1Input, function(value) {
      if (!value) {
        return '请设置密码';
      }
      if (value.length < 8) {
        return '密码长度不能少于8个字符';
      }
      return '';
    });
  }

  // 确认密码验证
  if (password2Input) {
    // 输入时验证
    addRealTimeValidation(password2Input, function(value) {
      if (!value) {
        return '请再次输入密码';
      }
      if (password1Input && value !== password1Input.value) {
        return '两次输入的密码不一致';
      }
      return '';
    });

    // 当密码输入框变化时，也验证确认密码
    if (password1Input) {
      password1Input.addEventListener('input', function() {
        if (password2Input.value) {
          clearError(password2Input);
          if (password2Input.value !== password1Input.value) {
            showError(password2Input, '两次输入的密码不一致');
          }
        }
      });
    }
  }

  // 条款同意验证
  if (termsInput) {
    termsInput.addEventListener('change', function() {
      const termsContainer = this.parentNode;
      const existingError = termsContainer.querySelector('.error-message');

      if (!this.checked) {
        if (!existingError) {
          const errorElement = document.createElement('div');
          errorElement.className = 'error-message';
          errorElement.innerHTML = '<iconify-icon class="text-red-500 mr-2 mt-0.5" icon="mdi:alert-circle"></iconify-icon><span>请阅读并同意服务条款和隐私政策</span>';
          termsContainer.appendChild(errorElement);
        }
      } else if (existingError) {
        termsContainer.removeChild(existingError);
      }
    });
  }

  // 表单提交验证
  registerForm.addEventListener('submit', function(e) {
  let isValid = true;
  clearAllErrors();

  // 账号验证（3-20字）
  if (usernameInput) {
    const username = usernameInput.value.trim();
    if (!username) {
      showError(usernameInput, '请输入账号');
      isValid = false;
    } else if (username.length < 3 || username.length > 20) {
      showError(usernameInput, '账号长度必须在3-20个字符之间');
      isValid = false;
    }
  }

  // 邮箱验证
  if (emailInput) {
    const email = emailInput.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      showError(emailInput, '请输入邮箱地址');
      isValid = false;
    } else if (!emailRegex.test(email)) {
      showError(emailInput, '请输入有效的邮箱地址（例如：xxx@example.com）');
      isValid = false;
    }
  }

  // 密码验证（至少8位）
  if (password1Input) {
    const password = password1Input.value;
    if (!password) {
      showError(password1Input, '请设置密码');
      isValid = false;
    } else if (password.length < 8) {
      showError(password1Input, '密码长度不能少于8个字符');
      isValid = false;
    }
  }

  // 密码一致性验证
  if (password2Input && password1Input) {
    const pwd1 = password1Input.value;
    const pwd2 = password2Input.value;
    if (!pwd2) {
      showError(password2Input, '请再次输入密码');
      isValid = false;
    } else if (pwd1 !== pwd2) {
      showError(password2Input, '两次输入的密码不一致');
      isValid = false;
    }
  }

  // 条款同意验证
  if (termsInput && !termsInput.checked) {
    const termsContainer = termsInput.parentNode;
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.innerHTML = '<iconify-icon class="text-red-500 mr-2 mt-0.5" icon="mdi:alert-circle"></iconify-icon><span>请阅读并同意服务条款和隐私政策</span>';
    termsContainer.appendChild(errorElement);
    isValid = false;
  }

  // 验证失败阻止提交
  if (!isValid) {
    e.preventDefault(); // 关键：阻止表单提交
    // 滚动到第一个错误
    const firstError = document.querySelector('.error-message');
    if (firstError) {
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
});
}


// 在DOM加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
  // URL检测并切换到正确的选项卡
  const path = window.location.pathname;
  if (path === '/user/login/') {
    switchTab('login');
  } else if (path === '/user/register/') {
    switchTab('register');
  }
  
  // 检查URL中是否有active_tab参数，如果有则切换到对应选项卡
  const urlParams = new URLSearchParams(window.location.search);
  const activeTab = urlParams.get('active_tab');
  if (activeTab === 'login' || activeTab === 'register') {
    switchTab(activeTab);
    // 滚动到页面顶部，确保错误信息可见
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  // 初始化表单验证
  initFormValidation();
});



// 作品编辑页交互逻辑

document.addEventListener('DOMContentLoaded', () => {
  // ===== 图片上传相关 =====
  const imageContainer = document.getElementById('image-container');
  const uploadArea = imageContainer ? imageContainer.querySelector('.upload-area') : null;
  const fileInput = uploadArea ? uploadArea.querySelector('input[type="file"]') : null;

  const MAX_IMAGES = 9;
  const MAX_SIZE_MB = 5;
  const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  // 用于真正提交到后端的文件集合（支持多次选择累加）
  let selectedFiles = [];

  function clearPreviews() {
    if (!imageContainer) return;
    // 保留第一个上传区域，其余全部移除
    while (imageContainer.children.length > 1) {
      imageContainer.removeChild(imageContainer.lastElementChild);
    }
  }

  function renderPreviews() {
    clearPreviews();
    selectedFiles.forEach((file, index) => createPreview(file, index));
  }

  function createPreview(file, index) {
    const wrapper = document.createElement('div');
    wrapper.className =
      'aspect-square rounded-lg overflow-hidden border border-gray-200 shadow-sm relative bg-gray-50 group';

    const img = document.createElement('img');
    img.className = 'w-full h-full object-cover';
    img.alt = file.name;

    const reader = new FileReader();
    reader.onload = e => {
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);

    // 删除按钮
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className =
      'absolute top-1 right-1 w-7 h-7 rounded-full bg-black/60 text-white flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition';
    deleteBtn.innerHTML = '×';
    deleteBtn.title = '移除这张图片';

    deleteBtn.addEventListener('click', e => {
      e.stopPropagation();
      // 根据索引从 selectedFiles 中移除对应文件
      selectedFiles.splice(index, 1);
      renderPreviews();
    });

    wrapper.appendChild(img);
    wrapper.appendChild(deleteBtn);
    imageContainer.appendChild(wrapper);
  }

  function handleFilesChange() {
    if (!fileInput || !fileInput.files) return;

    const files = Array.from(fileInput.files);

    if (files.length === 0) {
      return;
    }

    const validFiles = [];

    for (const file of files) {
      if (!ALLOWED_TYPES.includes(file.type)) {
        alert(`文件 "${file.name}" 格式不支持，只能上传 JPG / PNG / GIF / WebP 图片。`);
        continue;
      }

      const sizeMB = file.size / (1024 * 1024);
      if (sizeMB > MAX_SIZE_MB) {
        alert(`文件 "${file.name}" 大小超过 ${MAX_SIZE_MB}MB，请压缩后再上传。`);
        continue;
      }

      validFiles.push(file);
    }

    if (validFiles.length === 0) {
      alert('没有符合要求的图片，请检查格式与大小后重新选择。');
      return;
    }

    // 计算还能再添加几张（基于已选文件数量）
    const remainingSlots = MAX_IMAGES - selectedFiles.length;
    if (remainingSlots <= 0) {
      alert(`最多只能上传 ${MAX_IMAGES} 张图片，您已达到上限。`);
      return;
    }

    const filesToAdd = validFiles.slice(0, remainingSlots);

    if (validFiles.length > remainingSlots) {
      alert(`最多只能上传 ${MAX_IMAGES} 张图片，本次只会添加前 ${remainingSlots} 张。`);
    }

    // 将新选择的文件累加到 selectedFiles 中
    selectedFiles = selectedFiles.concat(filesToAdd);

    // 重新渲染预览，确保和 selectedFiles 一致
    renderPreviews();
  }

  if (fileInput && uploadArea && imageContainer) {
    // 仅监听文件变更事件，点击行为交给原生 input（其本身覆盖整个上传区域）
    fileInput.addEventListener('change', handleFilesChange);
  }

  // 拦截表单提交，使用 selectedFiles 构造 FormData 确保多次选择的图片都能提交到后端
  const workForm = document.querySelector('form[method="post"][enctype="multipart/form-data"]');
  if (workForm) {
    workForm.addEventListener('submit', event => {
      // 如果用户没有通过前端选择图片，就走浏览器默认提交（后端依旧可以从 request.FILES 取）
      if (!selectedFiles || selectedFiles.length === 0) {
        return;
      }

      event.preventDefault();

      const formData = new FormData(workForm);

      formData.delete('images');

      // 把前端累计的图片统一追加到 images 字段（Django 中用 request.FILES.getlist('images') 获取）
      selectedFiles.forEach(file => {
        formData.append('images', file);
      });

      const actionUrl = workForm.getAttribute('action') || window.location.pathname;

      fetch(actionUrl, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
      })
        .then(response => {
          // 若后端重定向，则跳转到最终地址；否则刷新当前页
          if (response.redirected) {
            window.location.href = response.url;
          } else {
            return response.text().then(html => {
              // 简单地用返回的 HTML 替换当前文档
              document.open();
              document.write(html);
              document.close();
            });
          }
        })
        .catch(() => {
          alert('作品提交失败，请稍后重试。');
        });
    });
  }

  // ===== 价格设置：类型切换 =====
  const priceTypeRadios = document.querySelectorAll('input[name="price_type"]');
  const priceInputContainer = document.getElementById('price-input-container');
  const priceInput = document.getElementById('work-price');

  function updatePriceVisibility() {
    if (!priceInputContainer) return;
    let selected = null;
    priceTypeRadios.forEach(radio => {
      if (radio.checked) selected = radio.value;
    });

    if (selected === 'for_sale') {
      priceInputContainer.style.display = '';
    } else {
      priceInputContainer.style.display = 'none';
      if (priceInput) {
        priceInput.value = '';
      }
    }
  }

  if (priceTypeRadios.length > 0) {
    // 初始隐藏价格输入框（仅展示时）
    updatePriceVisibility();
    priceTypeRadios.forEach(radio => {
      radio.addEventListener('change', updatePriceVisibility);
    });
  }

  // ===== 作品标签选择与自定义添加 =====
  const tagButtons = document.querySelectorAll('.tag-btn');
  const selectedTagsContainer = document.getElementById('selected-tags');
  const customTagInput = document.getElementById('custom-tag');
  const addCustomTagBtn = document.getElementById('add-custom-tag');
  const tagsInputHidden = document.getElementById('tags-input');

  let selectedTags = [];

  function syncTagsToHiddenInput() {
    if (!tagsInputHidden) return;
    tagsInputHidden.value = JSON.stringify(selectedTags);
  }

  function renderSelectedTags() {
    if (!selectedTagsContainer) return;
    selectedTagsContainer.innerHTML = '';

    selectedTags.forEach(tag => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className =
        'px-3 py-1 bg-bluewhite text-white text-sm rounded-full flex items-center space-x-1 hover:bg-bluewhite/90 transition';
      chip.dataset.tag = tag;
      chip.innerHTML = `<span>${tag}</span><span class="ml-1 text-xs opacity-80">×</span>`;

      chip.addEventListener('click', () => {
        // 点击已选标签可移除
        selectedTags = selectedTags.filter(t => t !== tag);
        renderSelectedTags();
        syncTagsToHiddenInput();
      });

      selectedTagsContainer.appendChild(chip);
    });
  }

  function addTag(tag) {
    const cleanTag = tag.trim();
    if (!cleanTag) return;
    if (selectedTags.includes(cleanTag)) return;

    selectedTags.push(cleanTag);
    renderSelectedTags();
    syncTagsToHiddenInput();
  }

  function removeTag(tag) {
    selectedTags = selectedTags.filter(t => t !== tag);
    renderSelectedTags();
    syncTagsToHiddenInput();
  }

  // 预置标签按钮点击
  if (tagButtons.length > 0) {
    tagButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const tagText = btn.textContent.replace(/\s+/g, ' ').trim();
        if (selectedTags.includes(tagText)) {
          removeTag(tagText);
        } else {
          addTag(tagText);
        }
      });
    });
  }

  // 自定义标签添加
  function handleAddCustomTag() {
    if (!customTagInput) return;
    const value = customTagInput.value.trim();
    if (!value) return;
    addTag(value);
    customTagInput.value = '';
  }

  if (addCustomTagBtn) {
    addCustomTagBtn.addEventListener('click', handleAddCustomTag);
  }

  if (customTagInput) {
    customTagInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleAddCustomTag();
      }
    });
  }

  // 初始化隐藏字段，避免后端 json.loads 失败
  if (tagsInputHidden && !tagsInputHidden.value) {
    syncTagsToHiddenInput();
  }
});



import json
import os
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from PIL import Image

from .models import Work, WorkImage, Category, Tag, WorkTag


def appreciation(request):
    return render(request, 'appreciation/works_appreciation.html')


def appreciation_detail(request, pk):
    work = Work.objects.get(pk=pk)
    # 浏览量 +1
    work.views_count += 1
    work.save(update_fields=['views_count'])

    images = WorkImage.objects.filter(work=work)
    # 当前作品的标签列表
    tags = Tag.objects.filter(worktag__work=work).distinct()

    context = {
        'work': work,
        'images': images,
        'tags': tags,
    }
    return render(request, 'appreciation/appreciation_detail.html', context)


@login_required
def edit_work(request):
    """
    发布 / 编辑作品：接收表单数据，保存作品、图片与标签。
    图片物理文件保存到 static/img/work_images 目录下，数据库中保存相对路径。
    """
    if request.method == 'POST':
        # ---------- 1. 基本表单数据 ----------
        title = request.POST.get('title', '').strip()
        category_name = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        material = request.POST.get('material', '').strip()
        technique = request.POST.get('technique', '').strip()
        specification = request.POST.get('specification', '').strip()
        origin = request.POST.get('origin', '').strip()

        price_type = request.POST.get('price_type')
        raw_price = request.POST.get('price', '').strip()

        # 价格：仅在可销售时读取，否则为 0
        if price_type == 'for_sale' and raw_price:
            try:
                price = Decimal(raw_price)
            except Exception:
                price = Decimal('0.00')
        else:
            price = Decimal('0.00')

        # ---------- 2. 分类处理 ----------
        category = None
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)

        # ---------- 3. 创建作品对象 ----------
        work = Work.objects.create(
            user=request.user,
            category=category,
            title=title,
            description=description,
            material=material,
            technique=technique,
            specification=specification,
            origin=origin,
            is_salable=True if price_type == 'for_sale' else False,
            price=price,
            status='published',
        )

        # ---------- 4. 处理标签（JSON 数组） ----------
        tags_json = request.POST.get('tags', '[]')
        try:
            tags_list = json.loads(tags_json)
        except json.JSONDecodeError:
            tags_list = []

        if isinstance(tags_list, list):
            for tag_name in tags_list:
                name = str(tag_name).strip()
                if not name:
                    continue
                tag_obj, _ = Tag.objects.get_or_create(name=name)
                WorkTag.objects.create(work=work, tag=tag_obj)

        # ---------- 5. 处理图片上传 ----------
        images = request.FILES.getlist('images')

        # 物理文件保存目录：<项目根>/static/img/work_images
        base_dir = getattr(settings, 'BASE_DIR', None) or os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        save_dir = os.path.join(base_dir, 'static', 'img', 'work_images')
        os.makedirs(save_dir, exist_ok=True)

        for image_file in images:
            if not image_file:
                continue

            # 生成唯一文件名，统一使用 webp 后缀
            original_name = image_file.name
            name_root, _ext = os.path.splitext(original_name)
            safe_root = name_root[:50] or 'work_image'

            filename = f"{safe_root}_{work.id}.webp"
            save_path = os.path.join(save_dir, filename)

            # 使用 Pillow 转为 WEBP 格式后再保存到 static 目录
            try:
                img = Image.open(image_file)
                # 确保有 RGB 模式，避免某些模式不能直接保存 webp
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')

                img.save(save_path, format='WEBP', quality=85, method=6)
            except Exception:
                # 如果转换失败，跳过该图片，避免页面崩溃
                continue

            # 数据库存储相对路径（相对于 static 根目录）
            relative_path = os.path.join('img', 'work_images', filename).replace('\\', '/')

            WorkImage.objects.create(
                work=work,
                image=relative_path,
            )

        # ---------- 6. 跳转到作品详情页 ----------
        return redirect('appreciation:appreciation_detail', pk=work.id)

    # GET 请求：展示表单
    return render(request, 'appreciation/edit_work.html')

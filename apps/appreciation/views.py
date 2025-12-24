import json
import os
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from PIL import Image

from .models import Work, WorkImage, Category, Tag, WorkTag, Like, Comment, CommentLike
from utils.notification import create_like_notification, create_comment_notification, create_reply_notification


def appreciation(request):
    """
    作品社区列表页：
    - 单次仅加载固定数量作品（瀑布流 / 无限滚动）
    - 首屏渲染前 8 条，其余通过前端滚动懒加载
    - 右侧栏与评论区依旧使用静态展示
    """
    works_qs = (
        Work.objects.filter(status='published')
        .select_related('user', 'category')
        .prefetch_related('workimage_set')
        .prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.filter(parent=None).order_by('-likes_count', '-created_at'),
                to_attr='top_comments'
            )
        )
        .order_by('-created_at')
    )

    page = request.GET.get('page', 1)
    paginator = Paginator(works_qs, 8)  # 单次加载 8 条
    page_obj = paginator.get_page(page)

    # AJAX 请求：仅返回作品卡片 HTML 片段与分页信息
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'appreciation/_work_cards.html',
            {'works': page_obj.object_list},
            request=request,
        )
        return JsonResponse(
            {
                'html': html,
                'has_next': page_obj.has_next(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            }
        )

    # 普通请求：渲染首屏 + 初始化分页信息
    context = {
        'works': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'appreciation/works_appreciation.html', context)


def appreciation_detail(request, pk):
    work = Work.objects.get(pk=pk)
    author = work.user
    # 浏览量 +1
    work.views_count += 1
    work.save(update_fields=['views_count'])

    images = WorkImage.objects.filter(work=work)
    # 当前作品的标签列表
    tags = Tag.objects.filter(worktag__work=work).distinct()

    # 获取评论列表（仅顶级评论）
    comments = Comment.objects.filter(work=work, parent=None).select_related('user').prefetch_related('replies').order_by('-created_at')
    
    # 获取所有回复（包括间接回复）
    all_replies = Comment.objects.filter(work=work, parent__isnull=False).select_related('user', 'parent').order_by('created_at')

    # 检查当前用户是否已点赞该作品
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(work=work, user=request.user).exists()

    context = {
        'work': work,
        'images': images,
        'tags': tags,
        'author': author,
        'is_liked': is_liked,
        'comments': comments,
        'all_replies': all_replies,
    }
    return render(request, 'appreciation/appreciation_detail.html', context)


@login_required
def edit_work(request, pk=None):
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

        # ---------- 3. 创建 / 更新作品对象 ----------
        if pk:
            # 编辑已有作品，限制只能编辑自己的作品
            work = get_object_or_404(Work, pk=pk, user=request.user)
            work.category = category
            work.title = title
            work.description = description
            work.material = material
            work.technique = technique
            work.specification = specification
            work.origin = origin
            work.is_salable = True if price_type == 'for_sale' else False
            work.price = price
            work.status = 'published'
            work.save()
        else:
            # 新建作品
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
            # 编辑模式下，先清空原有标签关系
            if pk:
                WorkTag.objects.filter(work=work).delete()

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
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')

                # 将处理后的图片存入内存
                img_buffer = BytesIO()
                img.save(img_buffer, format='WEBP', quality=85, method=6)
                img_buffer.seek(0)  # 移动到缓冲区开头

                # 用Django的ContentFile包装缓冲区内容
                django_file = ContentFile(img_buffer.read(), name=filename)

                # 创建WorkImage，让ImageField自动保存文件到MEDIA_ROOT
                WorkImage.objects.create(
                    work=work,
                    image=django_file  # 直接传入处理后的文件
                )
            except Exception:
                continue  # 处理失败则跳过

        # ---------- 6. 跳转到作品详情页 ----------
        return redirect('appreciation:appreciation_detail', pk=work.id)

    # GET 请求：展示表单（如果 pk 存在则为编辑模式）
    work = None
    work_tags = []
    if pk:
        work = get_object_or_404(Work, pk=pk, user=request.user)
        work_tags = list(
            Tag.objects.filter(worktag__work=work).values_list('name', flat=True)
        )

    context = {
        'work': work,
        'work_tags': work_tags,
    }
    return render(request, 'appreciation/edit_work.html', context)


@login_required
def delete_work(request, pk):
    """删除作品，仅允许作者本人删除"""
    work = get_object_or_404(Work, pk=pk, user=request.user)
    if request.method == 'POST':
        work.delete()
        # 删除后返回个人中心
        return redirect('user:profile')

    # GET 访问时简单重定向到作品详情，避免误删
    return redirect('appreciation:appreciation_detail', pk=pk)


# 添加点赞/取消点赞视图
@login_required
def toggle_like(request, pk):
    """处理作品点赞/取消点赞功能"""
    try:
        work = Work.objects.get(pk=pk)
        user = request.user

        # 检查用户是否已经点赞
        like, created = Like.objects.get_or_create(work=work, user=user)

        if not created:
            # 如果已经点赞，则取消点赞
            like.delete()
            work.likes_count -= 1
            is_liked = False
        else:
            # 如果未点赞，则添加点赞
            work.likes_count += 1
            is_liked = True
            # 创建点赞通知
            create_like_notification(user, work)

        # 保存作品点赞数
        work.save(update_fields=['likes_count'])

        # 返回JSON响应
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': work.likes_count
        })
    except Work.DoesNotExist:
        return JsonResponse({'success': False, 'error': '作品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# 评论视图
@login_required
def add_comment(request, pk):
    """处理添加评论功能"""
    try:
        work = Work.objects.get(pk=pk)
        user = request.user
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')

        if not content:
            return JsonResponse({'success': False, 'error': '评论内容不能为空'})

        # 创建评论
        comment_data = {
            'work': work,
            'user': user,
            'content': content
        }

        # 如果是回复评论
        if parent_id:
            try:
                parent_comment = Comment.objects.get(pk=parent_id, work=work)
                comment_data['parent'] = parent_comment
            except Comment.DoesNotExist:
                return JsonResponse({'success': False, 'error': '回复的评论不存在'})

        comment = Comment.objects.create(**comment_data)

        # 更新作品评论数
        work.comments_count += 1
        work.save(update_fields=['comments_count'])

        # 创建通知
        if comment.parent:
            # 如果是回复，创建回复通知
            create_reply_notification(user, comment)
        else:
            # 如果是新评论，创建评论通知
            create_comment_notification(user, comment)

        # 返回新评论的HTML（用于前端动态添加）
        if comment.parent:
            # 如果是回复，渲染为回复样式，而不是完整的评论样式
            comment_html = render_to_string(
                'appreciation/_reply.html',
                {'reply': comment, 'parent_comment': comment.parent, 'request': request},
                request=request
            )
        else:
            # 如果是顶级评论，渲染为完整的评论样式
            comment_html = render_to_string(
                'appreciation/_comment.html',
                {'comment': comment, 'user': user, 'request': request},
                request=request
            )

        return JsonResponse({
            'success': True,
            'comment_html': comment_html,
            'comments_count': work.comments_count
        })
    except Work.DoesNotExist:
        return JsonResponse({'success': False, 'error': '作品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# 评论点赞/取消点赞视图
@login_required
def toggle_comment_like(request, comment_id):
    """处理评论点赞/取消点赞功能"""
    try:
        comment = Comment.objects.get(pk=comment_id)
        user = request.user

        # 检查用户是否已经点赞
        comment_like, created = CommentLike.objects.get_or_create(comment=comment, user=user)

        if not created:
            # 如果已经点赞，则取消点赞
            comment_like.delete()
            comment.likes_count -= 1
            is_liked = False
        else:
            # 如果未点赞，则添加点赞
            comment.likes_count += 1
            is_liked = True

        # 保存评论点赞数
        comment.save(update_fields=['likes_count'])

        # 返回JSON响应
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': comment.likes_count
        })
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': '评论不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# 获取评论列表视图（用于分页加载）
def get_comments(request, pk):
    """获取作品评论列表，支持分页"""
    try:
        work = Work.objects.get(pk=pk)
        page = request.GET.get('page', 1)

        # 获取顶级评论（不包含回复）
        comments = Comment.objects.filter(work=work, parent=None).select_related('user').prefetch_related('replies').order_by('-created_at')

        paginator = Paginator(comments, 10)  # 每页10条评论
        page_obj = paginator.get_page(page)

        # 渲染评论列表HTML
        comments_html = render_to_string(
            'appreciation/_comments_list.html',
            {'comments': page_obj.object_list, 'request': request},
            request=request
        )

        return JsonResponse({
            'success': True,
            'comments_html': comments_html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None
        })
    except Work.DoesNotExist:
        return JsonResponse({'success': False, 'error': '作品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def delete_comment(request, comment_id):
    """删除评论及所有子评论，仅允许作者本人删除"""
    try:
        # 获取评论对象
        comment = get_object_or_404(Comment, pk=comment_id)
        
        # 检查是否为评论作者
        if comment.user != request.user:
            return JsonResponse({'success': False, 'error': '无权限删除该评论'}, status=403)
        
        # 获取评论所属作品
        work = comment.work
        
        # 计算要删除的评论数量（包括当前评论和所有子评论）
        comments_to_delete = [comment.id]
        
        # 递归获取所有子评论
        def get_all_replies(comment):
            for reply in comment.replies.all():
                comments_to_delete.append(reply.id)
                get_all_replies(reply)
        
        get_all_replies(comment)
        
        # 批量删除评论
        Comment.objects.filter(id__in=comments_to_delete).delete()
        
        # 更新作品评论数
        work.comments_count = max(0, work.comments_count - len(comments_to_delete))
        work.save(update_fields=['comments_count'])
        
        return JsonResponse({
            'success': True,
            'comment_id': comment_id,
            'comments_count': work.comments_count
        })
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': '评论不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
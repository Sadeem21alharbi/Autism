from django.shortcuts import render, redirect ,get_object_or_404
from django.http import HttpRequest, HttpResponse
from .forms import PostForm, CommentForm
from django.db.models import Q,Count
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Post, Like, Comment, CommentLike,Report
from django.contrib.auth.models import User
from django.contrib import messages
# Create your views here.

def community_view (request:HttpResponse):
    posts = Post.objects.all().order_by('-created_at')
    sleep_count = Post.objects.filter(category='sleep').count()
    food_count = Post.objects.filter(category='food').count()
    play_count = Post.objects.filter(category='play').count()
    education_count = Post.objects.filter(category='education').count()
    search = request.GET.get('search')
    if search:
        posts = posts.filter(
        Q(title__icontains=search) |
        Q(content__icontains=search) |
        Q(tags__icontains=search)|
        Q(user__first_name__icontains=search)
        )
    for post in posts:
        post.tags_list = post.tags.split(',')

    return render (request, 'community/community_feed.html', {
        'posts': posts,
        'sleep_count': sleep_count,
        'food_count': food_count,
        'play_count': play_count,
        'education_count': education_count,
        'reasons': Report.REASONS
        })

def create_post_view(request: HttpRequest):

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            messages.success(request, "تم نشر المنشور بنجاح")
            return redirect('community:community_view')

        else:
            print(form.errors)

    else:
        form = PostForm()

    return render(request, 'community/create_post.html', {'form': form})
def details_post_view(request:HttpRequest, post_id):

    post = get_object_or_404(Post, id=post_id)
    post.tags_list = post.tags.split(',')

    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(post=post, user=request.user).exists()

    
    comments = Comment.objects.filter(post=post)

    
    if request.user.is_authenticated:
        liked_comment_ids = CommentLike.objects.filter(
            user=request.user,
            comment__post=post
        ).values_list('comment_id', flat=True)

        for comment in comments:
            comment.is_liked = comment.id in liked_comment_ids

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, "تم إضافة التعليق بنجاح")

            return redirect('community:details_post_view', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'community/details_post.html', {
        'post': post,
        'form': form,
        'is_liked': is_liked,
        'comments': comments,   
        'reasons': Report.REASONS
    })
def posts_by_tag(request:HttpRequest, tag_name):

    posts = Post.objects.filter(tags__icontains=tag_name)
    return render(request, 'community/posts_by_tag.html', {'posts': posts, 'tag_name': tag_name,})

  
def like_post_view(request:HttpRequest, post_id):

    post = get_object_or_404(Post, id=post_id)

    like_obj = Like.objects.filter(post=post, user=request.user)

    if like_obj.exists():
        like_obj.delete()
        messages.success(request, "تم إزالة الإعجاب")

    else:
        Like.objects.create(post=post, user=request.user)
        messages.success(request, "تم الإعجاب بالمنشور")


    return redirect(request.META.get('HTTP_REFERER', 'community:community_view'))

def edit_post_view(request:HttpRequest, post_id):

    post = get_object_or_404(Post,id=post_id,user=request.user)

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل المنشور بنجاح")

            return redirect('community:details_post_view',post_id=post.id)

    else:
        form = PostForm(instance=post)

    return render(request,'community/edit_post.html',{'form': form})

def delete_post_view(request:HttpRequest, post_id):
    post = get_object_or_404(Post,id=post_id,user=request.user)
    post.delete()
    messages.success(request, "تم حذف المنشور")


    return redirect('community:community_view')


def edit_comment_view(request:HttpRequest, comment_id):

    comment = get_object_or_404(Comment,id=comment_id,user=request.user)

    if request.method == 'POST':
        comment.content = request.POST.get('content')
        comment.save()
        messages.success(request, "تم تعديل التعليق بنجاح")


    return redirect('community:details_post_view',post_id=comment.post.id)


def delete_comment_view(request:HttpRequest, comment_id):

    comment = get_object_or_404(Comment,id=comment_id,user=request.user)
    post_id = comment.post.id
    comment.delete()
    messages.success(request, "تم حذف التعليق بنجاح")


    return redirect('community:details_post_view',post_id=post_id)


@login_required
def likes_view(request):
    liked_posts = Post.objects.filter(
        likes__user=request.user
    ).annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    ).order_by('-created_at')

    liked_comments = Comment.objects.filter(
        comment_likes__user=request.user
    ).annotate(
        likes_count=Count('comment_likes', distinct=True)
    ).order_by('-created_at')

    return render(request, 'community/likes.html', {
        'liked_posts': liked_posts,
        'liked_comments': liked_comments,
        'liked_posts_count': liked_posts.count(),
        'liked_comments_count': liked_comments.count(),
    })


@login_required
def like_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    like_obj = CommentLike.objects.filter(comment=comment, user=request.user)

    if like_obj.exists():
        like_obj.delete()  
        messages.success(request, "تم إزالة الإعجاب من التعليق")

    else:
        CommentLike.objects.create(comment=comment, user=request.user)  
        messages.success(request, "تم الإعجاب بالتعليق")

    return redirect(request.META.get('HTTP_REFERER') or 'community:community_view')


@login_required
def user_posts_view(request, user_id):

    user = get_object_or_404(User, id=user_id)

    posts = Post.objects.filter(user=user).order_by('-created_at')
    posts_count = posts.count()

    return render(request, 'community/user_posts.html', {
        'profile_user': user,
        'posts': posts,
        'posts_count': posts_count,
    })
def report_post(request:HttpRequest, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':

        reason = request.POST.get('reason')
        already_reported = Report.objects.filter(user=request.user,post=post).exists()

        if not already_reported:
            Report.objects.create(user=request.user,post=post,reason=reason)
            messages.success(request, "تم إرسال البلاغ")
        else:
            messages.info(request, "لقد قمت بالإبلاغ عن هذا المنشور مسبقًا")
    return redirect('community:community_view')



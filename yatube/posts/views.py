from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'page': page, 'paginator': paginator}
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author__username=username)
    paginator = Paginator(posts, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts_count = Post.objects.filter(author=author).count()
    following = Follow.objects.filter(author=author)
    context = {
        'author': author,
        'page': page,
        'paginator': paginator,
        'posts_count': posts_count,
        'following': following,
    }
    return render(
        request,
        'profile.html',
        context=context
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()
    following = Follow.objects.filter(author=post.author.id,
                                      user=request.user.id)
    followers = post.author.following.count()
    follow = post.author.follower.count()
    form = CommentForm(request.POST or None)
    context = {'post': post,
               'author': post.author,
               'form': form,
               'comments': comments,
               'following': following,
               'followers': followers,
               'follow': follow
               }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post_edit = get_object_or_404(Post, pk=post_id, author__username=username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_edit
    )

    if request.user != post_edit.author:
        return redirect('post', username, post_id)

    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)

    return render(request, 'new.html', {'form': form, 'edit': post_edit})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404,
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    user_follows = User.objects.get(
        pk=request.user.id).follower.all().values_list('author')
    post_list = Post.objects.filter(author__in=user_follows)
    paginator = Paginator(post_list, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect('profile', username=username)

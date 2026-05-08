from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from .models import Post, Comment, Profile
from .models import Post
from .forms import PostForm
from .forms import ProfileUpdateForm
from django.db.models import Q

def like_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect('login')

    post = get_object_or_404(Post, id=post_id)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect('index')


def index(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'network/index.html', {
        'posts': posts,
        'form': form
    })


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'network/register.html'
    success_url = reverse_lazy('login')


def profile_view(request, username):
    user_profile = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user_profile).order_by('-created_at')

    return render(request, 'network/profile.html', {
        'user_profile': user_profile,
        'posts': user_posts,
    })


def add_comment(request, post_id):
    if request.method == "POST" and request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content")
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.author or request.user == comment.post.author:
        comment.delete()

    return redirect(request.META.get('HTTP_REFERER', 'index'))


def profile_follow(request, username):
    if not request.user.is_authenticated:
        return redirect('login')

    user_to_follow = get_object_or_404(User, username=username)

    my_profile = request.user.profile
    target_profile = user_to_follow.profile

    if my_profile == target_profile:
        return redirect('profile', username=username)

    if target_profile in my_profile.follows.all():
        my_profile.follows.remove(target_profile)
    else:
        my_profile.follows.add(target_profile)

    return redirect('profile', username=username)

def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'network/edit_profile.html', {'form': form})


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.author:
        post.delete()

    return redirect('index')


def search_users(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = User.objects.filter(Q(username__icontains=query))

    return render(request, 'network/search_results.html', {
        'results': results,
        'query': query
    })
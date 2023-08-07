from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from taggit.models import Tag

from django.db.models import Count


def post_share(request, post_id):
    post = get_object_or_404(Post, id= post_id, status= Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            #  ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                    f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'raisanj6@gmail.com', [cd['to']])
            sent = True

    else:
        form = EmailPostForm()

    return render(request, 'post/share.html', {'post':post, 'form':form, 'sent':sent})

            # "build_absolute_uri" create absolute URL. While, 
            # "get_absolute_url" create relative URL



# class PostListView(ListView):
#     # alternative to post_list view:
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'post/list.html'

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug= tag_slug)
        post_list = post_list.filter(tags__in =[tag])

    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page',1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # if page_number is out of range deliver last page as result
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # if page_number != integer, return first page
        posts = paginator.page(1)

    return render(request, 'post/list.html',{'posts':posts, 'tag':tag})


# def post_detail(request, year, month, day, post, image):
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                            status = Post.Status.PUBLISHED,
                            publish__year = year, 
                            publish__month = month,
                            publish__day = day,
                            slug = post)

    # image = post.image

    # queryset to List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    return render(request,'post/detail.html',
                    {'post': post,
                    'comments': comments,
                    'form': form,
                    'similar_posts':similar_posts})

# def post_detail(request, id):
#     post = get_object_or_404(Post, id=id, status = Post.Status.PUBLISHED)
#     return render(request, 'post/detail.html',{'post':post})

# def post_detail(request, id):
#     try:
#         post = Post.published.get(id=id)
#     except Post.DoesNotExist:
#         raise Http404("No post found")
#     return render(request, 'blog/post/detail.html',{'post':post})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
    # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
    # Assign the post to the comment
        comment.post = post
    # Save the comment to the database
        comment.save()
    return render(request, 'post/comment.html',
                        {'post': post,
                        'form': form,
                        'comment': comment})


# Building a search view

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

def post_search(request):
    form = SearchForm
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector('title', 'body', config='spanish')
            search_vector = SearchVector('title', weight='A') +  SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            # results = Post.published.annotate(search=SearchVector('title','body'),
            results = Post.published.annotate(
                similarity = TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
            # results = Post.published.annotate(
            #     search=search_vector,
            #     rank = SearchVector(search_vector, search_query),
            # ).filter(rank__gte=0.3).order_by('-rank')
            # ).filter(search=search_query).order_by('-rank')

    return render(request, 'post/search.html',
                    {'form':form,
                    'query':query,
                    'results':results})




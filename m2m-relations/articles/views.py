from django.shortcuts import render, get_object_or_404
from .models import Article, Tag 


def articles_list(request):
    articles = Article.objects.all()
    for article in articles:
        article.main_scope = article.scopes.filter(is_main=True).first()
        article.other_scopes = article.scopes.filter(is_main=False).order_by('tag__name')  # Corrected line
    return render(request, 'articles/articles_list.html', {'articles': articles})


def tag_detail(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    return render(request, 'articles/tag_detail.html', {'tag': tag})
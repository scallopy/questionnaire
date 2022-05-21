from .models import Category


def list_category_nav(request):
    categories = Category.objects.all()
    for category in categories:
        slug = category.slug
    context = {
        'categories': categories,
        'slug': slug,
    }
    return context

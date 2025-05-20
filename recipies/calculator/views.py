from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse

DATA = {
    'omlet': {
        'яйца, шт': 2,
        'молоко, л': 0.1,
        'соль, ч.л.': 0.5,
    },
    'pasta': {
        'макароны, г': 0.3,
        'сыр, г': 0.05,
    },
    'buter': {
        'хлеб, ломтик': 1,
        'масло, г': 20,
        'колбаса, ломтик': 1,
    },
    # можете добавить свои рецепты
}


def recipe_list(request):
    recipes = list(DATA.keys())  # Получаем список названий рецептов
    context = {'recipes': recipes}
    return render(request, 'calculator/recipe_list.html', context)


def recipe_view(request, recipe_name):
    servings = request.GET.get('servings')
    try:
        recipe = DATA[recipe_name]
    except KeyError:
        return HttpResponse("Рецепт не найден", status=404)

    if servings:
        try:
            servings = int(servings)
            if servings <= 0:
                return HttpResponse("Количество порций должно быть положительным числом.", status=400)
        except ValueError:
            return HttpResponse("Некорректное количество порций.", status=400)

        context = {
            'recipe': {ingredient: quantity * servings for ingredient, quantity in recipe.items()}
        }
    else:
        context = {
            'recipe': recipe
        }

    context['recipe_name'] = recipe_name  # Передаем имя рецепта в контекст
    return render(request, 'calculator/recipe.html', context)
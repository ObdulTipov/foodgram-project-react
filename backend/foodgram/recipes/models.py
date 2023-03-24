from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

FIRST_TEXT_SYM = 15


class Ingredient(models.Model):
    name = models.TextField(
        verbose_name='Название',
        help_text='Введите название ингридиента',
        max_length=200,
        blank=True,
    )
    amount = models.PositiveSmallIntegerField(blank=True,)
    unit = models.TextField(
        verbose_name='Единица измерения',
        max_length=200,
        blank=True,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name[:FIRST_TEXT_SYM]


class Tag(models.Model):
    COLOR_PALETTE = [
        ('#A9A9A9', 'DarkGray'),
        ('#FA8072', 'Salmon'),
        ('#FFB6C1', 'LightPink'),
        ('#FFA500', 'Orange'),
        ('#FFD700', 'Gold'),
        ('#D8BFD8', 'Thistle'),
        ('#98FB98', 'PaleGreen'),
        ('#AFEEEE', 'PaleTurquoise'),
        ('#66CDAA', 'MediumAquamarine'),
    ]
    name = models.TextField(
        verbose_name='Название',
        help_text='Введите название ингридиента',
        max_length=200,
        unique=True,
        blank=True,
    )
    color = models.CharField(
        choices=COLOR_PALETTE,
        default='#A9A9A9',
        blank=True,
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True,)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name[:FIRST_TEXT_SYM]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.TextField(
        verbose_name='Название',
        max_length=200,
        help_text='Введите название рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        help_text='Изображение готового блюда',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        # through='Ingredient',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, минут',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.name[:FIRST_TEXT_SYM]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['user']


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['user']


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок по рецепту'
        verbose_name_plural = 'Списоки покупок по рецептам'
        ordering = ['user']

from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products" , verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название продукта")
    description = models.TextField(blank=True, verbose_name="Описание продукта")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        PROCESSING = "processing", "В обработке"
        SHIPPED = "shipped", "Отправлен"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders", verbose_name="Пользователь")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW     , verbose_name="Статус заказа")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0 , verbose_name="Общая стоимость")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    def __str__(self):
        return f"Заказ #{self.pk}"  
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
        
    class Meta  :
            verbose_name = "Элемент заказа"
            verbose_name_plural = "Элементы заказов"

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews", verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Продукт")
    rating = models.PositiveSmallIntegerField(verbose_name="Рейтинг")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_user_product_review")]
    def __str__(self):
        return f"{self.product.name}: {self.rating}/5"
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

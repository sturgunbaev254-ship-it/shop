from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, Review

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Этот email уже используется.")
        return value
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    class Meta:
        model = Product
        fields = ["id", "category", "category_name", "name", "description", "price", "stock", "created_at"]

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
    def validate(self, attrs):
        request = self.context.get("request")
        product = attrs.get("product", getattr(self.instance, "product", None))
        if request and request.user.is_authenticated and product:
            qs = Review.objects.filter(user=request.user, product=product)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Вы уже оставили отзыв на этот товар.")
        return attrs

class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

class OrderItemReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]

class OrderReadSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    items = OrderItemReadSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_price", "items", "created_at"]
        read_only_fields = fields

class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, allow_empty=False)
    def validate_items(self, value):
        ids = [item["product"].pk for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Добавляйте каждый товар одной строкой.")
        return value
    def create(self, validated_data):
        user = self.context["request"].user
        with transaction.atomic():
            checked_items = []
            for item in validated_data["items"]:
                product = Product.objects.select_for_update().get(pk=item["product"].pk)
                quantity = item["quantity"]
                if product.stock < quantity:
                    raise serializers.ValidationError({"items": f"Недостаточно товара «{product.name}». Остаток: {product.stock}."})
                checked_items.append((product, quantity))
            order = Order.objects.create(user=user, total_price=Decimal("0.00"))
            total = Decimal("0.00")
            for product, quantity in checked_items:
                price = product.price
                product.stock -= quantity
                product.save(update_fields=["stock"])
                OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
                total += price * quantity
            order.total_price = total
            order.save(update_fields=["total_price"])
            if user.email:
                def send_confirmation():
                    send_mail(
                        subject=f"Заказ №{order.pk} оформлен",
                        message=f"Здравствуйте, {user.username}!\nНомер заказа: {order.pk}\nСумма: {order.total_price}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                transaction.on_commit(send_confirmation)
        return order

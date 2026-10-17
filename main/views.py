from django.db import transaction
from django.db.models import F
from django.contrib.auth import authenticate
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import Category, Product, Order, Review
from .serializers import RegisterSerializer, CategorySerializer, ProductSerializer, OrderCreateSerializer, OrderReadSerializer, ReviewSerializer
from .permissions import IsAdminOrReadOnly, IsReviewOwnerOrReadOnly
from .filters import ProductFilter

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        user = authenticate(request, username=request.data.get("username", ""), password=request.data.get("password", ""))
        if user is None:
            return Response({"detail": "Неверное имя пользователя или пароль."}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.auth:
            request.auth.delete()
        return Response({"detail": "Вы вышли из аккаунта."})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["name", "price", "created_at"]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "product").all().order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product").order_by("-created_at")
    def get_serializer_class(self):
        return OrderCreateSerializer if self.action == "create" else OrderReadSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderReadSerializer(order, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            order = self.get_object()
            order = Order.objects.select_for_update().get(pk=order.pk, user=request.user)
            if order.status != Order.Status.NEW:
                return Response({"detail": "Этот заказ уже нельзя отменить."}, status=status.HTTP_400_BAD_REQUEST)
            for item in order.items.all():
                Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status"])
        return Response(OrderReadSerializer(order, context=self.get_serializer_context()).data)

from rest_framework import viewsets, generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Product, Cart, CartItem, Category
from .serializers import ProductSerializer, CartSerializer, \
    UserRegistrationSerializer, CategorySerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by('id')  # Упорядочиваем товары
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination  # Включаем пагинацию
# Управление корзиной
class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):

        cart = request.user.cart
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID товара'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество товара', default=1),
            },
            required=['product_id'],
        ),
        responses={
            200: 'Товар успешно добавлен в корзину',
            404: 'Товар не найден',
        },
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):

        cart = request.user.cart
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)  # По умолчанию 1

        # Проверяем, существует ли товар
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Добавляем товар в корзину или обновляем количество
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        return Response({'status': 'Product added to cart'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID товара'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Новое количество товара'),
            },
            required=['product_id', 'quantity'],
        ),
        responses={
            200: 'Количество товара обновлено',
            404: 'Товар не найден в корзине',
            400: 'Некорректное количество',
        },
    )
    @action(detail=False, methods=['put'])
    def update_item(self, request):

        cart = request.user.cart
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        # Проверяем, существует ли товар в корзине
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)


        if quantity is not None and quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'status': 'Product quantity updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID товара'),
            },
            required=['product_id'],
        ),
        responses={
            204: 'Товар удален из корзины',
            404: 'Товар не найден в корзине',
        },
    )
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):

        cart = request.user.cart
        product_id = request.data.get('product_id')


        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)


        cart_item.delete()
        return Response({'status': 'Product removed from cart'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def clear_cart(self, request):

        cart = request.user.cart
        cart.cartitem_set.all().delete()
        return Response({'status': 'Cart cleared'}, status=status.HTTP_204_NO_CONTENT)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Количество элементов на странице
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().prefetch_related('subcategories')
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
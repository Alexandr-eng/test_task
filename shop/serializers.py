from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, SubCategory, Product, Cart, CartItem




class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='subcategory.category.name', read_only=True)
    subcategory = serializers.CharField(source='subcategory.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'category', 'subcategory', 'price', 'image_small', 'image_medium', 'image_large']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_items']

    def get_total_price(self, obj):
        return obj.total_price()

    def get_total_items(self, obj):
        return obj.total_items()



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'slug']

class CategorySerializer(serializers.ModelSerializer):

    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'subcategories']

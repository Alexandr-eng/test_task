

from rest_framework.test import APITestCase  # Импортируем APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Product, Category, SubCategory

class ProductListViewTest(APITestCase):
    def setUp(self):


        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
        )

        self.subcategory = SubCategory.objects.create(
            name='Test SubCategory',
            slug='test-subcategory',
            category=self.category,
        )
        # Создаем 15 товаров
        for i in range(15):
            Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100.00 + i,
                image_small=f'products/small/image{i}.jpg',
                image_medium=f'products/medium/image{i}.jpg',
                image_large=f'products/large/image{i}.jpg',
                subcategory=self.subcategory,  # Указываем подкатегорию
            )
        self.url = reverse('product-list')  # URL для списка товаров

    def test_get_product_list_with_pagination(self):

        response = self.client.get(self.url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)


        response = self.client.get(self.url, {'page': 2})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
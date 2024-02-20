from django.urls import path

from main.views import expense_category_views, index

urlpatterns = [
  path('', index.index),
  path('expenses/categories/', expense_category_views.ExpenseCategoryAPIView.as_view())
]
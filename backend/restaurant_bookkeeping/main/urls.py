from django.urls import path

from main.views import expense_category_views, outlet_views, index

urlpatterns = [
  path('', index.index),
  path('expenses/categories/', expense_category_views.ExpenseCategoryAPIView.as_view()),
  path('expenses/categories/<int:id>/', expense_category_views.ExpenseCategoryAPIView.as_view(), name='api_specific_expense_category'),
  path('expenses/categories/<int:id>/delete/', expense_category_views.ExpenseCategoryAPIView.as_view()),

  path('outlets/', outlet_views.OutletView.as_view()),
  path('outlets/<int:id>/', outlet_views.OutletView.as_view()),
  
]
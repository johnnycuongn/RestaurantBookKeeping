from django.urls import path

from main.views import expense_category_views, outlet_views, payment_account_views, payee_views, index

urlpatterns = [
  path('', index.index),
  path('expenses/categories/', expense_category_views.ExpenseCategoryAPIView.as_view()),
  path('expenses/categories/<int:id>/', expense_category_views.ExpenseCategoryAPIView.as_view(), name='api_specific_expense_category'),
  path('expenses/categories/<int:id>/delete/', expense_category_views.ExpenseCategoryAPIView.as_view()),

  path('outlets/', outlet_views.OutletView.as_view()),
  path('outlets/<int:id>/', outlet_views.OutletView.as_view()),

  path('payments/', payment_account_views.PaymentAccountView.as_view()),
  path('payments/<int:id>', payment_account_views.PaymentAccountView.as_view()),

  path('payees/', payee_views.PayeeView.as_view()),
  path('payees/<int:id>', payee_views.PayeeView.as_view())
  
]
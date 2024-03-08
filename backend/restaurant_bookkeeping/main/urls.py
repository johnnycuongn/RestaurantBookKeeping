from django.urls import path

from main.views import expense_category_views, outlet_views, payment_account_views, payee_views, expense_view, index

urlpatterns = [
  path('', index.index),
  path('expenses/categories/', expense_category_views.ExpenseCategoryAPIView.as_view()),
  path('expenses/categories/<int:id>/', expense_category_views.ExpenseCategoryAPIView.as_view(), name='api_specific_expense_category'),
  path('expenses/categories/<int:id>/delete/', expense_category_views.ExpenseCategoryAPIView.as_view()),

  path('outlets/', outlet_views.OutletView.as_view()),
  path('outlets/<int:id>/', outlet_views.OutletView.as_view()),
  path('outlets/<int:id>/delete/', outlet_views.OutletView.as_view()),

  path('payments/', payment_account_views.PaymentAccountView.as_view()),
  path('payments/<int:id>/', payment_account_views.PaymentAccountView.as_view()),
  path('payments/<int:id>/delete/', payment_account_views.PaymentAccountView.as_view()),

  path('payees/', payee_views.PayeeView.as_view()),
  path('payees/<uuid:id>/', payee_views.PayeeView.as_view()),
  path('payees/<uuid:id>/delete/', payee_views.PayeeView.as_view()),

  path('expenses/', expense_view.ExpenseGetView.as_view()),
  path('expenses/<uuid:id>/', expense_view.ExpenseGetView.as_view()),
  path('expenses/create/', expense_view.ExpensePostView.as_view()),
  path('expenses/edit/', expense_view.ExpensePostView.as_view()),
  path('expenses/delete/', expense_view.ExpensePostView.as_view())
  
]
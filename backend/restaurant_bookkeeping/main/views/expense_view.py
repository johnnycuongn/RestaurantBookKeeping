import json
from typing import Any
from django.http.response import HttpResponse as HttpResponse
from django.views import View
from django.views.generic.list import ListView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from datetime import datetime, date

from ..models import Expense, ExpenseCategory, Outlet, Payee, PaymentAccount


class ExpenseGetView(ListView):

  model = Expense
  queryset = Expense.objects.all()

  def get_queryset(self):
    queryset = super().get_queryset()

    url_query_keys = self.request.GET.keys()

    if 'year' in url_query_keys:
      print("There is year in ", url_query_keys)

    if self.kwargs.get('id', None) is not None:
      query = queryset.filter(id=self.kwargs.get('id'))
      return query.all()
    
      
    return queryset

  def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
    
    data_list = list(self.object_list.values())

    return JsonResponse(data_list, safe=False)

  def get(self, request, *args, **kwargs):
    print('Get request', request, str(args), str(kwargs))
    return super().get(request, *args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch') 
class ExpensePostView(View):

  model = Expense

  def post(self, request, *args, **kwargs):
    
    data = json.loads(request.body)

    if request.path.endswith('create/'):
      # TODO: request.user
      if not data.get('owner', ''):
        return JsonResponse({'error': 'Owner is required'}, status=400)
      if not data.get('outlet', ''):
        return JsonResponse({'error': 'Outlet is required'}, status=400)
      if not data.get('payee', ''):
        return JsonResponse({'error': 'Payee is required'}, status=400)
      if not data.get('payment', ''):
        return JsonResponse({'error': 'Payment is required'}, status=400)
      if not data.get('total_amount', ''):
        return JsonResponse({'error': 'Total amount is required. Property "total_amount" should not be empty.'}, status=400)
      if not data.get('main_category', ''):
        return JsonResponse({'error': 'Main category is required. Property "main_category" should not be empty.'}, status=400)
      if not data.get('category', ''):
        return JsonResponse({'error': 'Sub category is required. Property "category" should not be empty.'}, status=400)
      
      user_query = get_user_model().objects.filter(id=data.get('owner'))
      if not user_query.exists():
        return JsonResponse({'error': 'Invalid User'})

      outlet_query = Outlet.objects.filter(id=data.get('outlet'))
      if not outlet_query.exists():
        return JsonResponse({'error': 'Outlet doesn\'t exist'})
      
      payee_query = Payee.objects.filter(id=data.get('payee'))
      if not payee_query.exists():
        return JsonResponse({'error': f'Payee with id doesn\'t exists'}, status=400)
      
      payment_query = PaymentAccount.objects.filter(id=data.get('payment'))
      if not payment_query.exists():
        return JsonResponse({'error': f'Payment account with id doesn\'t exists'}, status=400)
      
      category_query = ExpenseCategory.objects.filter(id=data.get('category'))
      if not category_query.exists():
        return JsonResponse({'error': 'Category doesnt exist'}, status=400)

      creating_expense_data = {
        'owner': user_query.first(),
        'outlet': outlet_query.first(),
        'payee': payee_query.first(),
        'payment_date': date.today(),
        'payment': payment_query.first(),
        'payment_status': 'pending',
        'total_amount': data.get('total_amount'),
        'main_category': data.get('main_category'),
        'category': category_query.first(),
        'note': data.get('note', '')
      }

      self.model.objects.create(**creating_expense_data)

      return JsonResponse({}, status=201)
        
    elif request.path.endswith('update/'):
      if not data.get('id', ''):
        return JsonResponse({'error': 'ID is required.'})
    elif request.path.endswith('delete/'):
      return JsonResponse({'error': 'Delete'}, status=400)

    return JsonResponse({'error': 'Invalid URL'}, status=400)
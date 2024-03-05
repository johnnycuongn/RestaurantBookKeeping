from django.views import View
from django.http import JsonResponse
from django.db import IntegrityError

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json

from .expense_category_views import ExpenseCategoryAPIView
from .payment_account_views import PaymentAccountView

from ..models import Payee, ExpenseCategory, PaymentAccount

@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF for simplicity
class PayeeView(View):

  objects = Payee.objects
  display_name = 'Payment Account'

  @staticmethod
  def serialize(object: Payee):
      
    data = {
        'id': object.id,
        'name': object.name,
        'description': object.description,
        'contact_number': object.contact_number,
    }

    if object.default_expense_category is not None:
      try:
        category = ExpenseCategory.objects.get(id=object.default_expense_category.id)
        data["default_expense_category"] = ExpenseCategoryAPIView.serialize(category)
      except ExpenseCategory.DoesNotExist:
        data["default_expense_category"] = ""

    if object.default_payment is not None:
      try:
        payment = PaymentAccount.objects.get(id=object.default_payment.id)
        data["default_payment"] = PaymentAccountView.serialize(payment)
      except:
        data['default_payment'] = ""

    return data

  def get(self, request, *args, **kwargs):

    payee_id = kwargs.get('id')

    if payee_id is not None:
      try:
        payee = self.objects.get(id= payee_id)
        return JsonResponse(self.serialize(payee))
      except Payee.DoesNotExist:
        return JsonResponse({'error': f'{self.display_name} Does Not Exist'}, status=404)
      
    else:
      payees = self.objects.all().values()
      return JsonResponse(list(payees), safe=False, status=200)
    
  def post(self, request, *args, **kwargs):
    try:
      print(str(request))
      if request.path.endswith('/delete/'):
        return self.handle_delete(request, *args, **kwargs)

      if request.body is None: 
        return JsonResponse({'error': 'Invalid request body'}, status=404)
      
      data = json.loads(request.body)

      if data.get('id') is not None:
        # Updating
        try:
          payee = self.objects.get(id=data.get('id'))
          
          if data.get('name'): 
            payee.name = data.get('name') 
          if data.get('description'): 
            payee.description = data.get('description')
          if data.get('contact_number'):
            payee.contact_number = data.get('contact_number')
          
          if data.get('default_expense_category'):
            category = ExpenseCategory.objects.filter(id=data.get('default_expense_category')).first()

            if category:
              payee.default_expense_category = category

          if data.get('default_payment'):
            payment = PaymentAccount.objects.filter(id=data.get('default_payment'))
            if payment:
              payee.default_payment = payment

          payee.save()
          return JsonResponse({}, status=201)
        except Payee.DoesNotExist:
          return JsonResponse({'error': f'{self.display_name} ID doesn not exist'})

      else:
        # Creating
        if data.get('name') is None:
          return JsonResponse({'error': f'{self.display_name} Name is required for creating {self.display_name}'}, status=404)

        payee_creating_data = {
          "name": data.get('name'),
          "contact_number": data.get("contact_number", ''),
          "description": data.get('description', '')
        }
        
        category_base = ExpenseCategory.objects.filter(id=data.get('default_expense_category'))
        if category_base.exists():
          payee_creating_data["default_expense_category"] = category_base.first()

        payment_base = PaymentAccount.objects.filter(id=data.get('default_payment'))
        if payment_base.exists():
          payee_creating_data["default_payment"] = payment_base.first()

        new_payee = self.objects.create(**payee_creating_data)

        print('creating payee', new_payee)

        return JsonResponse(data=PayeeView.serialize(new_payee), status=201)
    except IntegrityError as e:
      if 'unique constraint' in str(e):
        return JsonResponse({'error': f'Duplication on {self.display_name}'}, status=400)
      return JsonResponse({'error': f'Database Integrity Error: {str(e)}'}, status=400)
    
  def handle_delete(self, request, *args, **kwargs):
    try:
      payee_id = kwargs.get('id')

      if payee_id is None:
        return JsonResponse({'error': 'ID is required for deletion'}, status=400)
      
      payee_base = Payee.objects.filter(id=payee_id)

      if payee_base.exists():
        payee = payee_base.first()

        payee.delete()
        return JsonResponse({'message': f'Delete {payee.name} successfully'}, status=200)
      
      return JsonResponse({'error': f'Fail to delete payee with id {payee_id}'}, status=400)

    except (ValueError, KeyError) as e:
      return JsonResponse({'error': str(e)}, status=400)

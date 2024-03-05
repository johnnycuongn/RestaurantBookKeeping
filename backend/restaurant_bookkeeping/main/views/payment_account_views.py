from django.views import View
from django.http import JsonResponse
from django.db import IntegrityError

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json

from ..models import PaymentAccount

@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF for simplicity
class PaymentAccountView(View):

  objects = PaymentAccount.objects
  display_name = 'Payment Account'

  @staticmethod
  def serialize(object: PaymentAccount):
    return {
        'id': object.id,
        'name': object.name,
        'description': object.description,
        'note': object.note if object.note is not None else "",
        'method': object.method if object.method is not None else ""
    }

  def get(self, request, *args, **kwargs):

    payment_id = kwargs.get('id')


    if payment_id is not None:
      try:
        payment = self.objects.get(id= payment_id)
        return JsonResponse(PaymentAccountView.serialize(payment))
      except PaymentAccount.DoesNotExist:
        return JsonResponse({'error': f'{self.display_name} Does Not Exist'}, status=404)
      
    else:
      payment_accounts = self.objects.all().values()
      return JsonResponse(list(payment_accounts), safe=False, status=200)
    
  def post(self, request, *args, **kwargs):
    valid_method_choices_display = dict(PaymentAccount.payment_methods_choices).values()

    if request.path.endswith('delete/'):
      return self.handle_delete(request, *args, **kwargs)

    try:
      if request.body is None: 
        return JsonResponse({'error': 'Invalid request body'}, status=404)
      
      data = json.loads(request.body)

      if data.get('id') is not None:
        # Updating
        try:
          payment_account = self.objects.get(id=data.get('id'))
          
          if data.get('name'): 
            payment_account.name = data.get('name') 
          if data.get('note'): 
            payment_account.note = data.get('note')
          if data.get('description'): 
            payment_account.description = data.get('description')

          if data.get('method'):
            if not self.is_valid_payment_method(data.get('method')):
              return JsonResponse({'error': f'Invalid Payment Method. Valid choices are {valid_method_choices_display}'})
            payment_account.method = data.get('method')

          payment_account.save()
          return JsonResponse({}, status=201)
        except PaymentAccount.DoesNotExist:
          return JsonResponse({'error': f'{self.display_name} ID doesn not exist'})

      else:
        # Creating
        if data.get('name') is None:
          return JsonResponse({'error': f'{self.display_name} Name is required for creating {self.display_name}'}, status=404)
        
        if data.get('method') is None or not self.is_valid_payment_method(data.get('method')):
          return JsonResponse({'error': f'Invalid Payment Method. Valid choices are {valid_method_choices_display}'})
      
        new_payment_account = self.objects.create(
          name = data.get('name'),
          note = data.get('note', ''),
          description = data.get('description', ''),
          method = data.get('method')
        )

        return JsonResponse(data=PaymentAccountView.serialize(new_payment_account), status=201)
    except IntegrityError as e:
      if 'unique constraint' in str(e):
        return JsonResponse({'error': f'Duplication on {self.display_name}'})
      return JsonResponse({'error': f'Database Integrity Error: {str(e)}'})
  
  def handle_delete(self, request, *args, **kwargs):
    try:
      payment_id = kwargs.get('id')

      if payment_id is None:
        return JsonResponse({'error': 'ID is required for deletion'})

      payment_base = self.objects.filter(id=payment_id)
      if payment_base.exists():
        payment = payment_base.first()

        payment.delete()

        return JsonResponse({'message': f'Payment Account ({payment.id}){payment.name} deleted successfully'}, status=200)

      return JsonResponse({'message': f'Failed to delete payment with {payment_id}'}, status=400)

    except (ValueError, KeyError) as e:
      return JsonResponse(data={'error': str(e)}, status = 400)

  def is_valid_payment_method(self, method: str) -> bool:
    method = method.upper()
    valid_method_choices = dict(PaymentAccount.payment_methods_choices).keys()

    return method in valid_method_choices


import json
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.db import IntegrityError
from django.core.exceptions import ValidationError

from ..models import ExpenseCategory, MainCategory

@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF for simplicity
class ExpenseCategoryAPIView(View):
    
    @staticmethod
    def serialize(object: ExpenseCategory):
        return {
            'id': object.id,
            'name': object.name,
            'description': object.description,
            'main_category': object.main_category
        }
    
    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('id')
        if category_id is not None:
            # Trying to get a single category
            try:
                category = ExpenseCategory.objects.get(id=category_id)
                
                return JsonResponse(ExpenseCategoryAPIView.serialize(category))
            except ExpenseCategory.DoesNotExist:
                return JsonResponse({'error': 'ExpenseCategory not found'}, status=404)
        else:
            # Listing all categories
            categories = ExpenseCategory.objects.all().values('id', 'name', 'description', 'main_category')
            return JsonResponse(list(categories), safe=False)


    def post(self, request, *args, **kwargs):
        try:
            print(f'request body {request.body}')
            print(f'Request path {request.path}')
            if request.path.endswith('/delete/'):
                print('delete route')
                print('kwargs ', kwargs)
                return self.handle_delete(request, *args, **kwargs)

            if (request.body is None):
                return JsonResponse(data={'error': 'Invalid Request'}, status=400)
            data = json.loads(request.body)

            if data.get('name') is None:
                return JsonResponse(data={'error': 'Name is required'}, status=400)
            
            data_main_category = data.get('main_category').upper()

            valid_expense_categories = dict(MainCategory.MAIN_CATEGORIES_CHOICES).keys()
            if data_main_category not in valid_expense_categories:
                return JsonResponse({'error': 'Invalid Expense Category. Options are (operating, inventory, labour, others)'})
            
            if 'id' not in data:
              category = ExpenseCategory.objects.create(
                  name=data['name'],
                  description=data.get('description', ''),
                  main_category=data_main_category
              )
              return JsonResponse({
                  'id': category.id,
                  'name': category.name,
                  'description': category.description,
                  'main_category': category.main_category
              }, status=201)
            
            if 'id' in data and data['id']:
              try:
                  category = ExpenseCategory.objects.get(id=data['id'])
              except ExpenseCategory.DoesNotExist:
                  return JsonResponse({'error': 'ExpenseCategory not found.'}, status=404)
              
              category.name = data['name']
              category.description = data.get('description', '')
              category.main_category = data_main_category
              category.save()

              return JsonResponse({
                  'id': category.id,
                  'name': category.name,
                  'description': category.description,
                  'main_category': category.main_category
              }, status=200)

        except IntegrityError as e:
            print('error integrity', e)
            return JsonResponse({'error': 'Database Integrity Error'}, status=400)
        except ValidationError as e:
            error_message = ', '.join(e.messages)
            return JsonResponse({'error': f'{error_message}'}, status=400)
        except (ValueError, KeyError) as e:
            print('error creating', e)
            return JsonResponse(data={'error': e}, status=400)
      
    def handle_delete(self, request, *args, **kwargs):
      try:
          category_id = kwargs.get('id')
          if category_id is None:
              return JsonResponse({'error': 'ID is required for deletion'}, status=400)

          try:
              category = ExpenseCategory.objects.get(id=category_id)
              category.delete()
              return JsonResponse({'message': 'ExpenseCategory deleted successfully'}, status=200)
          except ExpenseCategory.DoesNotExist:
              return JsonResponse({'error': 'ExpenseCategory not found.'}, status=404)

      except (ValueError, KeyError) as e:
          return JsonResponse({'error': str(e)}, status=400)
        
      
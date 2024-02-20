import json
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ..models import ExpenseCategory

@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF for simplicity
class ExpenseCategoryAPIView(View):
    
    def serialize(self, object: ExpenseCategory):
        return {
            'id': object.id,
            'name': object.name,
            'djandescription': object.description,
            'main_category': object.main_category
        }
    
    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('id')
        if category_id is not None:
            # Trying to get a single category
            try:
                category = ExpenseCategory.objects.get(id=category_id)
                
                return JsonResponse(self.serialize(category))
            except ExpenseCategory.DoesNotExist:
                return JsonResponse({'error': 'ExpenseCategory not found'}, status=404)
        else:
            # Listing all categories
            categories = ExpenseCategory.objects.all().values('id', 'name', 'description', 'main_category')
            return JsonResponse(list(categories), safe=False)


    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            if data.get('name') is None:
                return JsonResponse(data={'error': 'Name is required'}, status=400)

            category = ExpenseCategory.objects.create(
                name=data['name'],
                description=data.get('description', ''),  # Use .get to avoid KeyError
                main_category=data['main_category']
            )
            return JsonResponse({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'main_category': category.main_category
            }, status=201)  # Return HTTP 201 Created
        except (ValueError, KeyError) as e:
            return JsonResponse(data={'error': e}, status=400)  # Bad Request
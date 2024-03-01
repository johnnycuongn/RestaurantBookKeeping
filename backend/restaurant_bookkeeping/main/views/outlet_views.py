from django.views import View
from django.http import JsonResponse
from django.db import IntegrityError

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json

from ..models import Outlet

@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF for simplicity
class OutletView(View):

  def serialize(self, object: Outlet):
    return {
        'id': object.id,
        'name': object.name,
        'description': object.description,
        'address': object.address
    }

  def get(self, request, *args, **kwargs):

    outlet_id = kwargs.get('id')

    if outlet_id is not None:
      try:
        outlet = Outlet.objects.get(id= outlet_id)
        return JsonResponse(self.serialize(outlet))
      except Outlet.DoesNotExist:
        return JsonResponse({'error': 'Outlet Does Not Exist'}, status=404)
      
    else:
      outlets = Outlet.objects.all().values()
      return JsonResponse(list(outlets), safe=False, status=200)
    
  def post(self, request, *args, **kwargs):
    try:
      if request.body is None: 
        return JsonResponse({'error': 'Invalid request body'}, status=404)
      
      data = json.loads(request.body)

      if data.get('id') is not None:
        # Updating
        try:
          outlet = Outlet.objects.get(id=data.get('id'))
          if data.get('name'):
            outlet.name = data.get('name')
          if data.get('code'):
            code = data.get('code')
            if Outlet.objects.filter(code=code).exists():
              return JsonResponse({'error': f'Outlet with code {code} already existed'}, status=404)
            outlet.code = data.get('code')
          if data.get('address'):
            outlet.address = data.get('address')
          if data.get('description'):
            outlet.description = data.get('description')

          outlet.save()
          return JsonResponse({}, status=201)
        except Outlet.DoesNotExist:
          return JsonResponse({'error': 'Outlet ID doesn not exist'})

      else:
        # Creating
        if data.get('name') is None:
          return JsonResponse({'error': 'Outlet Name is required for creating Outlet'}, status=404)
        
        if data.get('code') is None:
          return JsonResponse({'error': 'Outlet Code is required for creating Outlet'})
      
        new_outlet = Outlet.objects.create(
          name = data.get('name'),
          code = data.get('code'),
          address = data.get('address', ''),
          description = data.get('description', '')
        )

        return JsonResponse(data=self.serialize(new_outlet), status=201)
    except IntegrityError as e:
      if 'unique constraint' in str(e):
        return JsonResponse({'error': 'Duplication on Outlet'})
      return JsonResponse({'error': f'Database Integrity Error: {str(e)}'})
    

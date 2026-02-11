from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

schemas_store = []
data_store = []

@csrf_exempt
def manage_schemas(request):
    if request.method == 'GET':
        return JsonResponse(schemas_store, safe=False)
    if request.method == 'POST':
        payload = json.loads(request.body)
        schemas_store.append(payload)
        return JsonResponse(payload, status=201)

@csrf_exempt
def manage_data(request):
    negocio_target = request.GET.get('negocio')

    if request.method == 'GET':
        filtered_data = [d for d in data_store if d.get('_negocio') == negocio_target]
        return JsonResponse(filtered_data, safe=False)
    
    if request.method == 'POST':
        payload = json.loads(request.body)
        
        # LÓGICA DE ID AUTOMÁTICO INDEPENDIENTE
        if not payload.get('id'):
            # Buscamos el ID más alto SOLO de este negocio
            datos_del_negocio = [d for d in data_store if d.get('_negocio') == negocio_target]
            if datos_del_negocio:
                max_id = max([int(d.get('id', 0)) for d in datos_del_negocio])
                payload['id'] = max_id + 1
            else:
                payload['id'] = 1
        else:
            payload['id'] = int(payload['id'])
            
        payload['_negocio'] = negocio_target
        data_store.append(payload)
        return JsonResponse(payload, status=201)

@csrf_exempt
def manage_detail(request, record_id):
    negocio_target = request.GET.get('negocio')
    item = next((d for d in data_store if str(d.get('id')) == str(record_id) and d.get('_negocio') == negocio_target), None)

    if not item: return JsonResponse({'error': 'No encontrado'}, status=404)

    if request.method == 'DELETE':
        data_store.remove(item)
        return JsonResponse({'status': 'deleted'}, status=204)

    if request.method == 'PUT':
        new_data = json.loads(request.body)
        item.update(new_data)
        return JsonResponse(item)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
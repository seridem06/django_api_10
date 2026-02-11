from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import EsquemaNegocio, DatoNegocio
import json
from collections import OrderedDict

@csrf_exempt
def manage_schemas(request):
    if request.method == 'GET':
        # Consultar todos los esquemas de la BD
        esquemas = list(EsquemaNegocio.objects.all().values())
        return JsonResponse(esquemas, safe=False)
    
    if request.method == 'POST':
        payload = json.loads(request.body)
        # Crear registro persistente en SQLite
        EsquemaNegocio.objects.create(
            nombre=payload['nombre'],
            config=payload['config'],
            campos=payload['campos']
        )
        return JsonResponse(payload, status=201)

    if request.method == 'DELETE':
        nombre_negocio = request.GET.get('nombre')
        # Eliminar esquema y sus datos de la BD en cascada
        EsquemaNegocio.objects.filter(nombre=nombre_negocio).delete()
        DatoNegocio.objects.filter(negocio=nombre_negocio).delete()
        return JsonResponse({'status': 'deleted'}, status=204)

@csrf_exempt
def manage_data(request):
    negocio_target = request.GET.get('negocio')

    if request.method == 'GET':
        # Filtrar datos por negocio en la BD
        registros = DatoNegocio.objects.filter(negocio=negocio_target)
        
        # FORZAR QUE EL ID APAREZCA PRIMERO EN EL JSON
        datos_ordenados = []
        for r in registros:
            contenido = r.contenido
            # Usamos OrderedDict para garantizar la jerarquía visual del ID
            item_ordenado = OrderedDict([('id', contenido.get('id'))])
            for key, value in contenido.items():
                if key != 'id':
                    item_ordenado[key] = value
            datos_ordenados.append(item_ordenado)
            
        return JsonResponse(datos_ordenados, safe=False)
    
    if request.method == 'POST':
        payload = json.loads(request.body)
        
        # Conversión inteligente para decimales y enteros
        for key, value in payload.items():
            if isinstance(value, str) and value.strip():
                if value.replace('.', '', 1).isdigit():
                    payload[key] = float(value) if '.' in value else int(value)
        
        # Lógica de ID Automático consultando la BD SQLite
        if not payload.get('id') or payload.get('id') == "AUTO":
            max_id = 0
            datos_previos = DatoNegocio.objects.filter(negocio=negocio_target)
            if datos_previos.exists():
                # Obtenemos el ID más alto registrado para este negocio
                max_id = max([int(r.contenido.get('id', 0)) for r in datos_previos])
            payload['id'] = max_id + 1
        else:
            try:
                payload['id'] = int(payload['id'])
            except ValueError: pass
            
        # Guardar el dato en la BD persistente
        DatoNegocio.objects.create(negocio=negocio_target, contenido=payload)
        return JsonResponse(payload, status=201)

@csrf_exempt
def manage_detail(request, record_id):
    negocio_target = request.GET.get('negocio')
    
    # Buscar el registro específico en la BD
    registros = DatoNegocio.objects.filter(negocio=negocio_target)
    target_obj = None
    for r in registros:
        if str(r.contenido.get('id')) == str(record_id):
            target_obj = r
            break

    if not target_obj: 
        return JsonResponse({'error': 'No encontrado'}, status=404)

    if request.method == 'DELETE':
        target_obj.delete()
        return JsonResponse({'status': 'deleted'}, status=204)

    if request.method == 'PUT':
        new_data = json.loads(request.body)
        for key, value in new_data.items():
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                new_data[key] = float(value) if '.' in value else int(value)
                
        # Actualizar JSON y guardar en BD
        target_obj.contenido.update(new_data)
        target_obj.save()
        return JsonResponse(target_obj.contenido)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
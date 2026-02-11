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
        try:
            payload = json.loads(request.body)
            # Crear registro persistente en SQLite
            EsquemaNegocio.objects.create(
                nombre=payload['nombre'],
                config=payload.get('config', {}),
                campos=payload['campos']
            )
            return JsonResponse(payload, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'DELETE':
        nombre_negocio = request.GET.get('nombre')
        if not nombre_negocio:
            return JsonResponse({'error': 'Nombre de negocio requerido'}, status=400)
        
        # Eliminar esquema y sus datos de la BD en cascada
        EsquemaNegocio.objects.filter(nombre=nombre_negocio).delete()
        DatoNegocio.objects.filter(negocio=nombre_negocio).delete()
        return JsonResponse({'status': 'deleted'}, status=200)

@csrf_exempt
def manage_data(request):
    negocio_target = request.GET.get('negocio')
    
    if not negocio_target:
        return JsonResponse({'error': 'Parámetro negocio requerido'}, status=400)

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
        try:
            payload = json.loads(request.body)
            
            # Obtener el esquema para validar tipos de datos
            try:
                esquema = EsquemaNegocio.objects.get(nombre=negocio_target)
                campos_config = {c['key']: c for c in esquema.campos}
            except EsquemaNegocio.DoesNotExist:
                return JsonResponse({'error': 'Esquema no encontrado'}, status=404)
            
            # Conversión inteligente basada en el esquema
            for key, value in list(payload.items()):
                if key in campos_config:
                    campo_tipo = campos_config[key].get('type')
                    
                    # Convertir números
                    if campo_tipo == 'number' and isinstance(value, str) and value.strip():
                        try:
                            # Si es entero
                            if campos_config[key].get('isInteger', False):
                                payload[key] = int(float(value))  # Convierte "12.0" a 12
                            else:
                                # Es decimal
                                payload[key] = round(float(value), 2)
                        except ValueError:
                            pass  # Mantener el valor original si no se puede convertir
            
            # Lógica de ID Automático consultando la BD SQLite
            id_automatico = esquema.config.get('idAutomatico', True)
            
            if id_automatico or not payload.get('id') or payload.get('id') == "AUTO":
                max_id = 0
                datos_previos = DatoNegocio.objects.filter(negocio=negocio_target)
                if datos_previos.exists():
                    # Obtenemos el ID más alto registrado para este negocio
                    try:
                        max_id = max([int(r.contenido.get('id', 0)) for r in datos_previos])
                    except (ValueError, TypeError):
                        max_id = 0
                payload['id'] = max_id + 1
            else:
                # ID manual
                try:
                    payload['id'] = int(payload['id'])
                except (ValueError, TypeError):
                    payload['id'] = 1
            
            # Guardar el dato en la BD persistente
            DatoNegocio.objects.create(negocio=negocio_target, contenido=payload)
            return JsonResponse(payload, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def manage_detail(request, record_id):
    negocio_target = request.GET.get('negocio')
    
    if not negocio_target:
        return JsonResponse({'error': 'Parámetro negocio requerido'}, status=400)
    
    # Buscar el registro específico en la BD
    registros = DatoNegocio.objects.filter(negocio=negocio_target)
    target_obj = None
    for r in registros:
        if str(r.contenido.get('id')) == str(record_id):
            target_obj = r
            break

    if not target_obj: 
        return JsonResponse({'error': 'Registro no encontrado'}, status=404)

    if request.method == 'DELETE':
        target_obj.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    if request.method == 'PUT':
        try:
            new_data = json.loads(request.body)
            
            # Obtener configuración del esquema
            try:
                esquema = EsquemaNegocio.objects.get(nombre=negocio_target)
                campos_config = {c['key']: c for c in esquema.campos}
            except EsquemaNegocio.DoesNotExist:
                campos_config = {}
            
            # Convertir tipos según el esquema
            for key, value in list(new_data.items()):
                if key in campos_config:
                    campo_tipo = campos_config[key].get('type')
                    
                    if campo_tipo == 'number' and isinstance(value, str) and value.strip():
                        try:
                            if campos_config[key].get('isInteger', False):
                                new_data[key] = int(float(value))
                            else:
                                new_data[key] = round(float(value), 2)
                        except ValueError:
                            pass
            
            # Actualizar JSON y guardar en BD
            target_obj.contenido.update(new_data)
            target_obj.save()
            return JsonResponse(target_obj.contenido)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
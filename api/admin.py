from django.contrib import admin
from .models import EsquemaNegocio, DatoNegocio

@admin.register(EsquemaNegocio)
class EsquemaNegocioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'config', 'cantidad_campos']
    search_fields = ['nombre']
    
    def cantidad_campos(self, obj):
        return len(obj.campos)
    cantidad_campos.short_description = 'N° Campos'


@admin.register(DatoNegocio)
class DatoNegocioAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'get_id', 'contenido_preview', 'created_at']
    list_filter = ['negocio', 'created_at']
    search_fields = ['negocio', 'contenido']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_id(self, obj):
        return obj.contenido.get('id', 'N/A')
    get_id.short_description = 'ID Registro'
    
    def contenido_preview(self, obj):
        import json
        return json.dumps(obj.contenido, indent=2)[:100] + '...'
    contenido_preview.short_description = 'Vista Previa'
"""
URL configuration for backend_lab10 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import manage_schemas, manage_data, manage_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schemas/', manage_schemas),             # Para crear/leer formatos
    path('api/data/', manage_data),                   # Para crear/leer registros
    path('api/data/<str:record_id>/', manage_detail), # Para editar/borrar
]
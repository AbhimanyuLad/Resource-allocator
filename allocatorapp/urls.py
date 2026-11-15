from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/create/', views.resource_create, name='resource_create'),
    path('resources/<int:pk>/', views.resource_detail, name='resource_detail'),
    path('resources/<int:pk>/edit/', views.resource_update, name='resource_update'),
    path('excel-upload/', views.excel_upload, name='excel_upload'),

    path('orders/', views.order_list, name='order_list'),
]
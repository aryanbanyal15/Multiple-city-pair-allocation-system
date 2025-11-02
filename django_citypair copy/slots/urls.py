from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('slots/', views.slot_index, name='slots_index'),
	path('slots/create', views.slot_create, name='slots_create'),
	path('slots/<int:slot_id>/update', views.slot_update, name='slots_update'),
	path('slots/<int:slot_id>/delete', views.slot_delete, name='slots_delete'),
]


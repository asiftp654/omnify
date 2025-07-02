from django.urls import path
from . import views


urlpatterns = [
    path('events', views.EventViewSet.as_view({'get': 'list', 'post': 'create'}), name='event-list'),    
    path('events/<int:event_id>/register', views.AttendeeViewSet.as_view({'post': 'create'}), name='attendee-create'),
    path('events/<int:event_id>/attendees', views.AttendeeViewSet.as_view({'get': 'list'}), name='attendee-list'),
]
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from django.core.exceptions import ValidationError
from omnify.response import APIResponse
from omnify.pagination import CustomPagination
from .models import Event, Attendee
from .serializers import EventSerializer, AttendeeSerializer
from .error import ErrorMessages
from .services import AttendeeService


class EventViewSet(viewsets.ModelViewSet):
    
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
    def list(self, request):
        events = self.get_queryset()
        serializer = self.get_serializer(events, many=True)
        if serializer.data:
            return APIResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)
        return APIResponse.error(errors=ErrorMessages.EVENTS_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(data=serializer.data, status_code=status.HTTP_201_CREATED)
        return APIResponse.error(errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    

class AttendeeViewSet(viewsets.ViewSet):

    def create(self, request, event_id):
        serializer = AttendeeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                attendee = AttendeeService.register_attendee(event_id, serializer.validated_data)
                return APIResponse.success(data=AttendeeSerializer(attendee).data, status_code=status.HTTP_201_CREATED)
            except ValidationError as e:
                return APIResponse.error(errors=e.message, status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.error(errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, event_id):
        event = Event.objects.filter(id=event_id).first()
        if not event:
            return APIResponse.error(errors=ErrorMessages.EVENT_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)
        
        attendees = Attendee.objects.filter(event=event).order_by('id')
        paginator = CustomPagination()
        try:
            paginated_attendees = paginator.paginate_queryset(attendees, request)
        except NotFound:
            return APIResponse.error(errors=ErrorMessages.INVALID_PAGE_NUMBER, status_code=status.HTTP_404_NOT_FOUND)
        serializer = AttendeeSerializer(paginated_attendees, many=True)
        data = paginator.get_paginated_response(serializer.data)
        return APIResponse.success(data=data, status_code=status.HTTP_200_OK)
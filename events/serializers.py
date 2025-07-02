from rest_framework import serializers
from .models import Event, Attendee
from .error import ErrorMessages


class EventSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', input_formats=['%d/%m/%Y %H:%M:%S'])
    end_time = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', input_formats=['%d/%m/%Y %H:%M:%S'])
    
    class Meta:
        model = Event
        fields = ['id', 'name', 'location', 'max_capacity', 'start_time', 'end_time']
    
    def validate(self, data):
        # Check if end_time is after start_time
        if 'end_time' in data and 'start_time' in data:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError({'end_time': ErrorMessages.END_TIME_BEFORE_START})        
        return data


class AttendeeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Attendee
        fields = ['id', 'name', 'email']
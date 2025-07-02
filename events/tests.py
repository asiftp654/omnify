from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch
from events.models import Event, Attendee
from events.error import ErrorMessages
from events.services import AttendeeService


class EventViewSetTestCase(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.event_data = {
            'name': 'Test Event',
            'location': 'Test Location',
            'max_capacity': 2,
            'start_time': '25/12/2024 10:00:00',
            'end_time': '25/12/2024 18:00:00'
        }
        
        self.event = Event.objects.create(
            name='Existing Event',
            location='Existing Location',
            max_capacity=50,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=8)
        )

    def test_list_events_success(self):
        url = reverse('event-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Existing Event')

    def test_create_event_success(self):
        url = reverse('event-list')
        response = self.client.post(url, self.event_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], 'Test Event')
        self.assertEqual(Event.objects.count(), 2)

    def test_create_event_end_time_before_start_time(self):
        invalid_data = {
            'name': 'Test Event',
            'location': 'Test Location',
            'max_capacity': 100,
            'start_time': '25/12/2024 18:00:00',
            'end_time': '25/12/2024 10:00:00'  # End time before start time
        }
        
        url = reverse('event-list')
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('end_time', response.data['errors'])


class AttendeeViewSetTestCase(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        self.event = Event.objects.create(
            name='Test Event',
            location='Test Location',
            max_capacity=2,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=8)
        )
        
        self.attendee_data = {
            'name': 'user 1',
            'email': 'user1@example.com'
        }

    def test_create_attendee_success(self):
        url = reverse('attendee-create', kwargs={'event_id': self.event.id})
        
        with patch.object(AttendeeService, 'register_attendee') as mock_register:
            mock_attendee = Attendee(
                id=1,
                event=self.event,
                name='user 1',
                email='user1@example.com'
            )
            mock_register.return_value = mock_attendee
            
            response = self.client.post(url, self.attendee_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], 'user 1')
        self.assertEqual(response.data['data']['email'], 'user1@example.com')
        mock_register.assert_called_once_with(self.event.id, self.attendee_data)

    def test_create_attendee_validation_error(self):
        url = reverse('attendee-create', kwargs={'event_id': self.event.id})
        
        with patch.object(AttendeeService, 'register_attendee') as mock_register:
            mock_register.side_effect = ValidationError(ErrorMessages.CAPACITY_REACHED)
            
            response = self.client.post(url, self.attendee_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['errors'], ErrorMessages.CAPACITY_REACHED)

    def test_create_attendee_nonexistent_event(self):
        url = reverse('attendee-create', kwargs={'event_id': 99999})
        response = self.client.post(url, self.attendee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_attendees_empty(self):
        url = reverse('attendee-list', kwargs={'event_id': self.event.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['total_items'], 0)
        self.assertEqual(len(response.data['data']['results']), 0)

    def test_list_attendees_invalid_page(self):
        url = reverse('attendee-list', kwargs={'event_id': self.event.id})
        response = self.client.get(f'{url}?page=999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['errors'], ErrorMessages.INVALID_PAGE_NUMBER)

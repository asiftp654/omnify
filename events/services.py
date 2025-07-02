from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from events.models import Event, Attendee
from events.error import ErrorMessages


class AttendeeService:
    @staticmethod
    def register_attendee(event_id, data):
        # This will avoid both race condition and data integrity issues
        try:
            with transaction.atomic():
                # Using select_for_update to prevent race conditions
                event = Event.objects.select_for_update().get(pk=event_id)

                if event.attendees.count() >= event.max_capacity:
                    raise ValidationError(ErrorMessages.CAPACITY_REACHED)
                
                attendee = Attendee.objects.create(event=event, **data)
                return attendee

        except IntegrityError:
            raise ValidationError(ErrorMessages.EMAIL_ALREADY_REGISTERED)
        except ObjectDoesNotExist:
            raise ValidationError(ErrorMessages.EVENT_NOT_FOUND)

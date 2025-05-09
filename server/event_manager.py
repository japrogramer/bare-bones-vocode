from vocode.streaming.models.events import Event, EventType
from vocode.streaming.utils.events_manager import EventsManager

from loguru import logger

class SimpleEventManager(EventManager):
    def __init__(self):
        super().__init__(
            subscribed_events={
                EventType.PHONE_CALL_CONNECTED,
                EventType.PHONE_CALL_ENDED,
                EventType.PHONE_CALL_STARTED,
                EventType.TRANSCRIPTION_COMPLETE,
                EventType.SYNTHESIS_COMPLETE,
                EventType.AGENT_GENERATED_AUDIO,
                EventType.HUMAN_AUDIO_START,
                EventType.HUMAN_AUDIO_STOP,
                EventType.ACTION_STARTED,
                EventType.ACTION_FINISHED,
                EventType.ACTION_FAILED,
            }
        )

    def handle_event(self, event: Event):
        # This is a simple event manager.
        # Add your event logic here
        logger.info(f"Event received: {event.type} - {event.payload}")

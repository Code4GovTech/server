from events.ticketEventHandler import TicketEventHandler
import logging


async def dispatch_event(event_type, data, postgres_client):
    """This function dispatches all webhook event to respective Handler class
    Args:
        event_type (_type_): Type of webhook event
        data (_type_): JSON payload
        postgres_client (_type_): postgres instace
    
    """
    try:
        module_name = f'handlers.{event_type}_handler'
        class_name = f'{event_type.capitalize()}Handler'
        module = __import__(module_name, fromlist=[class_name])
        handler_class = getattr(module, class_name)
        handler_instance = handler_class()
        await handler_instance.handle_event(data, postgres_client)

    except ImportError:
        print(f"No handler found for event type: {event_type}")
        return "Import Error"

    except :
        return "Server Error"




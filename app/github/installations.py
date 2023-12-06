from quart import Blueprint

from events.ticketEventHandler import TicketEventHandler

installations = Blueprint('installations', __name__, url_prefix='/installations')

@installations.route("/refresh/<organisation>")
async def refreshInstallationData(organisation: str):
    await TicketEventHandler().updateInstallation(installation={
        "account": {
            "login": organisation
        }
    })


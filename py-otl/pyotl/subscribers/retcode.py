from dataclasses import dataclass, field
from typing import Dict, cast
import betterproto
from pyotl.otl_telemetry.data import CommandEvent, CommandFinished, Event


@dataclass
class RetcodeTracker:
    """
    Simple subscriber that maps commands to return codes
    """

    retcode: Dict[str, int] = field(default_factory=dict)

    def process_message(self, message: Event):
        (variant, event_payload) = betterproto.which_one_of(message, "et")
        if variant == "command":
            event_payload = cast(CommandEvent, event_payload)
            (command_name, command_payload) = betterproto.which_one_of(
                event_payload, "CommandVariant"
            )

            if command_name == "finished":
                command_payload = cast(CommandFinished, command_payload)
                self.retcode[event_payload.command_ref] = (
                    command_payload.out.status_code
                )
            else:
                pass
        else:
            pass

    def reset(self):
        self.retcode = {}
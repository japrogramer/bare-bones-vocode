from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
import os
from dotenv import load_dotenv
from fastapi import FastAPI

from vocode.streaming.telephony.server.base import TelephonyServer
# from vocode.streaming.models.model import BaseModel
from vocode.streaming.models.actions import ActionConfig
from vocode.streaming.models.telephony import TwilioInboundCallConfig
from vocode.streaming.models.telephony import TwilioConfig, VonageConfig
from vocode.streaming.models.transcriber import TranscriberConfig
from vocode.streaming.models.synthesizer import SynthesizerConfig
from vocode.streaming.agent.default_factory import DefaultAgentFactory
from vocode.streaming.synthesizer.default_factory import DefaultSynthesizerFactory
from vocode.streaming.transcriber.default_factory import DefaultTranscriberFactory
from vocode.streaming.action.default_factory import DefaultActionFactory
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.actions import ActionType
from vocode.streaming.models.events import EventType
from vocode.streaming.utils.events_manager import EventsManager
from vocode.streaming.telephony.config_manager.base_config_manager import BaseConfigManager as BaseManager
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager

from typing import Optional
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
import sentry_sdk

from configs import _get_call_configs
from event_manager import SimpleEventManager
from actions.actions import MyAgentFactory
from actions.actions import LogConversationState, LogConversationStateConfig, _LOG_ACTION_DESCRIPTION
from pydantic.v1 import BaseModel
from utils.tools import extract_tag_values

from loguru import logger

load_dotenv()


class CustomOutboundCall(BaseModel):
    recipient: str
    caller: str
    transcriber_config: Optional[TranscriberConfig] = None
    synthesizer_config: Optional[SynthesizerConfig] = None
    conversation_id: Optional[str] = None
    vonage_config: Optional[VonageConfig] = None
    twilio_config: Optional[TwilioConfig] = None

class MyTelephonyServer(TelephonyServer):
    def __init__(
        self,
        base_url: str,
        port: int,
        agent_factory: DefaultAgentFactory,
        synthesizer_factory: DefaultSynthesizerFactory,
        transcriber_factory: DefaultTranscriberFactory,
        events_manager: EventsManager,
        config_manager: BaseManager,
        inbound_call_configs: list[TwilioInboundCallConfig],
        action_config: Optional[List[ActionConfig]] = None,
    ):
        self.port = port
        self.action_config = action_config
        self.telephony_config = telephony_config
        super().__init__(
            base_url=base_url,
            agent_factory=agent_factory,
            synthesizer_factory=synthesizer_factory,
            transcriber_factory=transcriber_factory,
            events_manager=events_manager,
            config_manager=config_manager,
            inbound_call_configs=inbound_call_configs,
        )
        self.router.add_api_route("/outbound", self.create_outbound_call, methods=["POST"])

    async def create_outbound_call(self, request: Request):
        """
        Creates and starts an outbound call.

        Args:
            create_outbound_call: The configuration for the outbound call.

        Returns:
            A dictionary containing the conversation ID of the created call.
        """
        # Get the necessary configurations using the helper method
        data = await request.json()

        try:
            create_outbound_call: CustomOutboundCall = CustomOutboundCall(**data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request: {e}")

        agent_config, synthesizer_config, transcriber_config = _get_call_configs(
            self.action_config,
            create_outbound_call
        )

        # Update the create_outbound_call object with the retrieved configs
        create_outbound_call.agent_config = agent_config
        create_outbound_call.synthesizer_config = synthesizer_config
        create_outbound_call.transcriber_config = transcriber_config

        # Create an OutboundCall instance using the updated create_outbound_call object
        outbound_call = OutboundCall(
            config_manager=self.config_manager,
            to_phone=create_outbound_call.recipient,
            from_phone=create_outbound_call.caller,
            agent_config=create_outbound_call.agent_config,
            synthesizer_config=create_outbound_call.synthesizer_config,
            transcriber_config=create_outbound_call.transcriber_config,
            conversation_id=create_outbound_call.conversation_id,
            telephony_config=self.telephony_config,
            # metadata=create_outbound_call.metadata,
            # Add other necessary configurations here from create_outbound_call if available
            # For example:
            # record_audio=create_outbound_call.record_audio,
            # speed=create_outbound_call.speed,
            # pitch=create_outbound_call.pitch,
            # volume=create_outbound_call.volume,
            # endpointing_config=create_outbound_call.endpointing_config,
            # Redact PII if needed
            # redact_pii=create_outbound_call.redact_pii,
            # pii_categories=create_outbound_call.pii_categories,
            # log_level=create_outbound_call.log_level,
            # max_duration_seconds=create_outbound_call.max_duration_seconds,
            # dtmf_input_sequence=create_outbound_call.dtmf_input_sequence,
            # actions=create_outbound_call.actions, # Example action
        )

        # Start the outbound call
        await outbound_call.start()

        # Return the conversation ID
        return {"conversation_id": outbound_call.conversation_id}

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

if __name__ == "__main__":
    if os.getenv("USE_SENTRY", False):
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            environment=os.getenv("ENVIRONMENT"),
            # Sample rate for transactions (performance).
            traces_sample_rate=1.0,
            # Sample rate for exceptions / crashes.
            sample_rate=1.0,
            max_request_body_size="always",
            integrations=[
                AsyncioIntegration(),
                LoguruIntegration(),
            ],
        )


    actions = [LogConversationState()]
    action_config = [
        LogConversationStateConfig(type="log_conversation_state", description=_LOG_ACTION_DESCRIPTION),
    ]

    action_factory = DefaultActionFactory(actions)
    agent_factory = MyAgentFactory(action_factory=action_factory)
    synthesizer_factory = DefaultSynthesizerFactory()
    transcriber_factory = DefaultTranscriberFactory()
    events_manager = SimpleEventManager()
    config_manager = RedisManager()
    inbound_prompt = extract_tag_values("./prompts/inbound.xml")
    telephony_config = TwilioConfig(
                    account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                    auth_token=os.environ["TWILIO_AUTH_TOKEN"],
                ),
    inbound_call_configs= [
            TwilioInboundCallConfig(
                url="/inbound_call",
                agent_config=ChatGPTAgentConfig(
                    initial_message=BaseMessage(text=inbound_prompt.initial_message),
                    prompt_preamble=inbound_prompt.prompt_preamble,
                    generate_responses=True,
                ),
                twilio_config=telephony_config,
            )
        ]

    server = MyTelephonyServer(
        action_config=action_config,
        telephony_config=telephony_config,
        base_url=os.getenv("BASE_URL"),
        port=int(os.getenv("PORT", 3000)),
        agent_factory=agent_factory,
        synthesizer_factory=synthesizer_factory,
        transcriber_factory=transcriber_factory,
        events_manager=events_manager,
        config_manager=config_manager,
        inbound_call_configs=inbound_call_configs
    )
    server.run()

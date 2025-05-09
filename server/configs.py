from vocode.streaming.models.telephony import CreateInboundCall, CreateOutboundCall
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
from vocode.streaming.models.message import BaseMessage
from utils.tools import extract_tag_values

def _get_call_configs(
        action_config, create_outbound_call: CreateOutboundCall
    ) -> tuple[ChatGPTAgentConfig, ElevenLabsSynthesizerConfig, DeepgramTranscriberConfig]:
    """
    Retrieves the agent, synthesizer, and transcriber configurations
    based on the CreateOutboundCall object or other server configuration.

    Args:
        create_outbound_call: The configuration for the outbound call.

    Returns:
        A tuple containing the agent, synthesizer, and transcriber configurations.
    """
    # In a real application, you would dynamically determine these configs
    # based on the create_outbound_call object (e.g., user ID, call type)
    # or other server-side logic/database lookups.
    # For this example, we use hardcoded configs.
    outbound_prompt = extract_tag_values("./prompts/outbound.xml")
    agent_config = ChatGPTAgentConfig(
        initial_message=BaseMessage(text=outbound_prompt.initial_message),
        prompt_preamble=outbound_prompt.prompt_preamble,
        generate_responses=True,
        action_config=action_config, # Or your action config
        # TODO: add action factory
    )
    synthesizer_config = ElevenLabsSynthesizerConfig.from_env()
    transcriber_config = DeepgramTranscriberConfig.from_env()

    return agent_config, synthesizer_config, transcriber_config


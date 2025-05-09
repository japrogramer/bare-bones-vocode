import os
from typing import Optional, Type

from pydantic import Field
from pydantic.v1 import BaseModel

from vocode.streaming.agent.abstract_factory import AbstractAgentFactory
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import ActionConfig
from vocode.streaming.models.actions import ActionInput, ActionOutput


from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.action.base_action import AbstractActionFactory
from loguru import logger


_LOG_ACTION_DESCRIPTION = """
Runs any time a new request is made to the agent.
"""

class LogConversationParameters(BaseModel):
    bot: Optional[str] = Field(..., description="The most recent response from the bot")
    human: Optional[str] = Field(None, description="The most recent response from the human")


class LogConversationResponse(BaseModel):
    success: bool


class LogConversationStateConfig(ActionConfig, type="log_conversation_state"):
    # Add fields here if you want to make it configurable in the future
    pass


class LogConversationState(BaseAction[
    LogConversationStateConfig,
    LogConversationParameters,
    LogConversationResponse
    ]):
    description: str = _LOG_ACTION_DESCRIPTION
    action_type: str = "log_conversation_state"

    async def run(
        self, action_input: ActionInput[LogConversationParameters]
    ) -> ActionOutput[LogConversationResponse]:
        logger.info(f"Conversation State: {action_input.parameters}")
        return ActionOutput(
            action_type=action_input.action_config.type,
            response=LogConversationResponse(success=True),
        )


class MyAgentFactory(AbstractAgentFactory):
    def __init__(self, action_factory: AbstractActionFactory):
        self.action_factory = action_factory

    def create_agent(self, agent_config: AgentConfig, logger: Optional[logging.Logger] = None):
        if agent_config.type == "CHAT_GPT":
            return ChatGPTAgent(
                agent_config=agent_config,
                action_factory=self.action_factory,
                logger=logger,
            )
        else:
            raise Exception("Invalid agent config")

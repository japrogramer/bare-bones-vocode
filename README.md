# Vocode Telephony Server

This project is a cookie cutter bare-bones implementation of a telephony server using the Vocode library, built with FastAPI.
It handles both inbound and outbound calls, integrating with services like Twilio and Eleven Labs, and utilizes Redis for configuration management.

## Features

*   Handles inbound calls via a configurable endpoint.
*   Supports creating outbound calls via a `/outbound` API endpoint.
*   Integrates with Twilio for telephony services.
*   Uses Eleven Labs for speech synthesis (configurable).
*   Utilizes Deepgram for speech transcription (configurable).
*   Includes custom actions, such as logging conversation state.
*   Integrates with Sentry for error tracking.
*   Uses Redis for managing call configurations.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd vocode_server
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file is assumed. If it doesn't exist, you may need to create one based on the imports in `server.py` and other project files.)*

3.  **Environment Variables:**
    Create a `.env` file in the `server/` directory based on the `.env.example` file. You will need to configure the following:

    *   `BASE_URL`: The base URL where the server is accessible (e.g., your ngrok URL or public IP).
    *   `PORT`: The port the server will run on (default is 3000).
    *   `TWILIO_ACCOUNT_SID`: Your Twilio Account SID.
    *   `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token.
    *   `ELEVEN_LABS_API_KEY`: Your Eleven Labs API Key (if using Eleven Labs synthesizer).
    *   `DEEPGRAM_API_KEY`: Your Deepgram API Key (if using Deepgram transcriber).
    *   `REDIS_URL`: The URL for your Redis instance (e.g., `redis://localhost:6379`).
    *   `USE_SENTRY`: Set to `True` to enable Sentry integration.
    *   `SENTRY_DSN`: Your Sentry DSN (if `USE_SENTRY` is `True`).
    *   `ENVIRONMENT`: The environment name for Sentry (e.g., `development`, `production`).

## Running the Server

Navigate to the `server/` directory and run the `server.py` file:

```bash
cd server
python server.py
```

The server will start and listen on the specified port (default 3000).

## API Endpoints

### `POST /outbound`

Creates and starts an outbound call.

**Request Body:**

```json
{
  "recipient": "string", // The phone number to call (e.g., "+15551234567")
  "caller": "string",    // Your Twilio/Vonage phone number (e.g., "+15559876543")
  "transcriber_config": {}, // Optional: Custom transcriber configuration
  "synthesizer_config": {}, // Optional: Custom synthesizer configuration
  "conversation_id": "string", // Optional: A unique ID for the conversation
  "vonage_config": {}, // Optional: Vonage configuration
  "twilio_config": {}  // Optional: Twilio configuration
}
```

*Note: The `transcriber_config` and `synthesizer_config` can be omitted to use the default configurations defined in `configs.py`.*

**Response:**

```json
{
  "conversation_id": "string" // The ID of the created conversation
}
```

### Inbound Calls

The server is configured to handle inbound calls at the `/inbound_call` endpoint, as defined in `server.py`. You will need to configure your Twilio or Vonage number to point to `<BASE_URL>/inbound_call`.

## Project Structure

*   `server.py`: The main FastAPI application and TelephonyServer implementation.
*   `configs.py`: Contains helper functions for retrieving call configurations.
*   `event_manager.py`: Simple event manager implementation.
*   `actions/actions.py`: Contains custom action definitions (e.g., `LogConversationState`) and a custom agent factory (`MyAgentFactory`).
*   `prompts/inbound.xml`: XML file containing prompts for inbound calls.
*   `prompts/outbound.xml`: XML file containing prompts for outbound calls.
*   `utils/tools.py`: Contains utility functions (e.g., `extract_tag_values`).
*   `.env.example`: Example file for environment variables.

## Dependencies

Key dependencies used in this project include:

*   `vocode`: The core library for voice AI.
*   `FastAPI`: Web framework for building the API.
*   `python-dotenv`: For loading environment variables.
*   `redis`: For Redis configuration management.
*   `sentry-sdk`: For error tracking.
*   `loguru`: For logging.
*   `uvicorn`: ASGI server to run the FastAPI app.
*   `pydantic`: For data validation.

*(This list is based on imports and usage in `server.py`. Refer to `requirements.txt` for the complete list.)*

## Extending

*   **Custom Agents:** Implement your own agent logic by creating a class that inherits from a Vocode `AgentConfig` and updating the `MyAgentFactory`.
*   **Custom Actions:** Define new actions by creating classes that inherit from `BaseAction` and `BaseActionConfig` and adding them to the `actions` list in `server.py`.
*   **Different Telephony Providers:** Modify the `telephony_config` and inbound call configurations in `server.py` to use Vonage or other supported providers.
*   **Different Transcribers/Synthesizers:** Update the `transcriber_factory` and `synthesizer_factory` or provide specific configurations in the outbound call request.

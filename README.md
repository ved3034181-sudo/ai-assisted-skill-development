# AI Question & Answering System

A modular Streamlit chat application that answers questions using Google's
Gemini API. It supports follow-up questions by sending successful conversation
turns to the selected Gemini model.

## Features

- Chat-style interface built with Streamlit.
- Multi-turn conversation history stored in Streamlit session state.
- Configurable Gemini model and response temperature.
- Loading indicator while a response is generated.
- Input validation and clear conversation control.
- User-friendly configuration and API error messages.
- API credentials loaded from a local `.env` file.
- Unit tests that mock Gemini; running the tests does not require a Gemini API
  key or make network calls.

## Architecture

- **UI (`app/main.py`)** renders the Streamlit chat, manages per-session
  conversation state, and displays safe status messages.
- **Configuration (`app/config/settings.py`)** loads `.env` values and
  validates required and optional settings.
- **Gemini service (`app/services/gemini_service.py`)** initializes the
  official `google-genai` client, converts conversation turns to Gemini
  contents, supplies the system instruction and generation settings, and
  returns the answer.
- **Prompt (`app/prompts/qa_prompt.py`)** stores the reusable system
  instruction separately from UI code.
- **Logging (`app/utils/logging_config.py`)** configures standard application
  logging without recording credentials or complete conversations.
- **Tests (`tests/`)** cover configuration, service behavior, and safe UI error
  handling with mocked API responses.

## Project structure

```text
.
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── qa_prompt.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging_config.py
│   └── main.py
├── streamlit_app.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_gemini_service.py
│   └── test_main.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run.sh
```

## Prerequisites

- Python **3.10 or newer**.
- `pip` (included with standard Python installations).
- Internet access when using the application to call the Gemini API.
- A Google Gemini API key.

The dependencies are declared in `requirements.txt`; the Google Gen AI SDK
(`google-genai`) is used rather than the legacy `google-generativeai` package.

## Obtain a Google Gemini API key

1. Open [Google AI Studio's API key page](https://aistudio.google.com/apikey).
2. Sign in and create or select a Google Cloud project as prompted.
3. Create an API key and copy it to your local `.env` file as described below.

Treat the key as a secret. Do not paste it into source code, screenshots, issue
reports, or chat messages.

## Create and activate a virtual environment

Run these commands from the project root.

Create the environment:

```shell
python -m venv .venv
```

Activate on macOS/Linux:

```shell
source .venv/bin/activate
```

Activate on Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use Command Prompt or follow your
organization's PowerShell policy instead of weakening the machine-wide policy.

## Install dependencies

With the virtual environment activated:

```shell
python -m pip install -r requirements.txt
```

## Configure `.env`

Create the local `.env` file by copying `.env.example`.

macOS/Linux:

```shell
cp .env.example .env
```

Windows Command Prompt:

```bat
copy .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the placeholder key with your own:

```dotenv
GEMINI_API_KEY=insert_key_here
GEMINI_MODEL=gemini-3.8-flash
TEMPERATURE=0.2
```

`GEMINI_API_KEY` is required. `GEMINI_MODEL` and `TEMPERATURE` have defaults
when omitted. The application currently defaults to the stable `gemini-3.8-flash`
model. See [Google's Gemini API model catalog](https://ai.google.dev/gemini-api/docs/models)
for current model IDs and availability.

### Change the model or generation settings

Set `GEMINI_MODEL` in `.env` to another model ID available to your Google
project, for example:

```dotenv
GEMINI_MODEL=gemini-3.8-flash
```

The configured model is displayed in the app sidebar. Google may change model
availability; check the model catalog before switching.

Set `TEMPERATURE` to a numeric value from `0` through `2`. Lower values
generally produce more focused, less varied responses; higher values allow more
variation. The default is `0.2`. Restart or rerun the app after changing
`.env` so the new settings are loaded.

## Run the Streamlit application

With the environment activated and `.env` configured:

```shell
streamlit run streamlit_app.py
```

On macOS/Linux, the helper script runs the same command from the project
directory (and forwards any additional Streamlit arguments):

```shell
chmod +x run.sh
./run.sh
```

Open the local URL printed by Streamlit in your browser. Ask a question in the
chat input; successful turns remain in the current Streamlit session for
follow-up questions. Use **Clear** in the sidebar to reset the
history.

## Run tests

Tests use mocked Gemini clients and responses, do not call the Gemini API, and
do not need a real API key. From the project root with dependencies installed:

```shell
pytest
```

## Example questions

- “Explain photosynthesis in three steps.”
- “What is the difference between a list and a tuple in Python?”
- “Suggest a simple weeknight meal using lentils.”
- Follow-up: “Can you make the explanation shorter?”

## Troubleshooting

- **The app says Gemini is not configured:** ensure `.env` exists in the
  project root and contains a non-empty `GEMINI_API_KEY`. Start Streamlit from
  the project root.
- **Authentication or access errors:** check that the key is valid, enabled for
  the Gemini API, and associated with a project that has access to the selected
  model. Never include the key in support requests.
- **Model not found or unavailable:** confirm the `GEMINI_MODEL` ID in
  [Google's model catalog](https://ai.google.dev/gemini-api/docs/models) and
  verify it is available to your project.
- **Invalid temperature:** set `TEMPERATURE` to a number between `0` and `2`,
  such as `0.2`.
- **Dependency/import errors:** activate the project's virtual environment and
  run `python -m pip install -r requirements.txt`.
- **PowerShell cannot activate the environment:** use Command Prompt or consult
  your machine's PowerShell policy; avoid changing system-wide security
  settings for this project.
- **Gemini request failed:** check internet access and service availability,
  then retry. The application intentionally shows a generic error rather than
  exposing provider details.

## Security considerations

- `.env` is ignored by `.gitignore`; never commit it. `.env.example` is a
  placeholder template and is safe to share.
- Keep API keys out of source code, logs, screenshots, terminal transcripts,
  and error reports. If a key is exposed, revoke it and create a replacement.
- The application sends the current question and successful conversation
  history to Google Gemini to generate an answer. Do not submit information you
  are not permitted to share with the service.
- API errors are handled with generic user-facing messages; tests verify
  sensitive details are not rendered.
- Conversation history is held in Streamlit session state and can be cleared
  from the sidebar. It is not persisted by this application between sessions.

## Stop the application and deactivate the environment

Stop Streamlit by pressing **Ctrl+C** in the terminal where it is running.

Deactivate the virtual environment when finished:

```shell
deactivate
```

## Future enhancements

- Add persistent conversation storage with explicit retention controls.
- Support export and import of user-selected conversation transcripts.
- Offer optional model and temperature controls in the sidebar.
- Add streaming responses and richer feedback controls.
- Expand automated UI and accessibility testing.

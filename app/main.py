import logging
import sys
from pathlib import Path

import streamlit as st

# Direct script execution puts the app directory, not the project root, on
# sys.path. Add the package root so the documented absolute imports resolve.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import SettingsError, get_gemini_model, load_settings
from app.services.gemini_service import GeminiService, GeminiServiceError
from app.utils.logging_config import configure_logging


logger = logging.getLogger(__name__)


def main() -> None:
    """Render the chat interface and process the submitted question."""
    configure_logging()
    st.set_page_config(page_title="AI Question & Answering System", page_icon="💬")
    st.title("AI Question & Answering System")
    st.caption(
        "Ask questions and get clear answers powered by a Google Gemini AI model."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    try:
        settings = load_settings()
    except SettingsError as exc:
        settings = None
        st.error(str(exc))

    with st.sidebar:
        st.subheader("Gemini")
        model_name = settings.gemini_model if settings else get_gemini_model()
        st.write(f"Model: `{model_name}`")
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []
            logger.info("Conversation cleared.")
            st.rerun()

    st.subheader("Conversation")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask Gemini a question",
        disabled=settings is None,
    )
    if question is None:
        return

    question = question.strip()
    if not question:
        st.warning("Enter a question before submitting.")
        return
    if settings is None:
        return

    user_message = {
        "role": "user",
        "content": question,
        "include_in_history": False,
    }
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Gemini is thinking..."):
            try:
                answer = GeminiService(settings).generate_answer(
                    question, st.session_state.messages[:-1]
                )
            except GeminiServiceError:
                error_message = (
                    "Sorry, Gemini couldn't answer just now. "
                    "Check your settings or try again."
                )
                st.error(error_message)
                user_message["include_in_history"] = False
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "include_in_history": False,
                    }
                )
                return

        st.markdown(answer)

    user_message["include_in_history"] = True
    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "include_in_history": True}
    )


if __name__ == "__main__":
    main()

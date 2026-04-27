import logging

import gradio as gr
from src.main import run_crag_pipeline

logger = logging.getLogger(__name__)


def chat_interface(user_message, history):
    try:
        return run_crag_pipeline(user_message)
    except Exception as e:
        logger.error("Unhandled error in chat interface: %s", e)
        return "Something went wrong. Please try again."

UserInterface = gr.ChatInterface(
    fn = chat_interface,
    title = 'Ask Craig',
    description = '''Ask questions about your local PDFs.
    System will automatically verify facts via Web Search if local data is insufficient.''',
    examples = ['What is the main argument in the uploaded PDF?', 'Summarize the latest trends mentioned.'],
    cache_examples = False,
    fill_height=True,
)

if __name__ == "__main__":
    UserInterface.launch(theme='soft', share=False,
                        pwa=True, show_api=False,
                        title='Ask Craig',
                        # favicon_path="icon.png",
                        )

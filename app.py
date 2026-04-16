import gradio as gr
from src.main import run_crag_pipeline

def chat_interface(user_message, history):
    response = run_crag_pipeline(user_message)
    return response

UserInterface = gr.ChatInterface(
    fn = chat_interface, 
    title = 'Ask Craig',
    description = '''Ask questions about your local PDFs. 
    System will automatically verify facts via Web Search if local data is insufficient.''',
    theme = 'soft',
    examples = ['What is the main argument in the uploaded PDF?', 'Summarize the latest trends mentioned.'],
    cache_examples = False,
)

if __name__ == "__main__":
    UserInterface.launch(share=False)

import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Page configuration
st.set_page_config(
    page_title="Visor Inteligente de Imágenes",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Title and description
st.title("🔎 Visor Inteligente con IA")
st.markdown("### Analiza imágenes con ayuda de inteligencia artificial")

st.write(
    "Esta herramienta te permite subir una imagen y obtener una descripción automática "
    "generada por IA. También puedes añadir contexto o hacer preguntas específicas "
    "para obtener un análisis más detallado."
)

# Load and display header image
try:
    header_image = Image.open("robotlupa.jpg")
    st.image(header_image, width=250)
except Exception as e:
    st.warning(f"No se pudo cargar la imagen principal: {e}")

# API Key input
ke = st.text_input('🔑 Ingresa tu API Key de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke if ke else ""

api_key = os.environ['OPENAI_API_KEY']

# Initialize OpenAI client
if api_key:
    client = OpenAI(api_key=api_key)

# File uploader
uploaded_file = st.file_uploader("📤 Sube una imagen para analizar", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("🖼️ Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle for additional context
show_details = st.toggle("➕ Añadir contexto o pregunta personalizada", value=False)

if show_details:
    additional_details = st.text_area(
        "✍️ Escribe aquí información adicional o lo que quieres saber:",
        disabled=not show_details
    )

# Analyze button
analyze_button = st.button("🚀 Analizar imagen", type="primary")

# Main logic
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("🧠 Procesando imagen..."):
        base64_image = encode_image(uploaded_file)
    
        prompt_text = "Describe detalladamente lo que ves en la imagen en español."
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nContexto adicional del usuario:\n{additional_details}"
            )
    
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]
    
        try:
            full_response = ""
            message_placeholder = st.empty()

            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
    
        except Exception as e:
            st.error(f"Ocurrió un error durante el análisis: {e}")

else:
    if not uploaded_file and analyze_button:
        st.warning("⚠️ Primero debes subir una imagen.")
    if not api_key:
        st.warning("⚠️ Ingresa tu API Key para continuar.")

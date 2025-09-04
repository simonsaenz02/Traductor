import os
import glob
import time
import streamlit as st
from PIL import Image
from gtts import gTTS
from googletrans import Translator
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events


# ----------------- CONFIGURACIÓN DE PÁGINA -----------------
st.set_page_config(
    page_title="Traductor de Voz",
    layout="wide"
)

# ----------------- ESTILOS -----------------
st.markdown(
    """
    <style>
    .title {text-align: center; font-size: 40px; font-weight: bold; color: #2c3e50;}
    .subtitle {text-align: center; font-size: 18px; color: #7f8c8d;}
    .block {padding: 1.5rem; border-radius: 12px; background-color: #f9f9f9; margin-bottom: 1rem;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<p class='title'>Traductor de Voz</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Habla, traduce y escucha el resultado en segundos</p>", unsafe_allow_html=True)

# Imagen decorativa
col1, col2, col3 = st.columns([1,2,1])
with col2:
    image = Image.open("OIG7.jpg")
    st.image(image, use_container_width=True)


# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.header("Guía de uso")
    st.markdown(
        """
        1. Presiona **Escuchar** y dicta el texto.  
        2. Elige idioma de entrada y salida.  
        3. Ajusta el acento si lo deseas.  
        4. Genera el audio con el texto traducido.  
        """
    )


# ----------------- CAPTURA DE VOZ -----------------
st.markdown("### Paso 1: Captura tu voz")
st.write("Presiona el botón y comienza a hablar cuando aparezca la señal.")

stt_button = Button(label="Iniciar escucha", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)


# ----------------- PROCESO DE TRADUCCIÓN -----------------
if result and "GET_TEXT" in result:
    text = str(result.get("GET_TEXT"))
    
    # Mostrar el texto capturado ANTES de traducir
    st.markdown("### Texto capturado")
    st.info(text)

    st.markdown("### Paso 2: Selecciona opciones de traducción")
    st.write("Configura idioma de entrada, salida y el acento de la voz.")

    # Idioma de entrada
    in_lang = st.selectbox(
        "Idioma de entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés")
    )
    input_language = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }[in_lang]

    # Idioma de salida
    out_lang = st.selectbox(
        "Idioma de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés")
    )
    output_language = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }[out_lang]

    # Acento
    english_accent = st.selectbox(
        "Acento",
        ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica")
    )
    tld_map = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }
    tld = tld_map[english_accent]

    # ----------------- FUNCIÓN DE TRADUCCIÓN -----------------
    translator = Translator()

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        my_file_name = text[0:20] if text else "audio"
        os.makedirs("temp", exist_ok=True)
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    st.markdown("### Paso 3: Generar resultado")

    if st.button("Convertir texto a audio"):
        file_name, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{file_name}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")

        st.markdown("#### Texto traducido:")
        st.success(output_text)

    # Limpieza de audios viejos
    def remove_files(n):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

    remove_files(7)

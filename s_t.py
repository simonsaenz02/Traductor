import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Configuración de la página
st.set_page_config(
    page_title="Traductor de Voz Multilenguaje",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #444;
        text-align: center;
        margin-bottom: 2rem;
    }
    .instruction-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1.5rem;
    }
    .language-section {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .stButton button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        height: 50px;
    }
    .result-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1.5rem;
    }
    .sidebar-title {
        font-size: 1.3rem;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown('<p class="main-header">Traductor de Voz Multilenguaje</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Convierte tu voz en texto y tradúcelo a diferentes idiomas</p>', unsafe_allow_html=True)

# Dividir en columnas para mejor distribución
col1, col2 = st.columns([1, 1])

with col1:
    # Imagen representativa
    try:
        image = Image.open('OIG7.jpg')
        st.image(image, width=350, caption="Sistema de traducción por voz")
    except:
        st.info("Imagen no encontrada. Agrega una imagen representativa para mejorar la experiencia.")

    # Instrucciones de uso
    st.markdown('<div class="instruction-box">', unsafe_allow_html=True)
    st.subheader("Instrucciones de uso:")
    st.write("""
    1. Presiona el botón 'Iniciar reconocimiento de voz'
    2. Espera a que aparezca el indicador de grabación
    3. Habla claramente lo que deseas traducir
    4. Selecciona los idiomas de entrada y salida
    5. Elige el acento deseado para la pronunciación
    6. Presiona 'Convertir' para obtener tu traducción
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Sección de reconocimiento de voz
    st.markdown("### Reconocimiento de voz")
    st.write("Presiona el botón para comenzar a grabar tu voz. Habla claramente después de hacer clic.")
    
    stt_button = Button(label="Iniciar reconocimiento de voz", width=400, height=60)
    
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
        debounce_time=0)

# Barra lateral con información adicional
with st.sidebar:
    st.markdown('<p class="sidebar-title">Configuración de Traducción</p>', unsafe_allow_html=True)
    st.write("""
    Este traductor utiliza tecnología de reconocimiento de voz para capturar tu audio
    y convertirlo en texto. Luego, utiliza el servicio de traducción de Google para
    traducir entre múltiples idiomas.
    """)
    
    st.markdown("---")
    st.subheader("Idiomas disponibles")
    st.write("""
    - Inglés
    - Español
    - Bengalí
    - Coreano
    - Mandarín
    - Japonés
    """)
    
    st.markdown("---")
    st.subheader("Acentos disponibles")
    st.write("""
    - Español (México)
    - Inglés (Reino Unido)
    - Inglés (Estados Unidos)
    - Inglés (Canadá)
    - Inglés (Australia)
    - Inglés (Irlanda)
    - Inglés (Sudáfrica)
    """)

# Procesamiento de resultados
if result:
    if "GET_TEXT" in result:
        st.markdown("### Texto reconocido:")
        st.info(result.get("GET_TEXT"))
    
    try:
        os.mkdir("temp")
    except:
        pass
    
    # Configuración de idiomas
    st.markdown("### Configuración de traducción")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="language-section">', unsafe_allow_html=True)
        in_lang = st.selectbox(
            "Idioma de origen",
            ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés"),
            help="Selecciona el idioma en el que hablaste"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="language-section">', unsafe_allow_html=True)
        out_lang = st.selectbox(
            "Idioma de destino",
            ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés"),
            help="Selecciona el idioma al que quieres traducir"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Configuración de acento
    st.markdown('<div class="language-section">', unsafe_allow_html=True)
    english_accent = st.selectbox(
        "Acento de pronunciación",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canada",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
        help="Selecciona el acento para la pronunciación del audio"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mapeo de idiomas
    lang_map = {
        "Inglés": "en",
        "Español": "es",
        "Bengalí": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }
    
    input_language = lang_map[in_lang]
    output_language = lang_map[out_lang]
    
    # Mapeo de acentos
    accent_map = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }
    
    tld = accent_map[english_accent]
    
    # Función de conversión
    def text_to_speech(input_language, output_language, text, tld):
        translator = Translator()
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    
    # Opción para mostrar texto
    display_output_text = st.checkbox("Mostrar texto traducido", value=True)
    
    # Botón de conversión
    if st.button("Traducir y generar audio"):
        text = str(result.get("GET_TEXT"))
        if text:
            with st.spinner("Procesando traducción..."):
                result_file, output_text = text_to_speech(input_language, output_language, text, tld)
                audio_file = open(f"temp/{result_file}.mp3", "rb")
                audio_bytes = audio_file.read()
                
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown("### Resultado de la traducción")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
                
                if display_output_text:
                    st.markdown("**Texto traducido:**")
                    st.success(output_text)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No se detectó texto para traducir. Por favor, intenta nuevamente.")

# Función de limpieza
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

# Información adicional al final
st.markdown("---")
st.markdown("""
### Acerca de esta aplicación
Esta herramienta permite traducir tu voz a diferentes idiomas y generar una 
pronunciación auditiva del texto traducido. Utiliza tecnología de reconocimiento 
de voz integrada en los navegadores modernos y servicios de traducción de Google.
""")

# Limpieza de archivos temporales
remove_files(7)

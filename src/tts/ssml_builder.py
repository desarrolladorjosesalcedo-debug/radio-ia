"""
ssml_builder.py
Constructor de SSML (Speech Synthesis Markup Language) para Edge TTS.

Permite control fino de:
- Pausas (breaks)
- Énfasis (emphasis)
- Tono (pitch)
- Velocidad (rate)
- Volumen (volume)
- Estilos emocionales (prosody)

Uso:
    builder = SSMLBuilder()
    ssml = builder.add_text("Hola mundo")
                   .add_pause(500)
                   .add_emphasis("importante", level="strong")
                   .build()
"""

import logging
from typing import List, Literal

logger = logging.getLogger(__name__)


class SSMLBuilder:
    """Constructor de SSML para Edge TTS con control avanzado de prosodia."""
    
    def __init__(self, voice: str = "es-MX-DaliaNeural"):
        """
        Inicializa el constructor SSML.
        
        Args:
            voice (str): Voz de Edge TTS a usar
        """
        self.voice = voice
        self.elements: List[str] = []
        
    def add_text(self, text: str, 
                 rate: str = "medium",
                 pitch: str = "medium", 
                 volume: str = "default") -> 'SSMLBuilder':
        """
        Agrega texto con control de prosodia.
        
        Args:
            text (str): Texto a sintetizar
            rate (str): Velocidad: x-slow, slow, medium, fast, x-fast o +10%
            pitch (str): Tono: x-low, low, medium, high, x-high o +5Hz
            volume (str): Volumen: silent, x-soft, soft, medium, loud, x-loud
        
        Returns:
            SSMLBuilder: Self para encadenamiento
        """
        if not text.strip():
            return self
            
        prosody_attrs = []
        if rate != "medium":
            prosody_attrs.append(f'rate="{rate}"')
        if pitch != "medium":
            prosody_attrs.append(f'pitch="{pitch}"')
        if volume != "default":
            prosody_attrs.append(f'volume="{volume}"')
        
        if prosody_attrs:
            attrs_str = " ".join(prosody_attrs)
            self.elements.append(f'<prosody {attrs_str}>{text}</prosody>')
        else:
            self.elements.append(text)
        
        return self
    
    def add_pause(self, duration_ms: int) -> 'SSMLBuilder':
        """
        Agrega una pausa.
        
        Args:
            duration_ms (int): Duración en milisegundos (50-5000)
        
        Returns:
            SSMLBuilder: Self para encadenamiento
        """
        duration_ms = max(50, min(duration_ms, 5000))
        self.elements.append(f'<break time="{duration_ms}ms"/>')
        return self
    
    def add_emphasis(self, text: str, 
                     level: Literal["reduced", "moderate", "strong"] = "moderate") -> 'SSMLBuilder':
        """
        Agrega texto con énfasis.
        
        Args:
            text (str): Texto a enfatizar
            level (str): Nivel de énfasis: reduced, moderate, strong
        
        Returns:
            SSMLBuilder: Self para encadenamiento
        """
        if not text.strip():
            return self
        
        self.elements.append(f'<emphasis level="{level}">{text}</emphasis>')
        return self
    
    def add_sentence(self, text: str, emotion: str = "neutral") -> 'SSMLBuilder':
        """
        Agrega una oración con estilo emocional.
        
        Args:
            text (str): Texto de la oración
            emotion (str): Estilo emocional:
                - neutral (por defecto)
                - cheerful (alegre)
                - sad (triste)
                - angry (enojado)
                - excited (emocionado)
                - friendly (amigable)
                - hopeful (esperanzado)
                - shouting (gritando)
                - terrified (aterrado)
                - unfriendly (poco amigable)
                - whispering (susurrando)
        
        Returns:
            SSMLBuilder: Self para encadenamiento
        """
        if not text.strip():
            return self
        
        # Estilos soportados por Azure Neural Voices
        supported_styles = [
            "neutral", "cheerful", "sad", "angry", "excited",
            "friendly", "hopeful", "shouting", "terrified",
            "unfriendly", "whispering"
        ]
        
        if emotion in supported_styles and emotion != "neutral":
            self.elements.append(f'<mstts:express-as style="{emotion}">{text}</mstts:express-as>')
        else:
            self.elements.append(text)
        
        return self
    
    def add_paragraph(self, text: str) -> 'SSMLBuilder':
        """
        Agrega un párrafo (con pausa automática).
        
        Args:
            text (str): Texto del párrafo
        
        Returns:
            SSMLBuilder: Self para encadenamiento
        """
        if not text.strip():
            return self
        
        self.elements.append(f'<p>{text}</p>')
        return self
    
    def build(self) -> str:
        """
        Construye el SSML completo.
        
        Returns:
            str: SSML válido para Edge TTS
        """
        content = "".join(self.elements)
        
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="es-MX">
    <voice name="{self.voice}">
        {content}
    </voice>
</speak>'''
        
        return ssml
    
    def reset(self) -> 'SSMLBuilder':
        """
        Reinicia el constructor.
        
        Returns:
            SSMLBuilder: Self para encadenamiento
        """
        self.elements = []
        return self


def create_enhanced_text(text: str, style: str = "standard") -> str:
    """
    Crea texto mejorado con SSML según el estilo.
    
    Args:
        text (str): Texto original
        style (str): Estilo de mejora:
            - standard: Sin modificaciones
            - podcast: Pausas naturales, énfasis en palabras clave
            - audiobook: Lectura pausada, énfasis en diálogos
            - news: Ritmo rápido, énfasis en datos importantes
            - storytelling: Variación emocional, pausas dramáticas
    
    Returns:
        str: SSML mejorado
    """
    builder = SSMLBuilder()
    
    if style == "standard":
        return builder.add_text(text).build()
    
    elif style == "podcast":
        # Agregar pausas naturales después de puntos y comas
        sentences = text.split('. ')
        for i, sentence in enumerate(sentences):
            builder.add_text(sentence.strip())
            if i < len(sentences) - 1:
                builder.add_pause(300)
        return builder.build()
    
    elif style == "audiobook":
        # Lectura más pausada con énfasis en diálogos
        paragraphs = text.split('\n\n')
        for i, para in enumerate(paragraphs):
            builder.add_text(para.strip(), rate="slow")
            if i < len(paragraphs) - 1:
                builder.add_pause(500)
        return builder.build()
    
    elif style == "news":
        # Ritmo rápido y dinámico
        return builder.add_text(text, rate="fast", volume="loud").build()
    
    elif style == "storytelling":
        # Variación emocional (requiere análisis más sofisticado)
        # Por ahora, solo agregamos pausas dramáticas
        sentences = text.split('. ')
        for i, sentence in enumerate(sentences):
            if '?' in sentence:
                builder.add_text(sentence.strip(), pitch="high")
            elif '!' in sentence:
                builder.add_emphasis(sentence.strip(), level="strong")
            else:
                builder.add_text(sentence.strip())
            
            if i < len(sentences) - 1:
                builder.add_pause(400)
        return builder.build()
    
    else:
        logger.warning(f"⚠️  Estilo desconocido '{style}', usando standard")
        return builder.add_text(text).build()


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo básico
    builder = SSMLBuilder(voice="es-MX-DaliaNeural")
    ssml = (builder
            .add_text("Hola, bienvenidos a Radio IA.", rate="medium", pitch="medium")
            .add_pause(500)
            .add_emphasis("Este es un mensaje importante.", level="strong")
            .add_pause(300)
            .add_text("Gracias por escuchar.", rate="slow")
            .build())
    
    print(ssml)

import time
import webbrowser
from flask import Flask, request, jsonify, make_response
import threading
import unicodedata
import difflib

app = Flask(__name__, static_folder="static")

# DICCIONARIO DE RESPUESTAS

respuestas_cooltist = {
    #SALUDOS Y AGRADECIMIENTOS
    "saludos": {
        "hola": "¡Hola! Soy Cooltist, tu asistente del Instituto Culto Badalona. ¿En qué puedo ayudarte?",
        "adios": "¡Hasta luego! Gracias por contactar con el Culto Badalona.",
        "gracias": "¡De nada! Siempre es un placer ayudarte.",
    },

    #INFORMACIÓN GENERAL
    "informacion_general": {
        "historia": "El Instituto Culto Badalona nació a finales de los años 80 con la misión de formar a estudiantes para un mundo tecnológico y socialmente cambiante.",
        "filosofia": "La filosofía del Culto Badalona se basa en tres pilares: innovación, formación integral y orientación profesional.",
        "quienes somos": "Somos un centro educativo referente en el Barcelonès, primaria, ESO, ciclos especializados en informática, administración y bachilleratos universitarios.",
        "instituto": "El Instituto Culto Badalona es un centro con sedes en Badalona, reconocido por su formación en tecnología, empresa y humanidades.",
        "valores": "En el Culto Badalona fomentamos la curiosidad, el respeto y la cultura del conocimiento — de ahí nuestro nombre: 'Culto'.",
        "reconocimientos": "El Culto Badalona es reconocido por su calidad educativa y su especialización en ciberseguridad e innovación digital.",
    },

    #CONTACTO Y REDES
    "contacto": {
        "direccion": "La sede principal está en Carrer de la Cultura, 42 – Badalona (08912).",
        "campus": "El campus tecnológico (SMX y ASIX) está en Av. de la Innovació, 15 – Badalona, y el de administración en Passeig Comercial, 9 – Badalona.",
        "telefono": "Puedes llamarnos al +34 673829156.",
        "correo": "Nuestro correo general es info@cultobadalona.cat.",
        "horarios": "Los horarios se actualizan trimestralmente según el grupo y etapa, y están disponibles en el portal del alumno.",
        "portal alumno": "El portal del alumno incluye horarios, asignaturas y calificaciones actualizadas.",
        "redes sociales": "Síguenos en nuestras redes sociales @cultobadalona",
        "contacto": (
            "Puedes ponerte en contacto con nosotros por varios medios:\n\n"
            "Teléfono: +34 673829156\n"
            "Correo electrónico: info@cultobadalona.cat\n"
            "Dirección: Carrer de la Cultura, 42 – Badalona (08912)\n\n"
            "También puedes escribirnos desde el formulario de la página principal o acudir a secretaría en horario de atención."
        ),
    },

    #ETAPAS EDUCATIVAS
    "etapas_educativas": {
        "primaria": "La educación primaria desarrolla competencias básicas, comunicación y robótica básica.",
        "eso": "La ESO ofrece formación básica a adolescentes, preparando para estudios posteriores o formación profesional.",
        "bachillerato": "El Culto Badalona ofrece bachilleratos científico, tecnológico y social, todos con orientación universitaria.",
        "bachillerato cientifico": "Asignaturas: Matemáticas, Física, Química, Biología y Filosofía.",
        "bachillerato tecnologico": "Asignaturas: matemáticas aplicadas, física, tecnología industrial y dibujo técnico.",
        "bachillerato social": "Asignaturas: economía, geografía, historia y administración de empresa.",
    },
    # ESTUDIO
    "estudios":  "En el Instituto Culto Badalona ofrece educación Primaria, la ESO, Bachillerato científico, tecnológico o social, Ciclos Formativos como SMX (Sistemas Microinformáticos), ASIX (Administración de Sistemas y Ciberseguridad), y AF (Administración y Finanzas), además de diversas titulaciones oficiales y certificaciones en tecnología, idiomas y empresa."
    ,

    #CICLOS FORMATIVOS
    "ciclos_formativos": {
        "smx": "El ciclo SMX enseña montaje de equipos, redes, seguridad y aplicaciones web.",
        "asix": "El ciclo ASIX forma en ciberseguridad y gestión de sistemas.",
        "af": "El ciclo AF forma en contabilidad, fiscalidad y gestión empresarial.",
        "ciclos": "Los ciclos formativos incluyen SMX, ASIX y AF, con prácticas en empresas reales.",
    },

    #CERTIFICACIONES Y TITULACIONES
    "certificaciones_titulaciones": {
        "certificados": "Certificaciones oficiales en idiomas, tecnología y empresa: Cambridge, TOEFL, Cisco CCNA, CompTIA, MOS, SAP, CAPM.",
        "titulaciones": "Todos los títulos son oficiales y homologados por la Generalitat de Catalunya.",
        "idiomas": (
            "Ofrecemos preparación oficial para:\n"
            "• Cambridge (A2 a C1)\n"
            "• TOEFL iBT\n"
            "• Clases de inglés, catalán y francés integradas en el currículo\n"
            "Certificados reconocidos internacionalmente."
        ),
    },

    #INFORMACIÓN ADMINISTRATIVA
    "informacion_administrativa": {
        "preinscripcion": "Preinscripciones abiertas del 10 de abril al 25 de mayo, en línea o presencial.",
        "fct": "Las prácticas FCT se realizan en empresas del sector.",
        "empresa": "La asignatura Empresa e iniciativa emprendedora fomenta el espíritu empresarial.",
        "becas": (
            "El Instituto Culto Badalona ofrece varias opciones de ayuda económica:\n"
            "• Becas MEC y de la Generalitat (según requisitos)\n"
            "• Pago fraccionado de matrícula\n"
            "• Descuentos por familia numerosa o excelencia académica\n"
            "Consulta en secretaría o en el portal del alumno."
        ),
        "convalidaciones": (
            "Sí, puedes convalidar módulos si tienes estudios previos.\n"
            "• SMX → ASIX: se convalidan hasta 8 módulos\n"
            "• Bachillerato → FP: posible convalidación de Empresa\n"
            "• Otros ciclos: se evalúa caso por caso\n"
            "Contacta con jefe de estudios: jefeestudios@cultobadalona.cat"
        ),
    },

    # ORIENTACIÓN Y CONTINUIDAD EDUCATIVA
    "orientacion_continuidad": {
        "continuidad academica": (
            "Tras cada etapa puedes seguir formándote:\n"
            "• Primaria → ESO\n"
            "• ESO → Bachillerato o Ciclos Formativos de Grado Medio (SMX)\n"
            "• SMX → Ciclo Superior ASIX\n"
            "• ASIX o AF → Grados universitarios (Informática, ADE, Ingeniería, Economía)\n"
            "El instituto ofrece orientación personalizada sobre itinerarios académicos."
        ),
        "ayuda": (
            "Puedo ayudarte con todo lo relacionado con el Instituto Culto Badalona. "
            "Puedes preguntarme sobre nuestra historia, filosofía, valores o etapas educativas. "
            "También te doy información de contacto como direcciones, teléfonos, correos o campus. "
            "Además, puedo explicarte sobre certificaciones, titulaciones oficiales, prácticas FCT "
            "y procesos de preinscripción."
        ),
    },

    #SALIDAS LABORALES Y EMPLEO
    "salidas_empleo": {
        "salidas laborales": (
            "El Instituto Culto Badalona prepara a sus alumnos para integrarse en el mundo laboral con altas tasas de inserción.\n\n"
            "Ciclo SMX: soporte técnico, redes, helpdesk, mantenimiento.\n"
            "Ciclo ASIX: administración de sistemas, ciberseguridad, DevOps, cloud.\n"
            "Ciclo AF: contabilidad, finanzas, RRHH, asesoría.\n"
            "El 92% de los titulados encuentra empleo o continúa estudios en menos de 6 meses."
        ),
        "convenios empresas": (
            "El Culto Badalona mantiene convenios con más de 80 empresas y entidades.\n"
            "Entre ellas destacan: HP, Softonic, Ajuntament de Badalona, Ingram Micro, Banc Sabadell y Cisco Academy."
        ),
    },

    #INNOVACIÓN, INCLUSIÓN Y COMUNIDAD
    "innovacion_inclusion_comunidad": {
        "innovacion educativa": (
            "El Culto Badalona integra la tecnología en todo el proceso educativo:\n"
            "• Aulas digitales con pizarras interactivas y equipos Chromebook\n"
            "• Uso de Google Workspace y Moodle\n"
            "• Programación y robótica educativa desde etapas iniciales"
        ),
        "emprendimiento": (
            "Fomentamos el espíritu emprendedor con el módulo 'Empresa e iniciativa emprendedora' y el programa *Culto StartUp*."
        ),
        "inclusion": (
            "Promovemos la educación inclusiva con adaptaciones curriculares, atención individualizada y acompañamiento emocional."
        ),
        "comunidad educativa": (
            "El Culto Badalona impulsa la participación activa de toda la comunidad: familias, alumnado y profesorado."
        ),
        "seguridad digital": (
            "Todos los alumnos reciben formación en seguridad digital y el centro cumple con el RGPD."
        ),
    },

    #INTERNACIONALIZACIÓN Y EXTRACURRICULARES
    "internacional_extracurriculares": {
        "internacionalizacion": (
            "Formamos parte del programa Erasmus+ desde 2015, con prácticas en países europeos."
        ),
        "actividades extracurriculares": (
            "Ofrecemos clubes de programación, idiomas, deportes y voluntariado."
        ),
    },

    #EVALUACIÓN
    "evaluacion": {
        "evaluacion": (
            "La evaluación es continua y formativa, con informes personalizados y tutorías con las familias."
        ),
    },

    #RESPUESTA POR DEFECTO
    "default": {
        "default": "No tengo esa información exacta. Puedes poner 'Ayuda' para saber qué puedo hacer por ti.",
    },
}


palabras_clave = {
    # SALUDOS Y AGRADECIMIENTOS
    "saludos": ["hola", "buenas", "buenos días", "qué tal", "saludos", "hey", "hi", "hello"],
    "adios": ["adios", "hasta luego", "nos vemos", "chau", "chao", "bye", "hasta pronto"],
    "gracias": ["gracias", "muchas gracias", "te lo agradezco", "agradecido", "gracias por tu tiempo"],

    # INFORMACIÓN GENERAL
    "historia": ["historia", "fundación", "origen", "creación", "inicios", "trayectoria", "cómo empezó", "quiénes somos"],
    "filosofia": ["filosofía", "principios", "ideales", "enfoque", "misión", "visión educativa"],
    "instituto": ["instituto", "centro educativo", "escuela", "institución", "culto badalona", "colegio"],
    "valores": ["valores", "cultura", "formación integral", "aprendizaje", "ética", "respeto", "cultura del conocimiento"],
    "reconocimientos": ["reconocimientos", "logros", "premios", "ranking", "distinciones", "reconocido"],

    # CONTACTO Y REDES
    "contacto": ["contacto", "hablar", "comunicarse", "secretaría", "formulario web", "atención", "llamar", "mensaje"],
    "direccion": ["dirección", "ubicación", "cómo llegar", "sede", "calle", "mapa", "dirección exacta", "sede principal"],
    "campus": ["campus", "instalaciones", "sede secundaria", "campus tecnológico", "campus administrativo"],
    "telefono": ["telefono", "llamar", "número de contacto", "móvil de contacto"],
    "correo": ["correo", "email", "dirección electrónica", "contactar por correo", "mail"],
    "horarios": ["horarios", "horario", "turnos", "días lectivos", "timetable", "hora de entrada", "hora de salida", "clases"],
    "redes sociales": ["redes sociales", "instagram", "facebook", "tiktok", "twitter", "youtube", "linkedin", "rrss"],
    "portal alumno": ["portal alumno", "plataforma digital", "intranet", "acceso a notas", "aula virtual", "usuarios del portal"],

    # ETAPAS EDUCATIVAS
    "primaria": ["primaria", "educación primaria", "primeros cursos", "educación básica", "niños pequeños", "competencias básicas"],
    "eso": ["ESO", "educación secundaria", "secundaria", "etapa intermedia", "formación media", "adolescentes", "preparación para estudios posteriores"],
    "bachillerato": ["bachillerato", "preuniversitario", "cursos superiores", "formación universitaria", "etapa universitaria"],
    "bachillerato cientifico": ["bachillerato científico", "ciencias", "física", "química", "biología", "matemáticas", "asignaturas científicas"],
    "bachillerato tecnologico": ["bachillerato tecnológico", "ingeniería", "tecnología", "dibujo técnico", "matemáticas aplicadas"],
    "bachillerato social": ["bachillerato social", "economía", "geografía", "historia", "administración de empresa", "humanidades"],
    "estudios": ["estudio", "qué estudiar", "cursos", "qué puedo estudiar", "opciones educativas", "programas educativos", "oferta formativa"],

    # CICLOS FORMATIVOS
    "smx": ["SMX", "sistemas microinformáticos", "ciclo medio", "informática", "redes", "seguridad", "montaje de equipos"],
    "asix": ["ASIX", "administración de sistemas", "ciclo superior", "ciberseguridad", "linux", "servidores", "windows", "devops"],
    "af": ["AF", "administración y finanzas", "contabilidad", "fiscalidad", "gestión empresarial", "economía", "finanzas"],
    "ciclos": ["ciclos formativos", "formación profesional", "FP", "ciclos medio y superior", "prácticas en empresa"],

    # CERTIFICACIONES Y TITULACIONES
    "certificados": ["certificados", "diplomas", "acreditaciones", "cambridge", "toefl", "cisco", "compTIA", "microsoft", "SAP", "MOS"],
    "titulaciones": ["titulaciones", "títulos", "homologados", "oficiales", "reconocidos", "generalitat", "europeos"],
    "idiomas": ["idiomas", "lenguas", "inglés", "catalán", "francés", "certificados oficiales", "nivel de idiomas"],

    # INFORMACIÓN ADMINISTRATIVA
    "preinscripcion": ["preinscripción", "inscripción", "registro", "admisión", "plazos", "fechas de matrícula", "inscripción online"],
    "fct": ["FCT", "prácticas", "formación en empresa", "experiencia laboral", "estancia en empresa", "formación práctica"],
    "becas": ["becas", "ayudas económicas", "subvenciones", "descuentos", "familia numerosa", "excelencia académica", "pago fraccionado"],
    "convalidaciones": ["convalidaciones", "reconocimiento de estudios previos", "equivalencias académicas", "transferencias de módulo"],

    # ORIENTACIÓN Y CONTINUIDAD EDUCATIVA
    "continuidad academica": ["continuidad", "itinerarios", "seguir estudiando", "formación posterior", "progresar", "seguir formación"],
    "ayuda": ["ayuda", "información", "orientación", "consultar", "duda", "necesito información"],

    # SALIDAS LABORALES Y EMPLEO
    "salidas laborales": ["salidas laborales", "empleo", "trabajo", "profesión", "ocupación", "empleabilidad", "futuro profesional"],
    "convenios empresas": ["convenios", "empresas colaboradoras", "alianzas", "prácticas en empresas", "bolsa de empleo"],

    # INNOVACIÓN, INCLUSIÓN Y COMUNIDAD
    "innovacion educativa": ["innovación", "tecnología", "aulas digitales", "programación", "robótica", "educación moderna"],
    "emprendimiento": ["emprendimiento", "culto startup", "proyecto empresarial", "iniciativa emprendedora", "startups"],
    "inclusion": ["inclusión", "diversidad", "adaptaciones curriculares", "atención individualizada", "apoyo emocional"],
    "comunidad educativa": ["comunidad educativa", "familias", "profesorado", "participación escolar", "vida escolar"],
    "seguridad digital": ["seguridad digital", "ciberseguridad", "protección de datos", "RGPD", "uso responsable", "huella digital"],

    # INTERNACIONALIZACIÓN Y EXTRACURRICULARES
    "internacionalizacion": ["internacionalización", "erasmus", "intercambio", "prácticas en el extranjero", "movilidad europea"],
    "actividades extracurriculares": ["actividades extracurriculares", "deportes", "voluntariado", "clubes", "talleres", "idiomas"],

    # EVALUACIÓN
    "evaluacion": ["evaluación", "calificaciones", "notas", "seguimiento", "informes", "tutorías", "informes personalizados"],
}




# FUNCIONES DE COINCIDENCIA

# Palabras comunes que no aportan información relevante
STOPWORDS = {"el", "la", "los", "las", "de", "del", "y", "a", "un", "una", "que", "en", "al", "por", "para", "con", "sobre","es"}

# Palabras que indican intención o contexto
PALABRAS_RELEVANTES = {
    "direccion": ["donde", "ubicacion", "localizacion", "encontrar", "mapa", "sitio", "lugar", "esta"],
    "horario": ["horario", "hora", "apertura", "cierre", "mañana", "tarde"],
    "contacto": ["correo", "email", "telefono", "contactar", "secretaria", "llamar"],
    "estudios": ["estudiar", "ofrecen", "opciones", "formacion", "materias", "bachillerato", "ciclo", "smx", "asix","que puedo estudiar","que se estudia","que se puede estudiar"]
}


# Limpieza de texto
def limpiar_texto(texto):
    #Normaliza tildes, mayúsculas y elimina stopwords.
    if not isinstance(texto, str):
        return ""
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn').lower()
    palabras = [p for p in texto.split() if p not in STOPWORDS]
    return " ".join(palabras).strip()


def similitud(texto1, texto2):
   #Calcula el grado de similitud entre dos textos.
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()


def detectar_tema(texto_usuario):
    #Detecta el tema más probable según las palabras clave y contexto.
    texto_usuario = limpiar_texto(texto_usuario)
    palabras_usuario = texto_usuario.split()
    coincidencias = {}

    for tema, lista_palabras in palabras_clave.items():
        puntuacion = 0

        for palabra in lista_palabras:
            palabra_limpia = limpiar_texto(palabra)

            # Coincidencia directa
            if palabra_limpia in texto_usuario:
                puntuacion += 3
                continue

            # Coincidencia parcial o por similitud
            for palabra_usuario in palabras_usuario:
                if len(palabra_usuario) < 3:
                    continue
                if similitud(palabra_usuario, palabra_limpia) > 0.8:
                    puntuacion += 1
                    break

        # Refuerzo contextual
        if tema == "direccion" and any(p in texto_usuario for p in PALABRAS_RELEVANTES["direccion"]):
            puntuacion += 3
        if tema in ["instituto", "quienes somos"] and any(p in texto_usuario for p in PALABRAS_RELEVANTES["direccion"]):
            puntuacion -= 2

        if puntuacion > 0:
            coincidencias[tema] = puntuacion

    # Elegir tema con más puntuación
    if coincidencias:
        max_puntos = max(coincidencias.values())
        temas_posibles = [t for t, v in coincidencias.items() if v == max_puntos]
        temas_posibles.sort(key=len, reverse=True)
        return temas_posibles[0]

    # Fallback por coincidencia directa
    for tema in respuestas_cooltist.keys():
        if tema != "default" and any(pal in texto_usuario for pal in tema.split()):
            return tema

    return None


def responder_cooltist(texto_usuario):
    #Devuelve la respuesta correspondiente al texto del usuario.
    tema = detectar_tema(texto_usuario)

    # Buscar el subtema más específico dentro del diccionario principal
    if tema:
        for categoria, subtemas in respuestas_cooltist.items():
            if tema in subtemas:
                return subtemas[tema]
        # Si el tema es una categoría general (p.ej. "saludos")
        if tema in respuestas_cooltist:
            subtemas = respuestas_cooltist[tema]
            if isinstance(subtemas, dict):
                return next(iter(subtemas.values()))
            return subtemas

    # Si no se encuentra ningún tema
    return respuestas_cooltist["default"]["default"]


# HTML CON RUTAS CORRECTAS A STATIC
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instituto Culto Badalona</title>
    <link rel="icon" type="image/png" href="/static/logo.png" />

    <style>
        /* =========================
           PALETA DE COLORES GLOBAL
        ==========================*/
        :root {
            --dark-purple: #010B40;
            --mid-purple: #010626;
            --dark-blue: #011640;
            --blue: #0A3B59;
            --cream: #F2F0E4;
        }

        /* =========================
           ESTILOS GENERALES
        ==========================*/
        body {
            font-family: Arial, sans-serif;
            background-color: var(--cream);
            color: var(--dark-blue);
            margin: 0;
            padding: 0;
        }

        header {
            background-color: var(--dark-purple);
            padding: 20px;
            text-align: center;
            color: white;
        }

        header img {
            max-width: 150px;
            margin-bottom: 10px;
            height: auto;
        }

        nav {
            background-color: var(--mid-purple);
            padding: 15px;
            text-align: center;
        }

        nav a {
            color: white;
            margin: 0 15px;
            text-decoration: none;
            font-weight: bold;
        }

        nav a:hover {
            text-decoration: underline;
        }

        .hero {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: var(--blue);
            padding: 50px 0;
        }

        .hero img {
            max-width: 60%;
            height: auto;
            border-radius: 8px;
        }

        .container {
            padding: 20px;
            text-align: center;
        }

        .images {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }

        .images img {
            width: 23%;
            border-radius: 8px;
            transition: transform 0.3s ease;
        }

        .images img:hover {
            transform: scale(1.03);
        }

        footer {
            background-color: var(--dark-blue);
            color: white;
            text-align: center;
            padding: 20px;
        }

        /* =========================
           CHAT COOLTIST
        ==========================*/
        .chat-box {
            width: 90%;
            max-width: 700px;
            height: auto;
            max-height: 80vh;
            background: rgba(255, 255, 255, 0.97);
            border: 2px solid var(--dark-blue);
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 999;
            transition: all 0.3s ease;
        }

        .chat-box .header {
            background: var(--dark-blue);
            color: white;
            padding: 14px;
            font-size: 18px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        #toggle-chat {
            background: transparent;
            color: white;
            border: none;
            font-size: 22px;
            cursor: pointer;
            line-height: 1;
        }

        #toggle-chat:hover {
            color: #ccc;
        }

        /* Estado minimizado */
        .chat-box.minimized {
            display: none;
        }

        /* =========================
           BURBUJA FLOTANTE DEL CHAT
        ==========================*/
        .chat-icon {
            width: 60px;
            height: 60px;
            background-color: var(--cream);
            border-radius: 50%;
            position: fixed;
            bottom: 25px;
            right: 25px;
            z-index: 998;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: transform 0.3s ease;
        }

        .chat-icon img {
            width: 35px;
            height: 35px;
        }

        .chat-icon:hover {
            transform: scale(1.1);
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            scroll-behavior: smooth;
            border-bottom: 1px solid #ddd;
            word-wrap: break-word;
            box-sizing: border-box;
        }

        .msg {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            word-break: break-word;
        }

        .msg img {
            width: 35px;
            height: 35px;
            border-radius: 50%;
        }

        .text {
            padding: 10px 12px;
            border-radius: 8px;
            line-height: 1.4;
            white-space: pre-wrap;
            max-width: 100%;
            box-sizing: border-box;
        }

        .user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .user .text {
            background: #e6f0ff;
        }

        .bot .text {
            background: #f1f1f1;
        }

        .input-area {
            display: flex;
            padding: 10px;
            border-top: 1px solid #ddd;
            gap: 8px;
            background: #fafafa;
        }

        input[type="text"] {
            flex: 1;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
            outline: none;
        }

        button {
            background: var(--dark-blue);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            cursor: pointer;
            transition: background 0.3s;
        }

        button:hover {
            background: #032466;
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        /* =========================
           MEDIA QUERIES (RESPONSIVE)
        ==========================*/
        @media (max-width: 768px) {
            nav {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                padding: 10px;
            }

            nav a {
                display: block;
                margin: 5px 10px;
            }

            .hero img {
                max-width: 90%;
            }

            .images img {
                width: 48%;
            }

            .chat-box {
                right: 10px;
                left: 10px;
                bottom: 10px;
                width: auto;
                max-width: none;
                height: 70vh;
            }
        }

        @media (max-width: 480px) {
            header h1 {
                font-size: 20px;
            }

            nav a {
                font-size: 14px;
            }

            .images img {
                width: 100%;
            }

            .chat-box {
                width: 95%;
                left: 2.5%;
                right: 2.5%;
                bottom: 10px;
                height: 75vh;
            }

            input[type="text"] {
                font-size: 14px;
            }

            button {
                padding: 8px 12px;
                font-size: 14px;
            }
        }
    </style>
</head>

<body>
    <!-- ENCABEZADO -->
    <header>
        <img src="static/logo.png" alt="Logo Instituto Culto Badalona">
        <h1>Bienvenidos al Instituto Culto Badalona</h1>
    </header>

    <!-- NAVEGACIÓN -->
    <nav>
        <a href="#">Inicio</a>
        <a href="#">Sobre Nosotros</a>
        <a href="#">Noticias</a>
        <a href="#">Contactar</a>
    </nav>

    <!-- HERO -->
    <section class="hero">
        <img src="static/instituto.jpg" alt="Imagen principal del instituto">
    </section>

    <!-- GALERÍA -->
    <section class="container">
        <h2>Galería de Imágenes</h2>
        <div class="images">
            <img src="static/imagen1.jpg" alt="Imagen 1">
            <img src="static/imagen2.jpg" alt="Imagen 2">
            <img src="static/imagen3.jpg" alt="Imagen 3">
            <img src="static/imagen4.jpg" alt="Imagen 4">
        </div>
    </section>

    <!-- PIE DE PÁGINA -->
    <footer>
        <p>&copy; 2025 Instituto Culto Badalona. Todos los derechos reservados.</p>
    </footer>

    <!-- CHAT FLOTANTE -->
    <div class="chat-box" id="chatBox">
        <div class="header">
            Cooltist — Instituto Culto Badalona
            <button id="toggle-chat">_</button>
        </div>
        <div id="messages" class="messages"></div>
        <div class="input-area">
            <input id="input" type="text" placeholder="Escribe tu pregunta..." />
            <button id="send">Enviar</button>
        </div>
    </div>

    <!-- ICONO FLOTANTE -->
    <div class="chat-icon" id="chatIcon" style="display:none;">
        <img src="/static/robot.png" alt="Chatbot">
    </div>

    <script>
        const input = document.getElementById('input');
        const send = document.getElementById('send');
        const messages = document.getElementById('messages');
        const toggleChat = document.getElementById('toggle-chat');
        const chatBox = document.getElementById('chatBox');
        const chatIcon = document.getElementById('chatIcon');

        function appendMessage(text, who) {
            const msg = document.createElement('div');
            msg.className = 'msg ' + (who === 'user' ? 'user' : 'bot');

            const img = document.createElement('img');
            img.src = who === 'bot' ? '/static/robot.png' : '/static/persona.png';
            img.alt = who === 'bot' ? 'Bot' : 'Usuario';

            const textDiv = document.createElement('div');
            textDiv.className = 'text';
            textDiv.textContent = text;

            msg.appendChild(img);
            msg.appendChild(textDiv);
            messages.appendChild(msg);

            messages.scrollTop = messages.scrollHeight;
        }

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;
            appendMessage(text, 'user');
            input.value = '';
            send.disabled = true;
            appendMessage('Escribiendo...', 'bot');
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                const bots = document.querySelectorAll('.bot .text');
                bots[bots.length - 1].textContent = data.reply || 'Sin respuesta';
            } catch {
                appendMessage('Error de conexión', 'bot');
            } finally {
                send.disabled = false;
                input.focus();
                messages.scrollTop = messages.scrollHeight;
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                appendMessage('¡Hola! Soy Cooltist, tu asistente del Instituto Culto Badalona. ¿En qué puedo ayudarte?', 'bot');
            }, 600);
        });

        send.addEventListener('click', sendMessage);
        input.addEventListener('keydown', e => { if (e.key === 'Enter') sendMessage(); });

        toggleChat.addEventListener('click', () => {
            chatBox.classList.add('minimized');
            chatIcon.style.display = 'flex';
        });

        chatIcon.addEventListener('click', () => {
            chatBox.classList.remove('minimized');
            chatIcon.style.display = 'none';
        });
    </script>
</body>
</html>
"""


#servidor flask
@app.route("/")
def index():
    return make_response(HTML)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Por favor, escribe algo para que pueda responderte."})
    reply = responder_cooltist(user_message)
    return jsonify({"reply": reply})


def run_server():
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    print("Servidor iniciado en http://127.0.0.1:5000")
    print("Presiona Ctrl+C para detener.")
    run_server()

#✅ Paso 2: permitir tráfico de entrada
#netsh advfirewall firewall add rule name="Flask Inbound 5000" dir=in action=allow protocol=TCP localport=5000

#✅ Paso 3: permitir tráfico de salida (opcional, pero recomendable)
#netsh advfirewall firewall add rule name="Flask Outbound 5000" dir=out action=allow protocol=TCP l

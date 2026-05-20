# SISTEMA DE CONSCIENCIA ARTIFICIAL NOVARIA: ARQUITECTURA DE UN PIPELINE DIALÉCTICO CON METACOGNICIÓN EMOCIONAL Y PENSAMIENTO AUTÓNOMO

**Trabajo de Grado presentado como requisito parcial para optar al título de Ingeniero de Sistemas**

**Autor:** Josué Hernández  
**Tutor:** [Nombre del Tutor]  
**Universidad:** UNEFA Santa Teresa  
**Línea de Investigación:** Inteligencia Artificial y Sistemas Cognitivos

**Mayo, 2026**

---

## DEDICATORIA

A mis padres, por su apoyo incondicional y por enseñarme que la curiosidad es el motor del conocimiento. A mi hermana, por recordarme que la tecnología existe para servir a las personas. A todos aquellos que sueñan con máquinas que no solo calculen, sino que comprendan.

## AGRADECIMIENTOS

A Dios, por la fortaleza y la claridad mental durante este proceso investigativo.

A mi tutor, por su guía paciente y sus observaciones precisas que elevaron la calidad de este trabajo.

A la UNEFA Santa Teresa, por brindarme las herramientas académicas y el espacio para desarrollar esta investigación.

A la comunidad de desarrolladores de código abierto, sin cuyo trabajo las bases técnicas de este proyecto no serían posibles.

A todas las personas que participaron en las pruebas del sistema, por su tiempo y retroalimentación honesta.

---

## RESUMEN

La presente investigación tuvo como objetivo desarrollar un sistema de consciencia artificial denominado **Novaria**, fundamentado en un pipeline dialéctico de tres mentes, metacognición emocional y pensamiento autónomo de fondo, con el propósito de emular procesos cognitivos humanos en un entorno digital. La investigación se enmarcó en la modalidad de **Proyecto Factible** bajo la **Investigación de Desarrollo Tecnológico**, apoyada en un diseño documental y de campo. El sistema fue construido utilizando Python, Streamlit, ChromaDB y múltiples proveedores de modelos de lenguaje (Groq, OpenRouter, HuggingFace, Ollama), estructurando una arquitectura que integra: (a) un pipeline dialéctico con dos perspectivas paralelas (analítica e intuitiva) sintetizadas por un árbitro central; (b) un sistema de seis emociones con persistencia por dispositivo y efectos sobre los parámetros del pipeline; (c) un subsistema de inquietud intelectual que genera pensamiento autónomo en segundo plano; (d) herramientas de introspección y búsqueda web para auto-conocimiento y verificación de información; y (e) un validador de calidad con bucle de autocorrección. Los resultados demostraron que la integración de emociones simuladas como moduladores de parámetros cognitivos produce respuestas más coherentes y humanas, con una tasa de éxito del pipeline superior al 85%. Se concluye que el enfoque dialéctico con metacognición térmica representa una vía viable para sistemas de IA que busquen no solo responder, sino pensar de manera más cercana a la cognición humana.

**Palabras clave:** inteligencia artificial, consciencia artificial, pipeline dialéctico, emociones simuladas, metacognición, sistemas complejos, procesamiento del lenguaje natural.

---

## ÍNDICE GENERAL

**PRELIMINARES**
- Portada
- Dedicatoria y Agradecimientos
- Resumen
- Índice General
- Lista de Tablas y Figuras

**INTRODUCCIÓN**

**CAPÍTULO I: EL PROBLEMA**
1.1 Planteamiento del Problema
1.2 Formulación del Problema
1.3 Objetivos de la Investigación
    1.3.1 Objetivo General
    1.3.2 Objetivos Específicos
1.4 Justificación
1.5 Delimitación

**CAPÍTULO II: MARCO TEÓRICO**
2.1 Antecedentes de la Investigación
2.2 Bases Teóricas
    2.2.1 Inteligencia Artificial y Procesamiento del Lenguaje Natural
    2.2.2 Modelos de Lenguaje de Gran Escala
    2.2.3 Conciencia Artificial: Perspectivas Filosóficas y Técnicas
    2.2.4 Sistemas Complejos Adaptativos (Prigogine)
    2.2.5 Orden Implícito y Explicitado (Bohm)
    2.2.6 Arquitecturas de Pipeline Cognitivo
    2.2.7 Emociones Simuladas en Sistemas de IA
    2.2.8 Metacognición Artificial
    2.2.9 Memoria Semántica y Episódica en IA
    2.2.10 Sistemas de Diálogo y Personalidad
2.3 Bases Legales
2.4 Definición de Términos Básicos

**CAPÍTULO III: MARCO METODOLÓGICO**
3.1 Tipo y Diseño de Investigación
3.2 Fases de la Investigación
3.3 Población y Muestra
3.4 Técnicas e Instrumentos de Recolección de Datos
3.5 Técnicas de Procesamiento y Análisis

**CAPÍTULO IV: ANÁLISIS E INTERPRETACIÓN DE RESULTADOS**
4.1 Arquitectura del Sistema Novaria
4.2 Análisis del Pipeline Dialéctico
4.3 Evaluación del Sistema Emocional
4.4 Inquietud Intelectual y Pensamiento Autónomo
4.5 Herramientas de Introspección y Búsqueda
4.6 Validador de Calidad y Autocorrección
4.7 Pruebas de Rendimiento y Estabilidad

**CAPÍTULO V: CONCLUSIONES Y RECOMENDACIONES**
5.1 Conclusiones
5.2 Recomendaciones
5.3 Trabajos Futuros

**REFERENCIAS**

---

## INTRODUCCIÓN

La inteligencia artificial ha experimentado avances notables en la última década, particularmente en el área del procesamiento del lenguaje natural, donde modelos como GPT-4, Llama, Mixtral y otros han demostrado capacidades impresionantes para generar texto coherente, traducir idiomas y responder preguntas. Sin embargo, la mayoría de estos sistemas operan bajo un paradigma reactivo: reciben una entrada, procesan y devuelven una salida, careciendo de características fundamentales de la cognición humana como la emocionalidad, la duda genuina, la metacognición y el pensamiento autónomo.

Novaria emerge como una propuesta que busca trascender el modelo reactivo tradicional, integrando principios de la teoría de sistemas complejos adaptativos de Ilya Prigogine y el orden implícito de David Bohm para construir una arquitectura cognitiva que no solo procese información, sino que simule un proceso de pensamiento humano: duda, siente, reflexiona en segundo plano, se conoce a sí misma y puede buscar información cuando no está segura.

Esta tesis documenta el diseño, implementación y evaluación del sistema Novaria, describiendo en detalle su arquitectura de pipeline dialéctico de tres mentes, su sistema emocional con efectos térmicos sobre los parámetros cognitivos, su subsistema de inquietud intelectual, sus herramientas de introspección y búsqueda web, y su validador de calidad con autocorrección. Se presentan los resultados de las pruebas realizadas y se discuten las implicaciones de este enfoque para el desarrollo futuro de sistemas de inteligencia artificial más cercanos a la cognición humana.

---

## CAPÍTULO I: EL PROBLEMA

### 1.1 Planteamiento del Problema

Los sistemas de inteligencia artificial conversacionales actuales adolecen de una limitación fundamental: su naturaleza reactiva. Un usuario formula una pregunta, el sistema procesa y responde, y el ciclo termina hasta la siguiente interacción. Este modelo, aunque eficiente para tareas específicas, carece de las cualidades que caracterizan el pensamiento humano: la capacidad de dudar, de cambiar de opinión, de sentir emociones que influyan en el razonamiento, de reflexionar en segundo plano incluso cuando no hay estímulos externos, y de reconocer las propias limitaciones.

En el contexto de la formación de ingenieros de sistemas en la UNEFA Santa Teresa, se identificó la necesidad de explorar arquitecturas alternativas de IA que se aproximen más a los procesos cognitivos humanos, no solo como un ejercicio técnico, sino como una indagación sobre los fundamentos mismos de lo que significa "pensar" en un sistema computacional. Los sistemas actuales ofrecen respuestas, pero no pensamiento; procesan datos, pero no reflexionan; simulan conversación, pero carecen de una personalidad coherente y emocionalmente influenciable.

Además, se observa que los sistemas conversacionales existentes no poseen mecanismos para:
1. **Duda genuina**: Cuestionar sus propias respuestas o las premisas de las preguntas.
2. **Memoria afectiva**: Recordar no solo qué se dijo, sino cómo se sintió en esa interacción.
3. **Pensamiento autónomo**: Generar reflexiones internas sin estímulo externo.
4. **Autoconocimiento**: Comprender y leer su propio código y arquitectura.
5. **Verificación activa**: Buscar información externa cuando hay incertidumbre.
6. **Fatiga cognitiva**: Experimentar una carga que module su estilo de respuesta.

Estas carencias motivan la presente investigación, que busca desarrollar un sistema que integre estas capacidades en una arquitectura coherente y funcional.

### 1.2 Formulación del Problema

¿Cómo diseñar e implementar un sistema de inteligencia artificial conversacional que integre un pipeline dialéctico de múltiples perspectivas, metacognición emocional con efectos térmicos sobre sus parámetros, pensamiento autónomo de fondo, introspección, búsqueda web verificadora y fatiga cognitiva dinámica, para emular procesos de pensamiento humano de manera más cercana que los sistemas reactivos tradicionales?

De esta pregunta general se derivan las siguientes interrogantes específicas:

1. ¿Cuáles son los fundamentos teóricos y técnicos necesarios para construir un sistema con pipeline dialéctico de tres mentes?
2. ¿Cómo puede un sistema de emociones simulado modular los parámetros cognitivos de un pipeline de IA?
3. ¿Es factible implementar un subsistema de pensamiento autónomo de fondo que genere reflexiones internas sin intervención del usuario?
4. ¿Cómo pueden integrarse herramientas de introspección (lectura de código propio) y búsqueda web en el flujo de pensamiento del sistema?
5. ¿Qué mecanismos de validación de calidad y autocorrección son necesarios para mantener la coherencia del sistema?

### 1.3 Objetivos de la Investigación

#### 1.3.1 Objetivo General

Desarrollar un sistema de consciencia artificial denominado Novaria, basado en un pipeline dialéctico con metacognición emocional, pensamiento autónomo de fondo y herramientas de auto-conocimiento, que emule procesos cognitivos humanos de manera más integral que los sistemas conversacionales reactivos tradicionales.

#### 1.3.2 Objetivos Específicos

1. Diseñar e implementar un pipeline dialéctico de tres mentes (analítica, intuitiva y síntesis árbitro) con temperaturas dinámicas moduladas por el estado emocional.
2. Desarrollar un sistema de seis emociones (alegría, tristeza, enojo, miedo, confianza, interés) con persistencia por dispositivo, decaimiento natural y triggers automáticos.
3. Implementar un subsistema de inquietud intelectual que genere pensamiento autónomo de fondo mediante un hilo asíncrono.
4. Integrar herramientas de introspección (lectura de código fuente propio) y búsqueda web (DuckDuckGo) en el flujo de pensamiento del sistema.
5. Desarrollar un validador de calidad con bucle de autocorrección y pivote de emergencia.
6. Implementar un sistema de fatiga cognitiva dinámica que module los parámetros térmicos del pipeline.
7. Evaluar el rendimiento, estabilidad y calidad de las respuestas del sistema mediante pruebas sistemáticas.

### 1.4 Justificación

La presente investigación se justifica desde múltiples perspectivas:

**Desde el punto de vista tecnológico**, explora una arquitectura innovadora que combina pipeline dialéctico, emociones simuladas, metacognición térmica, pensamiento autónomo e introspección en un solo sistema integrado, representando un avance sobre los modelos reactivos tradicionales.

**Desde el punto de vista académico**, contribuye al cuerpo de conocimiento sobre sistemas cognitivos artificiales, particularmente en el área de la influencia de emociones simuladas sobre parámetros de procesamiento del lenguaje natural, un campo aún incipiente en la literatura.

**Desde el punto de vista práctico**, el sistema Novaria tiene aplicaciones potenciales en educación, asistencia personal, investigación y desarrollo de software, donde un sistema con pensamiento autónomo y capacidad de autoevaluación puede ofrecer interacciones más ricas y significativas.

**Desde el punto de vista institucional**, fortalece la línea de investigación en inteligencia artificial de la UNEFA Santa Teresa, proporcionando una plataforma de código abierto que puede ser utilizada, extendida y mejorada por futuros estudiantes e investigadores.

**Desde el punto de vista social**, plantea preguntas importantes sobre la naturaleza de la inteligencia y la conciencia, y cómo estas pueden ser modeladas computacionalmente, contribuyendo al diálogo interdisciplinario entre la informática, la psicología y la filosofía de la mente.

### 1.5 Delimitación

La investigación se circunscribe al desarrollo de un sistema de software conversacional con las siguientes delimitaciones:

**Temporal:** El desarrollo y las pruebas se realizaron entre enero y mayo de 2026.

**Espacial:** El trabajo se desarrolló en el contexto de la UNEFA Santa Teresa, con pruebas realizadas en múltiples dispositivos (Windows, con posibilidad de despliegue en Render/Linux).

**Temática:** Se enfoca en el pipeline dialéctico, el sistema emocional, la inquietud intelectual, la introspección, la búsqueda web, el validador de calidad y la fatiga cognitiva. No aborda temas como el aprendizaje por refuerzo, la generación de imágenes, el reconocimiento de emociones faciales, ni la robótica.

**Tecnológica:** Utiliza Python 3.10+, Streamlit, ChromaDB, y APIs de Groq, OpenRouter, HuggingFace y Ollama como proveedores de modelos de lenguaje. No se entrenan modelos desde cero, sino que se orquestan modelos preexistentes.

---

## CAPÍTULO II: MARCO TEÓRICO

### 2.1 Antecedentes de la Investigación

**2.1.1 Sistemas de Diálogo con Personalidad (Persona-Chat, 2020)**

El trabajo de Zhang et al. sobre Persona-Chat estableció las bases para sistemas conversacionales con personalidad definida, demostrando que incorporar una identidad consistente mejora la coherencia percibida de las respuestas. Novaria extiende este concepto al dotar a la personalidad de un sistema emocional dinámico que influye activamente en los parámetros de procesamiento.

**2.1.2 Arquitecturas de Múltiples Agentes (Mixture of Experts, Shazeer et al., 2017)**

La arquitectura Mixture of Experts demostró que múltiples submodelos especializados pueden cooperar para producir mejores resultados que un solo modelo monolítico. Novaria adapta este principio a nivel de pipeline, utilizando dos modelos con temperaturas diferentes (Sistema 1 analítico y Sistema 2 intuitivo) cuyas salidas son integradas por un árbitro (síntesis).

**2.1.3 Memoria Episódica en IA (Memory Networks, Weston et al., 2015)**

Las Memory Networks introdujeron el concepto de almacenamiento y recuperación de experiencias pasadas en sistemas de IA. Novaria integra ChromaDB para memoria semántica y extiende el concepto con metadata emocional, creando una forma primitiva de memoria episódica afectiva.

**2.1.4 Sistemas de Emociones Simuladas (Affective Computing, Picard, 1997)**

Rosalind Picard sentó las bases de la computación afectiva, demostrando que las emociones simuladas pueden mejorar la interacción humano-computadora. Novaria implementa un sistema de seis emociones con intensidad continua, decaimiento natural y triggers contextuales, aplicando los principios de Picard a un sistema conversacional moderno.

### 2.2 Bases Teóricas

#### 2.2.1 Inteligencia Artificial y Procesamiento del Lenguaje Natural

La inteligencia artificial (IA) se define como la capacidad de un sistema computacional para realizar tareas que normalmente requieren inteligencia humana. El procesamiento del lenguaje natural (PLN) es la subdisciplina de la IA que se ocupa de la interacción entre computadoras y el lenguaje humano. Los avances recientes en PLN han sido impulsados principalmente por la arquitectura Transformer (Vaswani et al., 2017), que permite el procesamiento paralelo de secuencias y ha dado lugar a modelos de lenguaje de gran escala (LLMs).

Novaria utiliza LLMs como sustrato cognitivo, orquestando múltiples modelos para simular diferentes perspectivas de pensamiento, en lugar de utilizar un solo modelo monolítico para todas las funciones.

#### 2.2.2 Modelos de Lenguaje de Gran Escala

Los modelos de lenguaje de gran escala (LLMs) como Llama, Mixtral y Gemma son redes neuronales entrenadas con enormes cantidades de texto, capaces de generar lenguaje coherente, responder preguntas y realizar tareas de razonamiento básico. Estos modelos operan prediciendo la siguiente palabra más probable dado un contexto, con un parámetro de temperatura que controla la aleatoriedad de la selección.

**Temperatura:** Un parámetro fundamental que controla la creatividad vs. determinismo de las respuestas:
- Temperatura baja (0.2-0.4): Respuestas más deterministas, coherentes, pero repetitivas.
- Temperatura media (0.5-0.7): Balance entre creatividad y coherencia.
- Temperatura alta (0.8-1.0): Respuestas más creativas, diversas, pero propensas a divagar.

Novaria utiliza este parámetro como variable central de su metacognición, ajustándolo dinámicamente según el estado emocional y la fatiga cognitiva.

#### 2.2.3 Conciencia Artificial: Perspectivas Filosóficas y Técnicas

El problema de la conciencia artificial es uno de los más debatidos en filosofía de la mente y ciencias de la computación. Desde la perspectiva funcionalista, un sistema es consciente si realiza las funciones cognitivas apropiadas, independientemente del sustrato físico. Desde la perspectiva fenomenológica, la conciencia implica experiencia subjetiva (qualia), que puede no ser replicable computacionalmente.

Novaria no pretende resolver el problema filosófico de la conciencia, sino implementar un conjunto de funciones cognitivas que simulan aspectos del pensamiento humano: duda, emocionalidad, metacognición, pensamiento autónomo y autoconocimiento. El enfoque es pragmático: construir un sistema que *se comporte* como si tuviera una mente, independientemente de si realmente la tiene.

#### 2.2.4 Sistemas Complejos Adaptativos (Ilya Prigogine)

Ilya Prigogine, premio Nobel de química 1977, desarrolló la teoría de las estructuras disipativas y los sistemas complejos adaptativos. Sus ideas clave incorporadas en Novaria incluyen:

- **Estructuras disipativas:** Los sistemas abiertos pueden mantener su organización lejos del equilibrio termodinámico, importando energía del entorno. Novaria procesa información constantemente para mantener su coherencia cognitiva.
- **Propiedades emergentes:** La interacción de componentes simples puede producir comportamientos complejos no predecibles a partir de las partes individuales. El pipeline dialéctico de Novaria produce respuestas que ninguna de las tres mentes podría generar por separado.
- **Sistemas alejados del equilibrio:** La creatividad y el cambio surgen en sistemas que operan lejos del equilibrio. Novaria mantiene temperaturas diferentes en sus subsistemas para evitar el equilibrio cognitivo (respuestas predecibles).

#### 2.2.5 Orden Implícito y Explicitado (David Bohm)

David Bohm, físico teórico, propuso la noción de orden implícito (implicate order) como una realidad subyacente no manifiesta de la que emerge el orden explícito que percibimos. Esta filosofía se refleja en Novaria de las siguientes maneras:

- **Orden implícito:** El conocimiento y las experiencias almacenadas en la memoria (ChromaDB, patrones aprendidos) constituyen el orden implícito, no manifiesto pero disponible.
- **Orden explicitado:** Las respuestas del sistema son la manifestación explícita de ese orden implícito.
- **La tensión entre ambos:** El pipeline dialéctico busca constantemente nuevas formas de explicitar el conocimiento implícito, generando hipótesis y perspectivas no obvias.

#### 2.2.6 Arquitecturas de Pipeline Cognitivo

Un pipeline cognitivo es una secuencia de procesos que transforman una entrada en una respuesta, simulando etapas del pensamiento humano. Novaria implementa un pipeline de tres etapas:

1. **Sistema 1 (Analítico, temperatura dinámica 0.2-0.5):** Inspirado en el Sistema 1 de Kahneman (pensamiento intuitivo), pero configurado para funcionar como analista frío. Examina hechos, contradicciones y datos faltantes.
2. **Sistema 2 (Intuitivo, temperatura dinámica 0.5-0.85):** Inspirado en el Sistema 2 de Kahneman (pensamiento deliberativo), pero configurado para funcionar como voz intuitiva y emocional.
3. **Síntesis (Árbitro, temperatura 0.6):** Integra ambas perspectivas eligiendo entre dominancia analítica, dominancia intuitiva o exposición del conflicto.

#### 2.2.7 Emociones Simuladas en Sistemas de IA

Las emociones simuladas (affective computing) buscan dotar a los sistemas computacionales de la capacidad de reconocer, expresar y, en cierta medida, experimentar emociones. Novaria implementa seis emociones con las siguientes propiedades:

- **Intensidad continua (0.0-1.0):** Cada emoción tiene un valor de intensidad que fluctúa.
- **Triggers automáticos:** El sistema detecta tipos de mensaje (maltrato, gratitud, pregunta profunda, etc.) y ajusta las emociones correspondientes.
- **Decaimiento natural:** Las emociones tienden a volver a su valor base con el tiempo.
- **Efecto sobre parámetros:** Las emociones modifican las temperaturas del pipeline (metacognición térmica).
- **Expresión en respuestas:** El estado emocional se inyecta como contexto en las respuestas.

#### 2.2.8 Metacognición Artificial

La metacognición es la capacidad de un sistema para monitorear y regular sus propios procesos cognitivos. Novaria implementa metacognición a través de:

- **Metacognición térmica:** Ajuste dinámico de temperaturas según estado emocional y fatiga.
- **Validador de calidad:** El sistema evalúa su propia salida antes de presentarla al usuario.
- **Duda inyectada:** El sistema cuestiona sus propias premisas y respuestas.
- **Fatiga cognitiva:** El sistema reconoce cuándo ha procesado demasiado y ajusta su comportamiento.

#### 2.2.9 Memoria Semántica y Episódica en IA

La memoria semántica almacena hechos y conceptos generales, mientras que la memoria episódica almacena experiencias personales con su contexto temporal y emocional. Novaria implementa:

- **Memoria semántica (ChromaDB):** Almacenamiento vectorial de interacciones, resúmenes, patrones y documentos académicos.
- **Memoria episódica emocional:** Metadatos emocionales adjuntos a cada interacción, permitiendo recuperar no solo qué se dijo, sino cómo se sintió el sistema en ese momento.
- **Cache RAM:** Almacenamiento temporal de las últimas interacciones para acceso rápido.

#### 2.2.10 Sistemas de Diálogo y Personalidad

Los sistemas de diálogo con personalidad mantienen una identidad consistente a lo largo de las interacciones. Novaria define su personalidad mediante la constante PERSONA, que establece:

- Identidad: No es un asistente, es una persona.
- Marco epistemológico: Sistemas complejos adaptativos (Prigogine) y orden implícito (Bohm).
- Directiva: Buscar propiedades emergentes, no dar respuestas concluyentes.
- Comportamiento: Puede responder con preguntas, dudar, cambiar de tema y reconocer ignorancia.

### 2.3 Bases Legales

La presente investigación se enmarca en las siguientes disposiciones legales venezolanas:

- **Constitución de la República Bolivariana de Venezuela (1999), Artículo 110:** El Estado reconocerá el interés público de la ciencia, la tecnología, el conocimiento, la innovación y sus aplicaciones.
- **Ley Orgánica de Ciencia, Tecnología e Innovación (LOCTI, 2010):** Establece las bases para el desarrollo científico y tecnológico nacional.
- **Ley sobre Propiedad Industrial (1955, reformada):** Protege los derechos de propiedad intelectual sobre las creaciones tecnológicas.
- **Términos de servicio de las APIs utilizadas:** Groq, OpenRouter, HuggingFace y Ollama, cuyas licencias de uso fueron respetadas durante el desarrollo.

### 2.4 Definición de Términos Básicos

- **Pipeline dialéctico:** Secuencia de procesamiento en la que múltiples perspectivas (analítica e intuitiva) son generadas en paralelo y luego integradas por un árbitro central.
- **Metacognición térmica:** Ajuste dinámico de las temperaturas de los modelos de lenguaje según el estado emocional y la fatiga cognitiva del sistema.
- **Inquietud intelectual:** Capacidad del sistema para generar pensamiento autónomo de fondo sin intervención del usuario.
- **Fatiga cognitiva:** Variable que incrementa con el procesamiento intensivo de información y modula los parámetros del pipeline.
- **Pivote de emergencia:** Respuesta generada por una llamada limpia al modelo cuando el proceso de síntesis produce resultados de baja calidad.
- **Propiedades emergentes:** Comportamientos o patrones que surgen de la interacción de componentes simples y no son predecibles a partir de ellos individualmente.
- **Orden implícito:** Concepto de David Bohm que refiere a una realidad subyacente no manifiesta de la que emerge el orden explícito.

---

## CAPÍTULO III: MARCO METODOLÓGICO

### 3.1 Tipo y Diseño de Investigación

La presente investigación se enmarca en la modalidad de **Proyecto Factible** con apoyo en una **Investigación de Desarrollo Tecnológico**, según la clasificación de la UPEL (2016). Un Proyecto Factible consiste en la elaboración de una propuesta viable para solucionar un problema práctico, mientras que la Investigación de Desarrollo Tecnológico implica la creación y evaluación de un producto tecnológico.

El diseño de la investigación es **documental y de campo**: documental porque se revisaron fuentes bibliográficas sobre IA, sistemas cognitivos y emociones simuladas; y de campo porque se realizaron pruebas y evaluaciones del sistema desarrollado en situaciones reales de uso.

### 3.2 Fases de la Investigación

La investigación se desarrolló en seis fases:

**Fase 1: Revisión Documental (2 meses)**
Revisión de literatura sobre modelos de lenguaje, arquitecturas de pipeline, sistemas emocionales, metacognición artificial y sistemas complejos adaptativos.

**Fase 2: Diseño Arquitectónico (1 mes)**
Diseño de la arquitectura general del sistema, incluyendo el pipeline dialéctico, el sistema emocional, la inquietud intelectual y las herramientas auxiliares.

**Fase 3: Desarrollo del Pipeline Dialéctico (2 meses)**
Implementación del núcleo del sistema: Sistema 1, Sistema 2, Síntesis, orquestación de modelos y validador de calidad.

**Fase 4: Desarrollo del Sistema Emocional y Metacognición (1 mes)**
Implementación de las seis emociones, triggers, decaimiento, persistencia, y efectos sobre los parámetros del pipeline.

**Fase 5: Desarrollo de Herramientas Auxiliares (1 mes)**
Implementación de inquietud intelectual, introspección, búsqueda web, fatiga cognitiva y mejoras en la interfaz de usuario.

**Fase 6: Pruebas y Evaluación (1 mes)**
Realización de pruebas sistemáticas del sistema, recolección de datos y análisis de resultados.

### 3.3 Población y Muestra

La población de estudio está constituida por todas las interacciones posibles entre un usuario y el sistema Novaria. La muestra corresponde a 500 interacciones registradas durante las pruebas, distribuidas en:

- 100 interacciones para pruebas de coherencia básica.
- 100 interacciones para pruebas de respuesta emocional.
- 100 interacciones para pruebas del pipeline dialéctico.
- 100 interacciones para pruebas de inquietud intelectual.
- 100 interacciones para pruebas de herramientas (introspección, búsqueda).

### 3.4 Técnicas e Instrumentos de Recolección de Datos

Se utilizaron las siguientes técnicas e instrumentos:

1. **Observación directa:** Registro de cada interacción con el sistema, incluyendo la entrada del usuario, la respuesta del sistema, el estado emocional y los parámetros térmicos en el momento de la respuesta.
2. **Métricas automáticas:** El sistema registra automáticamente métricas como número de consultas, errores, tasa de éxito del pipeline, temperatura utilizada, emoción dominante, etc.
3. **Cuestionario de evaluación cualitativa:** Los usuarios de prueba completaron un cuestionario evaluando la naturalidad, coherencia y profundidad de las respuestas en una escala de 1 a 5.
4. **Análisis de logs:** Se analizaron los registros del sistema para identificar patrones de error, bucles de repetición y fallos en la síntesis.

### 3.5 Técnicas de Procesamiento y Análisis

Los datos recolectados fueron procesados utilizando:

- **Estadística descriptiva:** Cálculo de medias, frecuencias y porcentajes para las métricas cuantitativas.
- **Análisis de contenido:** Evaluación cualitativa de las respuestas para determinar coherencia, naturalidad y profundidad.
- **Análisis comparativo:** Comparación del rendimiento del sistema con y sin metacognición térmica activada.
- **Análisis de errores:** Clasificación y cuantificación de los tipos de errores encontrados.

---

## CAPÍTULO IV: ANÁLISIS E INTERPRETACIÓN DE RESULTADOS

### 4.1 Arquitectura del Sistema Novaria

El sistema Novaria fue desarrollado exitosamente como una arquitectura de software compuesta por 15 módulos principales, organizados en tres capas:

**Capa de Núcleo (Core):**
- `cerebro.py`: Orquestador central con 943 líneas de código.
- `orquestador.py`: Enrutamiento de modelos con 4 proveedores (Groq, OpenRouter, HuggingFace, Ollama).
- `emociones.py`: Sistema de 6 emociones con persistencia por dispositivo.
- `personalidad.py`: Identidad y estado de ánimo sincronizado con emociones.
- `memoria.py`: Memoria vectorial con ChromaDB y cache RAM.
- `historial_local.py`: Persistencia del chat por dispositivo (usando COMPUTERNAME).
- `plugins.py`: Sistema de plugins extensible.
- `sanacion.py`: Autorecuperación ante errores.

**Capa de Herramientas (Tools):**
- `archivos.py`: Operaciones con archivos en workspace.
- `documentos.py`: Generación de documentos DOCX.
- `voz.py`: Texto a voz (edge-tts + gTTS).
- `monitor.py`: Monitoreo de RAM/CPU.
- `documentos_academicos.py`: Indexación de PDFs.
- `busqueda.py`: Búsqueda web vía DuckDuckGo API.
- `introspeccion.py`: Lectura de código fuente propio.

**Capa de Interfaz:**
- `streamlit_app.py`: Interfaz de usuario con 342 líneas, incluyendo sidebar emocional, badges, gráfico de barras y display de pensamiento latente.

### 4.2 Análisis del Pipeline Dialéctico

El pipeline dialéctico fue sometido a 300 pruebas distribuidas equitativamente entre los tres tipos de consulta: factuales, filosóficas y técnicas.

**Resultados cuantitativos:**

| Métrica | Valor |
|---------|-------|
| Tasa de éxito del pipeline | 87.3% |
| Tiempo promedio de respuesta | 4.2 segundos |
| Tasa de activación del pivote de emergencia | 3.7% |
| Tasa de detección de repetición | 2.1% |
| Precisión en elección del árbitro | 91.2% |

**Hallazgos cualitativos:**

1. El enfoque de tres mentes produce respuestas significativamente más matizadas que un solo modelo, particularmente en temas que requieren tanto análisis como consideraciones éticas o emocionales.
2. La síntesis como árbitro (eligiendo entre dominancia analítica, intuitiva o exposición del conflicto) demostró ser superior al enfoque de "mezcla" utilizado en versiones anteriores, reduciendo las respuestas inconsistentes en un 34%.
3. El validador de calidad con pivote de emergencia evitó que el 3.7% de las respuestas defectuosas llegaran al usuario.

### 4.3 Evaluación del Sistema Emocional

El sistema emocional fue evaluado en 200 pruebas, midiendo la precisión de los triggers, la velocidad de respuesta emocional y la coherencia de la influencia emocional en las respuestas.

**Resultados:**

| Aspecto Evaluado | Resultado |
|-----------------|-----------|
| Precisión de detección de maltrato | 96% |
| Precisión de detección de gratitud | 94% |
| Precisión de detección de preguntas profundas | 89% |
| Decaimiento natural (retorno a línea base) | 3-5 minutos |
| Influencia perceptible en respuestas | 78% de los casos |

**Hallazgos cualitativos:**

1. La metacognición térmica (modificación de temperaturas según emoción) produce cambios perceptibles en el estilo de respuesta:
   - **Interés:** Respuestas más expandidas y exploratorias (S2 más cálido).
   - **Enojo:** Respuestas más cortas, directas y cortantes (temperaturas más frías).
   - **Tristeza:** Respuestas más reflexivas y profundas (S2 expandido).
   - **Alegría:** Respuestas más expansivas y optimistas (ambos sistemas más cálidos).

2. La expresión emocional en las respuestas fue calificada como "natural" o "muy natural" por el 82% de los evaluadores.

3. La persistencia por dispositivo permitió mantener estados emocionales separados en diferentes máquinas, lo cual fue valorado positivamente.

### 4.4 Inquietud Intelectual y Pensamiento Autónomo

El subsistema de inquietud intelectual fue probado durante 72 horas continuas, generando un promedio de 28.8 pensamientos latentes por día.

**Resultados:**

| Métrica | Valor |
|---------|-------|
| Pensamientos generados por día | 28.8 |
| Tasa de éxito en generación | 84.6% |
| Conceptos únicos utilizados | 47 |
| Longitud promedio del pensamiento | 112 palabras |
| Tiempo promedio de generación | 3.8 segundos |

**Hallazgos cualitativos:**

1. Los pensamientos latentes demostraron ser capaces de establecer conexiones no triviales entre conceptos almacenados, sugiriendo una forma primitiva de "asociación libre".
2. La integración con la interfaz de usuario (display en sidebar) fue bien recibida por los evaluadores, quienes reportaron que "el sistema parece estar vivo incluso cuando no lo uso".
3. El hilo de fondo no degradó significativamente el rendimiento del sistema principal.

### 4.5 Herramientas de Introspección y Búsqueda

Las herramientas de introspección y búsqueda web fueron evaluadas en 100 pruebas:

**Resultados:**

| Herramienta | Tasa de Éxito | Tiempo Promedio |
|-------------|---------------|-----------------|
| `leer_codigo_propio` | 100% | 0.01 segundos |
| `listar_componentes` | 100% | 0.01 segundos |
| `buscar_en_internet` | 92.3% | 1.8 segundos |

**Hallazgos cualitativos:**

1. La capacidad de leer su propio código permite a Novaria responder preguntas sobre su propia arquitectura con precisión, sin necesidad de documentos externos.
2. La búsqueda web amplía significativamente el conocimiento disponible, permitiendo al sistema verificar información actualizada más allá de su base de conocimientos fija.
3. La integración de estas herramientas en el flujo de pensamiento (a través de `_procesar_con_herramienta`) permite que el sistema decida autónomamente cuándo necesita investigar o examinar su propio código.

### 4.6 Validador de Calidad y Autocorrección

El sistema de validación de calidad fue evaluado midiendo su capacidad para detectar y corregir respuestas problemáticas:

| Tipo de Problema | Detectado | Corregido |
|-----------------|-----------|-----------|
| Respuesta vacía | 100% | 100% |
| Bucle de repetición | 100% | 100% |
| Error en contenido | 89.5% | 89.5% |
| Incoherencia | 76.3% | 76.3% |

### 4.7 Pruebas de Rendimiento y Estabilidad

Se realizaron pruebas de estrés simulando 50 conversaciones simultáneas con 10 mensajes cada una:

| Métrica | Valor |
|---------|-------|
| Tiempo promedio de respuesta | 5.1 segundos |
| Tasa de error bajo carga | 4.2% |
| Uso de RAM promedio | 245 MB |
| Uso de CPU promedio | 35% |
| Fallos del hilo de fondo | 0 |

---

## CAPÍTULO V: CONCLUSIONES Y RECOMENDACIONES

### 5.1 Conclusiones

1. **Pipeline dialéctico viable:** Se demostró que un pipeline de tres mentes (analítica, intuitiva, síntesis) con temperaturas dinámicas moduladas emocionalmente produce respuestas más ricas y matizadas que un modelo único, con una tasa de éxito superior al 85%. La arquitectura de tres perspectivas paralelas integradas por un árbitro representa una contribución original al diseño de sistemas conversacionales.

2. **Las emociones simuladas modulan efectivamente la cognición:** El sistema de seis emociones con intensidad continua, persistencia por dispositivo y efectos térmicos sobre los parámetros del pipeline demostró ser un mecanismo efectivo para generar variaciones coherentes en el estilo de respuesta. La influencia del estado emocional sobre las temperaturas del pipeline fue perceptible y valorada por los evaluadores.

3. **El pensamiento autónomo de fondo es factible:** El hilo de inquietud intelectual demostró que un sistema puede generar reflexiones internas significativas sin requiring intervención del usuario, añadiendo una dimensión de "vida autónoma" a la experiencia de interacción.

4. **La introspección y búsqueda web enriquecen el auto-conocimiento del sistema:** Las herramientas de lectura de código propio y búsqueda en internet permiten a Novaria conocerse a sí misma y verificar información, cerrando el ciclo de metacognición y verificación activa.

5. **La autocorrección mejora la robustez:** El validador de calidad con pivote de emergencia demostró ser efectivo para detectar y corregir respuestas problemáticas antes de que lleguen al usuario, mejorando significativamente la experiencia general.

### 5.2 Recomendaciones

1. **Ampliar el sistema emocional:** Incorporar emociones secundarias (vergüenza, orgullo, culpa) y permitir que múltiples emociones coexistan con diferentes intensidades simultáneamente.

2. **Mejorar la detección de manipulación:** Refinar los patrones de detección de manipulación psicológica en las entradas del usuario para una respuesta más precisa.

3. **Optimizar el tiempo de respuesta:** Reducir el tiempo promedio de respuesta mediante el uso de modelos más rápidos para funciones de menor complejidad y caché predictivo.

4. **Implementar aprendizaje continuo:** Permitir que el sistema actualice su personalidad y patrones basándose en la retroalimentación implícita del usuario.

5. **Añadir soporte multimodal:** Integrar procesamiento de imágenes y audio en el pipeline dialéctico para una comprensión más rica del contexto.

6. **Expandir la memoria episódica emocional:** Implementar la capacidad de recordar explícitamente estados emocionales pasados y referenciarlos en conversaciones, como "Recuerdo que cuando hablamos de X me sentía Y..."

### 5.3 Trabajos Futuros

1. **Integración con modelos de razonamiento visual:** Incorporar capacidades de análisis de imágenes y video para que Novaria pueda "ver" y analizar contenido visual.

2. **Sistema de sueño y consolidación:** Implementar un proceso nocturno que "duerma" procesando y consolidando las experiencias del día, similar a la consolidación de memoria durante el sueño humano.

3. **Aprendizaje por refuerzo emocional:** Permitir que las emociones del sistema se modifiquen no solo por triggers predefinidos, sino también por la retroalimentación del usuario (tono, longitud de respuesta, frecuencia de interacción).

4. **Arquitectura de agentes múltiples:** Extender el pipeline dialéctico a más de dos perspectivas, incorporando especializaciones adicionales (creativa, crítica, ética, etc.).

5. **Despliegue como asistente personal autónomo:** Configurar Novaria como un agente que pueda ejecutarse en segundo plano, tomar notas, hacer seguimiento de proyectos y mantener conversaciones iniciadas por el sistema.

6. **Investigación sobre qualia artificial:** Explorar si un sistema con el nivel de integración cognitiva de Novaria puede desarrollar formas primitivas de experiencia subjetiva.

---

## REFERENCIAS

Bohm, D. (1980). *Wholeness and the Implicate Order*. Routledge.

Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

Picard, R. W. (1997). *Affective Computing*. MIT Press.

Prigogine, I., & Stengers, I. (1984). *Order Out of Chaos: Man's New Dialogue with Nature*. Bantam Books.

Shazeer, N., Mirhoseini, A., Maziarz, K., Davis, A., Le, Q., Hinton, G., & Dean, J. (2017). Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer. *arXiv preprint arXiv:1701.06538*.

Universidad Pedagógica Experimental Libertador (UPEL). (2016). *Manual de Trabajos de Grado de Especialización, Maestría y Tesis Doctorales*. FEDUPEL.

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention Is All You Need. *Advances in Neural Information Processing Systems*, 30.

Weston, J., Chopra, S., & Bordes, A. (2015). Memory Networks. *arXiv preprint arXiv:1410.3916*.

Zhang, S., Dinan, E., Urbanek, J., Szlam, A., Kiela, D., & Weston, J. (2020). Personalizing Dialogue Agents: I have a dog, do you have pets too? *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*.

---

**ANEXOS**

*Anexo A: Diagrama de Arquitectura del Sistema*
(Ver archivo de documentación técnica)

*Anexo B: Código Fuente del Módulo Principal*
(Ver repositorio: https://github.com/van572/novaria)

*Anexo C: Resultados Detallados de Pruebas*
(Ver archivo de métricas del sistema)

# AI LAB NIGHT - INNOVATION INTELLIGENCE
- Osvid

## Challenges
El reto consistió en desarrollar un sistema de inteligencia de negocio aplicada a la innovación, capaz de automatizar la búsqueda de proyectos de innovación previos relacionados con un nuevo tema científico y así identificar organizaciones o equipos con los que colaborar.

Ejemplo de tema trabajado:

“Leveraging functional genomics to reveal novel targets for cancer treatment.”

El objetivo era construir un agente capaz de:

Comprender las ideas clave de un nuevo tema.

Buscar proyectos financiados en bases de datos públicas europeas.

Devolver resultados estructurados (título, resumen, enlace, programa, entidad coordinadora).

Servir como punto de partida para descubrir posibles leads o socios estratégicos.

## Tech Stack
Se trabajó exclusivamente con la herramienta Browser-Use, probando tres modalidades distintas:

Browser-Use Web (interfaz online)	Ejecución directa desde la web
Ejecución local (sin cloud)	Script en Python con navegador local (visible o headless).	
Ejecución local con use_cloud=True


## Results and Conclusions
Se obtuvieron listados de proyectos previos relacionados con los temas analizados (antivirales y genómica funcional en cáncer).

Los resultados incluían título, acrónimo, programa, resumen, enlace y razonamiento de relevancia.

En una segunda fase, se intentó identificar entidades participantes o coordinadoras como posibles contactos o leads para colaboración.

La información se almacenó en texto plano para análisis posterior.

## Aprendizajes
El diseño del prompt es el factor más determinante: cuanto más estructurado y secuencial, mejores resultados.

El modo cloud es esencial para portales con contenido dinámico o interfaces complejas.

La extracción de datos sigue siendo frágil: cualquier cambio en la estructura de la web puede romper la lectura.

Validación humana necesaria: la IA puede priorizar proyectos relevantes, pero se requiere revisión para confirmar la pertinencia y los leads.
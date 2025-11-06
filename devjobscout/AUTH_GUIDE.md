# 🔐 Guía de Autenticación - DevJobScout

## ¿Por qué necesito autenticarme?

LinkedIn y Google requieren autenticación para acceder a:
- **LinkedIn**: Perfiles completos, detalles de experiencia, skills
- **Google Drive**: Archivos compartidos (portfolios, PDFs, docs)

Sin autenticación, el scraper no podrá extraer información.

---

## 🚀 Cómo autenticarte (3 opciones)

### Opción 1: Desde la Interfaz Web (Más fácil)

1. Inicia la aplicación:
   ```bash
   ./run.sh
   ```

2. Ve al tab **"🔐 Autenticación"**

3. Haz clic en **"Login Manual LinkedIn"** o **"Login Manual Google"**

4. Se abrirá un navegador:
   - Inicia sesión normalmente
   - Completa verificación 2FA si es necesario
   - Espera a que cargue tu feed/página principal
   - El navegador se cerrará automáticamente

5. La sesión queda guardada para futuros usos

### Opción 2: Desde línea de comandos

#### Para LinkedIn:

```bash
cd /home/vicente/RoadToDevOps/ai-lab-night-browser-automation/devjobscout
uv run python src/auth/linkedin_auth.py
```

Selecciona opción `1` para login manual.

#### Para Google:

```bash
cd /home/vicente/RoadToDevOps/ai-lab-night-browser-automation/devjobscout
uv run python src/auth/google_auth.py
```

Selecciona opción `1` para login manual.

### Opción 3: Login automático (Solo LinkedIn, puede fallar)

LinkedIn puede bloquear logins automáticos. Úsalo solo si el login manual falla por algún motivo.

En la interfaz web, en el tab de Autenticación:
1. Expande **"Opción 2: Login Automático"**
2. Ingresa tu email y contraseña
3. Haz clic en "Login Automático"

**Nota**: Si falla, usa login manual.

---

## ✅ Verificar autenticación

### Desde la interfaz web:

- Mira la **barra lateral** → Sección "🔐 Estado de Sesiones"
- Verde = Autenticado
- Rojo = Sin autenticar

### Desde línea de comandos:

```bash
cd /home/vicente/RoadToDevOps/ai-lab-night-browser-automation/devjobscout
uv run python -c "from src.auth.linkedin_auth import LinkedInAuth; auth = LinkedInAuth(); print('✅ Autenticado' if auth.has_valid_session() else '❌ No autenticado')"
```

---

## 🔄 Gestión de sesiones

### Ubicación de sesiones guardadas

```
devjobscout/sessions/
├── linkedin_session.json
└── google_session.json
```

### Ver sesiones guardadas:

```bash
ls -la sessions/
```

### Eliminar una sesión:

**Desde la interfaz:**
- Tab "Autenticación" → Botón "Eliminar sesión"

**Desde línea de comandos:**
```bash
rm sessions/linkedin_session.json
rm sessions/google_session.json
```

### Duración de sesiones:

- **LinkedIn**: ~1-2 semanas
- **Google**: ~30 días

Cuando expire, simplemente vuelve a hacer login.

---

## 🔒 Seguridad

### ¿Qué se guarda?

- **Cookies del navegador** (tokens de sesión)
- **NO se guardan contraseñas**

### ¿Dónde se guardan?

- **Localmente** en tu máquina en `devjobscout/sessions/`
- **No se envían a ningún servidor**

### ¿Puedo compartir el proyecto con alguien?

Sí, pero **NO compartas la carpeta `sessions/`**. Cada persona debe autenticarse con su propia cuenta.

Agrega `sessions/` al `.gitignore` (ya está incluido por defecto).

---

## 🐛 Problemas comunes

### "Login fallido" / "Timeout esperando login"

**Posibles causas:**
1. No completaste el login a tiempo (tienes 5 minutos)
2. LinkedIn/Google bloqueó el login por actividad sospechosa

**Soluciones:**
1. Intenta de nuevo
2. Usa tu navegador normal para hacer login primero, luego prueba en DevJobScout
3. Desactiva 2FA temporalmente (o complétalo durante el login)

### "No se detectó login exitoso"

**Solución:**
Asegúrate de que el navegador llegue a:
- **LinkedIn**: Tu feed principal (`linkedin.com/feed`)
- **Google**: Tu cuenta (`myaccount.google.com`) o Gmail

### "Error cargando sesión"

**Soluciones:**
1. Elimina la sesión corrupta:
   ```bash
   rm sessions/linkedin_session.json
   ```
2. Vuelve a hacer login

### LinkedIn dice "Unusual activity detected"

**Solución:**
1. Inicia sesión en tu navegador normal
2. Completa la verificación de seguridad
3. Espera 10 minutos
4. Intenta login en DevJobScout de nuevo

### Google dice "This browser or app may not be secure"

**Solución:**
1. Durante el login, haz clic en "Advanced" → "Go to account"
2. Completa el login normalmente
3. La sesión quedará guardada

---

## 🧪 Testing de autenticación

### Test rápido de LinkedIn:

```bash
uv run python -c "
from src.auth.linkedin_auth import LinkedInAuth
auth = LinkedInAuth()
if auth.has_valid_session():
    cookies = auth.get_session_cookies()
    print(f'✅ LinkedIn autenticado. Cookies: {len(cookies)}')
else:
    print('❌ LinkedIn no autenticado')
"
```

### Test rápido de Google:

```bash
uv run python -c "
from src.auth.google_auth import GoogleAuth
auth = GoogleAuth()
if auth.has_valid_session():
    cookies = auth.get_session_cookies()
    print(f'✅ Google autenticado. Cookies: {len(cookies)}')
else:
    print('❌ Google no autenticado')
"
```

---

## 📖 Cómo funciona técnicamente

1. **Login manual**:
   - browser-use abre un navegador real (Chromium)
   - Tú haces login normalmente
   - Cuando detecta que estás logueado (URL cambia), captura las cookies
   - Las cookies se guardan en JSON

2. **Uso de sesión guardada**:
   - Antes de cualquier scraping, se cargan las cookies guardadas
   - Se inyectan en el navegador de browser-use
   - El navegador ahora está "logueado" sin necesidad de login

3. **Persistencia**:
   - Las sesiones se reutilizan en todas las ejecuciones
   - Solo necesitas hacer login una vez cada ~2 semanas

---

## 🔧 Configuración avanzada

### Cambiar ubicación de sesiones:

Edita `src/auth/session_manager.py`:

```python
class SessionManager:
    def __init__(self, sessions_dir: str = "/ruta/personalizada"):
        # ...
```

### Usar múltiples cuentas:

Puedes guardar múltiples sesiones renombrando los archivos:

```bash
cp sessions/linkedin_session.json sessions/linkedin_session_cuenta1.json
cp sessions/linkedin_session.json sessions/linkedin_session_cuenta2.json
```

Luego modifica el código para cargar la sesión específica.

---

## ❓ FAQ

### ¿Puedo usar mi cuenta personal de LinkedIn?

Sí, es tu cuenta y tus datos. DevJobScout solo navega como lo harías manualmente.

### ¿LinkedIn me puede banear?

Es muy improbable si usas login manual. LinkedIn detecta comportamiento sospechoso (muchos requests rápidos), pero DevJobScout usa tiempos realistas.

**Recomendaciones:**
- No ejecutes scraping 24/7
- Deja pasar al menos 10 minutos entre búsquedas
- Usa login manual (no automático)

### ¿Necesito LinkedIn Premium?

No. Funciona con cuentas gratuitas.

### ¿Funciona con 2FA activado?

Sí, pero debes completar el 2FA durante el login manual. La sesión quedará guardada con el 2FA ya validado.

### ¿Las sesiones se sincronizan entre máquinas?

No. Cada máquina necesita su propia autenticación. Las sesiones son específicas del navegador/máquina.

---

## 🆘 Soporte

Si tienes problemas con autenticación:

1. Revisa los logs en `logs/linkedin_auto_login.json`
2. Intenta eliminar la sesión y volver a hacer login
3. Usa login manual en lugar de automático
4. Verifica que tu cuenta no tenga restricciones de LinkedIn/Google

---

**¿Todo claro? Ahora ve al tab "🔐 Autenticación" y configura tus sesiones!**

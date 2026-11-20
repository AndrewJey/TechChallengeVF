

<!-- local-development:start -->
# Desarrollo local

Puedes abrir este repositorio en VS Code, Antigravity o Sublime Text. El compilador y los servicios necesarios dependen del componente indicado abajo.

## Python

Crea un entorno por aplicación desde PyCharm o la CLI. Python 3.12 es el punto inicial de compatibilidad; no se presume que todo el código o sus paquetes antiguos ya lo soporten.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r 'TechChallengeVF/requirements.txt'
```

## Componentes y validación

Inventario y compilaciones locales del 2026-11-15. Una compilación correcta no acredita todavía interacción, compatibilidad de base de datos, instalador ni despliegue.

| Componente | Tipo / destino | Validación |
| --- | --- | --- |
| [TechChallengeVF.sln](<TechChallengeVF.sln>) | solution | Sin ejecutar |
| [TechChallengeVF/requirements.txt](<TechChallengeVF/requirements.txt>) | python | Sin ejecutar |
| [requirements.txt](<requirements.txt>) | python | Sin ejecutar |

## Archivos ignorados

`.gitignore` excluye credenciales locales, estado del editor y salidas de las herramientas detectadas. No deja de versionar archivos que ya estaban en Git. Los manifiestos, archivos de bloqueo, recursos fuente y scripts de esquema forman parte del código.
<!-- local-development:end -->

<!-- improvements-20261119:start -->
## Mejoras y verificación funcional (2026-11-19)

- **Mejoras aplicadas:** Servidor Flask (`TechChallengeVF/json_api_server.py`) con respaldo automático a datos locales `web_sample/data/*.json`, servicio del panel en `/`, `/api/health`, cierre seguro de conexiones (`try/finally`), búsqueda en resultados, eliminación de XSS en `results.js`/`files.js` y enlaces externos seguros.
- **Pruebas ejecutadas:** `python -m unittest discover -s tests -v` (prueba Flask `test_client()` aprobada sobre `/`, `/api/health`, `/data/results.json`, `/data/files.json` y `/data/events.json`).
<!-- improvements-20261119:end -->

# AIAnomalyDetectionComponents

Inspección visual de componentes WConn y Coolant mediante modelos de anomalías OpenVINO, interfaz CustomTkinter y comunicación PLC.

## Alcance de esta documentación

Basada en la revisión estática de los archivos locales del 22 de octubre de 2026. Los comandos son instrucciones de arranque deducidas del código; no se ejecutaron aplicaciones, instalaciones, entrenamientos ni conexiones a equipos.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `aoii.bat` | Lanzador Windows existente; comprobar su directorio de trabajo. |
| `backend/` | Lógica de inspección, procesamiento o servicios. |
| `config.json` | Configuración local consumida por los scripts. |
| `frontend/` | Interfaz de usuario y recursos de presentación. |
| `good/` | Muestras de referencia. |
| `NG/` | Muestras clasificadas como NG. |
| `openvino_cache/` | Caché de inferencia OpenVINO. |
| `requirements.txt` | Dependencias Python declaradas por el proyecto. |
| `tempor/` | Archivos temporales de trabajo. |
| `training/` | Datos y/o utilidades de entrenamiento; revisar su contenido antes de ejecutar. |
| `venv/` | Entorno virtual local; no sustituye la declaración de dependencias. |
| `weights/` | Pesos y artefactos de modelos. |

## Preparación

Se necesita Python y un entorno compatible con las versiones declaradas. La versión exacta de Python no se ha validado. En PowerShell, desde esta carpeta:

```powershell
python -m venv .venv-doc
.\.venv-doc\Scripts\Activate.ps1
python -m pip install -r "requirements.txt"
```

## Configuración

Revisar `config.json` antes del arranque. Sus claves de primer nivel son:

`Components`, `Image_correlation1`, `Image_correlation2`, `Image_correlation3`, `Image_correlation4`, `Image_correlation5`, `Image_correlation6`, `Modelbinpath`, `Folder_path`, `enviados_log`, `scorelimit1`, `scorelimit2`, `scorelimit3`, `log_path`, `model v3`, `PLC_IP`, `PLC_PORT`.

Ajustar rutas de imágenes y modelos, regiones de interés y límites de clasificación según la estación. Si aparecen PLC_IP y PLC_PORT, configurarlos para el equipo correspondiente. Mantener los archivos de modelo y metadatos requeridos por el código. Las rutas locales o compartidas deben existir y ser accesibles.

## Ejecución

Desde la raíz de esta carpeta, con el entorno activado:

```powershell
python -m frontend.newmain
```

## Flujo de trabajo

1. Revisar configuración, modelos y carpetas de entrada/salida.
2. Abrir la interfaz y cargar las imágenes o activar el modo de seguimiento disponible.
3. Consultar los resultados de inspección y los registros generados por la variante utilizada.
4. Validar con muestras conocidas antes de habilitar comunicación con el PLC. Los módulos PLC incluyen escritura de bits.

## Verificación y mantenimiento

La documentación se comprobó contra la estructura y el código local, sin prueba funcional. Si falla un import, revisar el entorno y el manifiesto de la variante; si falla una lectura, comprobar el directorio de trabajo y las rutas configuradas. Actualizar este README cuando cambien entradas, dependencias o configuración.

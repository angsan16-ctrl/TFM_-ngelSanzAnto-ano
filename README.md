# TFM SAF — Excel → MySQL → Python/Pandas

Proyecto reproducible para cargar `data/plantilla.xlsx` en MySQL 8.x sin inventar datos, conservar los IDs existentes y dejar la base preparada para RDKit, xTB/ORCA, Machine Learning y NetworkX.

La auditoría del Excel está en `docs/EXCEL_AUDIT.md`.

## Estructura

```text
TFM_SAF/
├── database/
│   ├── schema.sql
│   └── create_user.sql
├── data/
│   ├── plantilla.xlsx
│   └── rejected/
├── docs/
│   └── EXCEL_AUDIT.md
├── src/
│   ├── db/
│   │   ├── connection.py
│   │   └── queries.py
│   ├── etl/
│   │   ├── config.py
│   │   ├── extract.py
│   │   ├── transform.py
│   │   ├── validate.py
│   │   └── load.py
│   └── repositories/
├── scripts/
│   ├── load_excel_to_mysql.py
│   └── test_database.py
├── logs/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── load_excel_to_mysql.py
└── test_database.py
```

Los dos scripts de la raíz son envoltorios para que puedas ejecutar exactamente `python load_excel_to_mysql.py` y `python test_database.py`.

# PASO 1

**Objetivo:** instalar Python 3.11 o superior y comprobar que Windows lo reconoce.

**Dónde:** PowerShell o Símbolo del sistema.

**Archivo:** ninguno.

**Acción:** instala Python y activa la opción de añadir Python al PATH durante el instalador. Después abre una terminal nueva.

**Comando:**

```bat
py --version
```

**Resultado esperado:** algo como `Python 3.11.x` o una versión superior.

**Si falla:** reinstala Python marcando la opción de PATH, o usa `python --version` para comprobar si tu instalación usa ese comando.

# PASO 2

**Objetivo:** entrar en la carpeta del proyecto.

**Dónde:** PowerShell o CMD.

**Archivo:** carpeta `TFM_SAF`.

**Acción:** sustituye la ruta de ejemplo por la carpeta donde hayas descomprimido el proyecto.

**Comando:**

```bat
cd C:\ruta\donde\descomprimiste\TFM_SAF
```

**Resultado esperado:** el prompt de la terminal termina en `TFM_SAF>`.

**Si falla:** comprueba la ruta con el Explorador de archivos y usa comillas si contiene espacios.

# PASO 3

**Objetivo:** crear un entorno virtual aislado.

**Dónde:** raíz de `TFM_SAF`.

**Archivo:** se creará `.venv\`.

**Acción:** crea y activa el entorno.

**Comando:**

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
```

Si tu Python es posterior y `py -3.11` no existe, usa:

```bat
py -m venv .venv
.venv\Scripts\activate
```

**Resultado esperado:** aparece `(.venv)` al principio del prompt.

**Si falla:** ejecuta `py --version`; si no existe, revisa el PASO 1.

# PASO 4

**Objetivo:** instalar las dependencias Python.

**Dónde:** terminal con `(.venv)` activo.

**Archivo:** `requirements.txt`.

**Acción:** actualiza pip e instala las librerías.

**Comando:**

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Resultado esperado:** instalación finaliza sin errores.

**Si falla:** copia el error completo; normalmente indicará una dependencia concreta o un problema de red/permiso.

# PASO 5

**Objetivo:** instalar MySQL Server 8.x y MySQL Workbench.

**Dónde:** instalador oficial de MySQL para Windows.

**Archivo:** ninguno del proyecto.

**Acción:** instala MySQL Server y Workbench. Durante la instalación define una contraseña de administrador `root` y guárdala de forma segura. No se usa `root` desde Python.

**Comando de comprobación opcional en terminal:**

```bat
mysql --version
```

**Resultado esperado:** Workbench abre y puedes crear/probar una conexión local a `127.0.0.1:3306` como administrador.

**Si falla:** verifica que el servicio MySQL está iniciado en `services.msc` y que el puerto configurado es 3306.

# PASO 6

**Objetivo:** crear la base y las 11 tablas.

**Dónde:** MySQL Workbench conectado como `root` o como administrador.

**Archivo:** `database\schema.sql`.

**Acción:** en Workbench abre `File > Open SQL Script`, selecciona `database\schema.sql` y pulsa el icono de rayo para ejecutar todo.

**Comando SQL de comprobación:**

```sql
USE saf_biomass;
SHOW TABLES;
```

**Resultado esperado:** aparecen 11 tablas: `source`, `biomass`, `biomass_composition`, `molecule`, `biomass_molecule`, `reaction`, `reaction_participant`, `fuel_property`, `molecular_descriptor`, `quantum_calculation`, `quantum_property`.

**Si falla:** comprueba que el servidor es MySQL 8.x y que tu conexión tiene permisos para crear bases/tablas.

# PASO 7

**Objetivo:** crear el usuario de aplicación `saf_app` sin usar `root` desde Python.

**Dónde:** editor de texto + MySQL Workbench como administrador.

**Archivo:** `database\create_user.sql`.

**Acción:** abre el archivo y sustituye SOLO `CHANGE_ME` por una contraseña fuerte que tú elijas. Después ejecútalo en Workbench.

**Comando SQL de comprobación:**

```sql
SHOW GRANTS FOR 'saf_app'@'127.0.0.1';
```

**Resultado esperado:** permisos `SELECT`, `INSERT` y `DELETE` sobre `saf_biomass.*`. `DELETE` solo se necesita para la opción explícita `--replace-data`.

**Si falla:** si el usuario ya existía con otra contraseña, ejecuta como administrador:

```sql
ALTER USER 'saf_app'@'127.0.0.1' IDENTIFIED BY 'TU_NUEVA_PASSWORD';
```

No guardes esa contraseña en Git.

# PASO 8

**Objetivo:** configurar Python para conectarse con `saf_app`.

**Dónde:** raíz del proyecto.

**Archivo:** `.env`.

**Acción:** abre `.env` y sustituye `CHANGE_ME` por EXACTAMENTE la misma contraseña usada en el PASO 7.

**Comando:**

```bat
notepad .env
```

Contenido esperado:

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=saf_biomass
MYSQL_USER=saf_app
MYSQL_PASSWORD=TU_PASSWORD_REAL
```

**Resultado esperado:** `.env` queda guardado localmente. Está incluido en `.gitignore`.

**Si falla:** asegúrate de que el archivo se llama exactamente `.env`, no `.env.txt`.

# PASO 9

**Objetivo:** cargar el Excel real mediante Extract → Transform → Validate → Load.

**Dónde:** terminal en la raíz del proyecto, con `(.venv)` activo.

**Archivo:** `load_excel_to_mysql.py`, que usa `data\plantilla.xlsx`.

**Acción:** ejecuta la carga inicial.

**Comando:**

```bat
python load_excel_to_mysql.py
```

**Resultado esperado:** se muestran `[OK]` para cada tabla y `LOAD COMPLETE`. El log queda en `logs\etl.log`.

La carga actual esperada es:

```text
source: 92
biomass: 182
biomass_composition: 305
molecule: 170
biomass_molecule: 13
reaction: 82
reaction_participant: 164
fuel_property: 61
molecular_descriptor: 0
quantum_calculation: 0
quantum_property: 0
```

**Si falla:** revisa `logs\etl.log`. Si hay filas inválidas, se guardan en `data\rejected\<HOJA>_rejected.csv` con `error_reason`, y por defecto MySQL NO se modifica.

No ejecutes `--allow-rejects` para “hacer desaparecer” errores. Úsalo únicamente si decides conscientemente cargar solo las filas válidas tras revisar los CSV rechazados.

# PASO 10

**Objetivo:** comprobar conexión, tablas, conteos, integridad referencial, duplicados, rangos y Pandas.

**Dónde:** terminal en la raíz del proyecto.

**Archivo:** `test_database.py`.

**Acción:** ejecuta las pruebas.

**Comando:**

```bat
python test_database.py
```

**Resultado esperado:** termina con:

```text
DATABASE READY
```

Además, los conteos de MySQL deben coincidir con el Excel.

**Si falla:** lee cada línea `[FAIL]`. Corrige primero el problema indicado; no edites datos directamente en MySQL para “forzar” que pase el test si el Excel es la fuente de verdad.

# PASO 11

**Objetivo:** consultar MySQL desde Python/Pandas sin repetir conexiones.

**Dónde:** un script, notebook o consola Python ejecutada desde la raíz del proyecto.

**Archivo:** `src\db\connection.py` y `src\db\queries.py`.

**Acción:** prueba una consulta simple.

**Comando:**

```bat
python
```

Después:

```python
import pandas as pd
from src.db.connection import engine

df = pd.read_sql("SELECT * FROM biomass", engine)
print(df.head())
```

También puedes usar las funciones reutilizables:

```python
from src.db.queries import (
    get_all_biomass,
    get_biomass_composition_with_source,
    get_rdkit_input,
)

biomass = get_all_biomass()
composition = get_biomass_composition_with_source()
rdkit_input = get_rdkit_input()
```

**Resultado esperado:** recibes `pandas.DataFrame` con los datos cargados.

**Si falla:** comprueba que `(.venv)` está activo, que MySQL está ejecutándose y que `.env` contiene credenciales correctas.

# PASO 12

**Objetivo:** volver a cargar deliberadamente el Excel después de una corrección, sin duplicar IDs.

**Dónde:** terminal en la raíz del proyecto.

**Archivo:** `load_excel_to_mysql.py`.

**Acción:** usa `--replace-data`. El código borra en orden inverso de dependencias y vuelve a insertar todo dentro de una única transacción InnoDB. Si falla, se revierte la transacción.

**Comando:**

```bat
python load_excel_to_mysql.py --replace-data
```

**Resultado esperado:** los conteos vuelven a coincidir exactamente con el Excel.

**Si falla:** la transacción se revierte. Consulta `logs\etl.log`; después ejecuta `python test_database.py` para confirmar el estado.

## Decisiones de diseño importantes

- El Excel es la fuente de verdad. No se consulta ninguna fuente externa durante la carga.
- Las celdas realmente vacías pasan a `NULL`. Los textos literales `NA`, `N/A`, `null`, `None` o `-` NO se reinterpretan silenciosamente como NULL; si aparecen en una columna numérica, se rechaza la fila.
- Los IDs del Excel se insertan explícitamente. MySQL conserva `AUTO_INCREMENT` para registros futuros.
- DOI e InChIKey son `UNIQUE` cuando existen; MySQL permite múltiples `NULL` en un índice único.
- Los porcentajes de composición y reacción tienen `CHECK` 0–100.
- `reported_yield` no tiene un CHECK 0–100 porque en el Excel actual puede ser `%` o `g/L`.
- Las tablas de descriptores/cuántica existen aunque hoy estén vacías.
- `canonical_smiles` no se inventa. `get_rdkit_input()` devuelve únicamente moléculas con SMILES ya presente.
- Los ficheros pesados de xTB/ORCA se referencian por ruta/hash en `quantum_calculation`; no se guardan blobs enormes en MySQL.
- No hay ORM complejo: SQLAlchemy se usa para conexión/transacciones/consultas, y Pandas para ETL/DataFrames.

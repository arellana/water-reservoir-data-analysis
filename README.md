# 🌊 EmbalsesCordoba

## 🛰️ Análisis del Estado Trófico de los Embalses de Córdoba
**Basado en imágenes satelitales ópticas Sentinel-2.**

Repositorio destinado al análisis del estado trófico de diversos embalses en la provincia de Córdoba, Argentina, utilizando herramientas de **teledetección, análisis espacial y machine learning**.

Esta es la versión reorganizada del repositorio: contiene únicamente el código y los datos vectoriales que el algoritmo usa realmente (se eliminaron carpetas y archivos sueltos sin referencias en el código). Ver `DOCUMENTACION.txt` para el detalle línea por línea de qué hace cada carpeta, la lógica del pipeline, y los datos satelitales que faltan/se agregaron.

---

## 📂 Contenido del Repositorio

### 🗂️ Carpetas
- ✏️ **geometrias-corregidas**
  Contiene `Embalses unificado.shp`: el polígono único con el contorno de todos los embalses, usado por los 4 notebooks para recortar la imagen satelital al área de interés antes de calcular cualquier índice.

- 🗺️ **poligonosnorte**
  Polígonos individuales de los embalses de la zona Norte (Cruz del Eje, El Cajón, San Roque), usados para separar estadísticas por embalse.

- 🗺️ **poligonossur**
  Ídem para la zona Sur (Río Tercero, Los Molinos, Piedra Mora, Cerro Pelado, Arroyo Corto, La Viña, Usina 3).

- 🧩 **2022/Poligonos**
  Polígonos de entrenamiento (ROIs dibujadas a mano) usados por `Presentacion2.ipynb` como muestras etiquetadas para los clasificadores supervisados y para comparar firmas espectrales entre coberturas.

- 🛰️ **Imagenes enero 2021**
  Stacks Sentinel-2 (`Norte_20mTODOS.tif`, `Sur_20mTODOS.tif`), 11 bandas a 20 m, recortados sobre las zonas de los embalses. Se generaron a partir de datos públicos de Sentinel-2 L2A (ver sección 3.1 de `DOCUMENTACION.txt`). Esta carpeta es un symlink a un disco externo (`/media/javi/KINGSTON/Sentinel_Cordoba/Imagenes enero 2021`) por el peso de los archivos, y no se versiona en git.

---

### 📑 Archivos principales
- 📘 **Estadistica_ROIs.ipynb**
  Notebook que analiza estadísticas de las **Regiones de Interés (ROIs)**:
  - Firma Espectral
  - Índices Ópticos (NDVI, NDWI)
  - Brightness, Greeness, Wetness

- 🌲 **RandomForest.ipynb**
  Implementación de un modelo **Random Forest** (y árbol de decisión) para clasificar el estado trófico, con matriz de confusión, accuracy, kappa y validación cruzada.

- ⚙️ **funciones.py**
  Funciones auxiliares:
  - `nequalize()` - normaliza/equaliza bandas por percentiles.
  - `plot_rgb()` - compone y grafica combinaciones de bandas.
  - `delNone()` - descarta nodata y normaliza por el factor de reflectancia.
  - `guardar_GTiff()` - escribe una matriz a GeoTIFF con CRS y transform.

- 📙 **Presentacion1.ipynb** y **Presentacion2.ipynb**
  - Métodos de clasificación **KMeans** (y k-POD) aplicados a las ROIs.
  - Métodos de **Machine Learning** aplicados a las ROIs junto con análisis de firmas espectrales:
    - Tasseled Cap (Brightness, Greeness, Wetness)
    - Clasificadores Supervisados y No Supervisados

- 📝 **DOCUMENTACION.txt**
  Detalle de la lógica del pipeline, qué usa cada carpeta, dependencias adicionales detectadas en el código, y qué se excluyó del repositorio original y por qué.

---

## ▶️ Ejecución del Proyecto

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/arellana/EmbalsesCordoba.git
   cd EmbalsesCordoba
   ```

2. **Preparar el entorno**
   Instalar dependencias desde el archivo **YAML**:

   ```bash
   conda env create -f dependencies.yml
   ```

   Faltan en `dependencies.yml` algunas dependencias detectadas en el código (`kPOD`, `dictances`, `cmasher`); instalarlas aparte con pip. Ver `DOCUMENTACION.txt` (sección 4).

3. **Explorar los notebooks**

   * 📘 `Estadistica_ROIs.ipynb`: estadísticas de las ROIs.
   * 📙 `Presentacion1.ipynb` y `Presentacion2.ipynb`: análisis visual y métodos de ML.
   * 🌲 `RandomForest.ipynb`: modelo supervisado aplicado.

4. **Inspeccionar datos geoespaciales**

   * Las carpetas con geometrías (`geometrias-corregidas`, `poligonosnorte`, `poligonossur`, `2022/Poligonos`) contienen los polígonos de entrada del algoritmo.
   * 🔧 Se pueden modificar las **Regiones de Interés (ROIs)** para estudiar nuevos sitios.

---

## 📝 Cosas por Hacer

* 🌐 Traducir todo el repositorio al inglés.
* 🛰️ Conseguir/generar los stacks Sentinel-2 de **2022** (`2022/Stack/stack2022Norte.tif`, `stack2022Sur.tif`, y el recorte de Los Molinos), que usan `RandomForest.ipynb` y `Presentacion2.ipynb` y todavía no están disponibles.
* 📦 Sumar `kPOD`, `dictances` y `cmasher` a `dependencies.yml`.
* 📖 Documentar cada notebook con descripciones claras.

---

## 👨‍🔬 Créditos

Desarrollado por **Javier Arellana**

* Instituto de Astronomía y Física del Espacio (IAFE), **UBA – CONICET**
* Departamento de Física, Facultad de Ciencias Exactas y Naturales, **Universidad de Buenos Aires**

---

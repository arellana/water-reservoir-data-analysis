<p align="center">
  <img src="assets/banner.jpeg" alt="EmbalsesCordoba banner" width="100%">
</p>

# 🌊 EmbalsesCordoba

## 🛰️ Análisis del Estado Trófico de los Embalses de Córdoba
**Basado en imágenes satelitales ópticas Sentinel-2.**

Repositorio destinado al análisis del estado trófico de diversos embalses en la provincia de Córdoba, Argentina, utilizando herramientas de **teledetección, análisis espacial y machine learning**.

Esta es la versión reorganizada del repositorio: contiene únicamente el código y los datos vectoriales que el algoritmo usa realmente (se eliminaron carpetas y archivos sueltos sin referencias en el código). Ver `DOCUMENTACION.txt` para el detalle línea por línea de qué hace cada carpeta, la lógica del pipeline, y los datos satelitales que faltan/se agregaron.

---

## 📂 Contenido del Repositorio

### 🗂️ Carpetas
- 🗺️ **Poligonos**
  Toda la información vectorial del proyecto en un solo lugar:
  - `Embalses_unificado.shp` — el polígono único con el contorno de todos los embalses, usado por los 4 notebooks para recortar la imagen satelital al área de interés antes de calcular cualquier índice.
  - `Norte/PoligonosEmbalses18-10.shp` — polígonos individuales de los embalses de la zona Norte (Cruz del Eje, El Cajón, San Roque), usados para separar estadísticas por embalse.
  - `Sur/PoligonosEmbalsesSur18-10.shp` — ídem para la zona Sur (Río Tercero, Los Molinos, Piedra Mora, Cerro Pelado, Arroyo Corto, La Viña, Usina 3).
  - `Entrenamiento_2022/` — polígonos de entrenamiento (ROIs dibujadas a mano) usados por `Presentacion2.ipynb` y `RandomForest.ipynb` como muestras etiquetadas para los clasificadores supervisados y para comparar firmas espectrales entre coberturas.

- 🛰️ **ImagenesSentinel**
  Carpeta única con todos los stacks Sentinel-2 que usan los notebooks: `Norte_20mTODOS.tif` y `Sur_20mTODOS.tif` (17/01/2021, 11 bandas a 20 m) y `stack2022norte.tif` y `StackRecortado_Molinos_B1a8_11_12.tif` (18/02/2022, 10 bandas a 20 m). Se generaron a partir de datos públicos de Sentinel-2 L2A (ver sección 3 de `DOCUMENTACION.txt`) y se versionan con **Git LFS** por su peso.

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

   * La carpeta `Poligonos` (con sus subcarpetas `Norte`, `Sur` y `Entrenamiento_2022`) contiene todos los polígonos de entrada del algoritmo.
   * 🔧 Se pueden modificar las **Regiones de Interés (ROIs)** para estudiar nuevos sitios.

---

## 📝 Cosas por Hacer

* 🌐 Traducir todo el repositorio al inglés.
* 🗺️ Recuperar o volver a trazar `Poligonos/Entrenamiento_2022/TrainingMolinosPoligonos.shp` (ROIs de entrenamiento de Los Molinos, dibujadas a mano, que usa `RandomForest.ipynb`).
* 🛰️ Definir y generar `ImagenesSentinel/stack2022norte-2.tif`, que usa `Presentacion2.ipynb` (zona='norte-2') y todavía no está disponible.
* 📦 Sumar `kPOD`, `dictances` y `cmasher` a `dependencies.yml`.
* 📖 Documentar cada notebook con descripciones claras.

---

## 👨‍🔬 Créditos

Desarrollado por **Javier Arellana**

* Instituto de Astronomía y Física del Espacio (IAFE), **UBA – CONICET**
* Departamento de Física, Facultad de Ciencias Exactas y Naturales, **Universidad de Buenos Aires**

---

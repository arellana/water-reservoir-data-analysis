# Embalses_V2

Version limpia del proyecto de analisis del estado trofico de los embalses
de Cordoba: solo el codigo y los datos vectoriales que el algoritmo usa
realmente. Ver `DOCUMENTACION.txt` para el detalle de que hace cada
carpeta, la logica del pipeline y los datos (imagenes Sentinel-2) que
faltan agregar para poder correrlo.

## Notebooks
- `Estadistica_ROIs.ipynb` - estadisticas de las ROIs (firma espectral,
  indices opticos, Brightness/Greeness/Wetness).
- `RandomForest.ipynb` - clasificacion supervisada (Random Forest / arbol
  de decision) del estado trofico.
- `Presentacion1.ipynb` - clustering no supervisado (KMeans, k-POD).
- `Presentacion2.ipynb` - Tasseled Cap, firmas espectrales y
  clasificadores supervisados/no supervisados.

## Entorno
```
conda env create -f dependencies.yml
```
Ver `DOCUMENTACION.txt` (seccion 4) por dependencias adicionales no
incluidas en `dependencies.yml` (kPOD, dictances, cmasher).

## Datos faltantes
El repositorio no incluye las imagenes Sentinel-2 (pesan demasiado para
git). Ver `DOCUMENTACION.txt` (seccion 3) para la lista exacta de
archivos raster/vector a agregar y sus rutas esperadas.

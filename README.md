# Proyecto 2 — Parser CYK (Cocke–Younger–Kasami)

Autores:

- Joel Antonio Jaquez López — 23369
- Juan Francisco Martínez — 23617

## Descripción

Este proyecto implementa el algoritmo CYK (Cocke–Younger–Kasami) para el parsing de frases usando una gramática libre de contexto (CFG) convertida a la Forma Normal de Chomsky (CNF). El programa está escrito en Python y contiene:

- Una implementación de la representación de gramáticas (clase `Grammar`).
- Un conversor simple de CFG a CNF (`CNFConverter`).
- Un parser CYK con programación dinámica (`CYKParser`) que además construye un árbol de parsing parcial si la frase es aceptada.
- Modo interactivo y opciones para analizar frases directamente.

La gramática de ejemplo está en inglés y viene cargada por defecto (pronombres, determinantes, verbos, sustantivos y preposiciones). El vocabulario está definido en el archivo principal `CYK.py`.

## Requisitos

- Python 3.8 o superior.
- No requiere dependencias externas (solo librerías estándar).

## Archivos principales

- `CYK.py` — Implementación completa del conversor a CNF y del parser CYK, además del menú interactivo.

## Cómo ejecutar

Abrir una terminal (PowerShell en Windows) en la carpeta del proyecto y ejecutar:

```powershell
python CYK.py
```

El programa mostrará la gramática original, la gramática convertida a CNF y un menú con opciones:

1. Modo interactivo (ingresar frases manualmente).
2. Ingresar una frase directamente para analizar.
3. Salir.

También puede ejecutar una verificación rápida de sintaxis (sin ejecutar el script) con:

```powershell
python -m py_compile CYK.py
```

## Vocabulario de ejemplo

El parser usa la siguiente vocabulario (tal como aparece en `CYK.py`):

- Pronombres: he, she
- Verbos: cooks, drinks, eats, cuts
- Determinantes: a, the
- Sustantivos: cat, dog, beer, cake, juice, meat, soup, fork, knife, oven, spoon
- Preposiciones: in, with

Frases de ejemplo válidas:

- she eats a cake
- the cat drinks the beer
- he cooks the meat with a fork
- she cuts a cake with a knife
- the dog eats the soup in the oven

## Ejemplo de uso (PowerShell)

```powershell
# Ejecutar el programa
python CYK.py

# En el menú seleccionar "2" y luego ingresar, por ejemplo:
she eats a cake

# Salida esperada (resumen):
# Resultado: SI
# La frase pertenece al lenguaje generado por la gramática.
# Tiempo de ejecución: 0.000xxx segundos
# (Opcional) Se imprime un árbol de parsing básico.
```

## Notas y limitaciones

- La gramática está embebida en `CYK.py`. Para probar otras gramáticas o vocabularios, modifique la función `create_english_grammar()` o cree una función similar.
- El conversor a CNF implementado es simple y cubre casos básicos: reemplazo de terminales en producciones binarias y descomposición de producciones largas. No gestiona explícitamente producciones epsilon ni eliminación de símbolos inaccesibles/useless.
- El árbol de parsing construido usa el primer back-pointer que encuentre; para gramáticas ambiguas puede no mostrar todas las derivaciones posibles.

## Verificación rápida de sintaxis

Para comprobar que `CYK.py` no contiene errores de sintaxis, ejecute:

```powershell
python -m py_compile CYK.py
```

Si no aparece salida, la verificación fue exitosa.

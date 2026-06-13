# ANALIZADOR Y VISUALIZADOR DE LIMITES - MATE1133
# Universidad Católica de Temuco
# INDICE DEL CODIGO
#   LINEA  30  - IMPORTS Y CONFIGURACION GLOBAL
#   LINEA  45  - BLOQUE 1: FUNCIONES MATEMATICAS
#   LINEA  48  - parsear_funcion()             -> convierte texto a expresion SymPy
#   LINEA  60  - parsear_c()                   -> convierte texto de c a valor SymPy
#   LINEA  70  - sustitucion_directa()         -> PASO 1: evalua f(c) directamente
#   LINEA  84  - detectar_indeterminacion()    -> PASO 2: clasifica 0/0 o inf/inf
#   LINEA  96  - factorizar_expresion()        -> PASO 3a: factoriza y cancela factores
#   LINEA 115  - resolver_trigonometrico()     -> PASO 3b: limites notables sin/cos
#   LINEA 150  - analizar_limite_infinito()    -> PASO 3c: reglas de grado x->inf
#   LINEA 175  - calcular_lateral_izquierdo()  -> lim x->c- por aproximacion
#   LINEA 200  - calcular_lateral_derecho()    -> lim x->c+ por aproximacion
#   LINEA 225  - verificar_continuidad()       -> verifica las 3 condiciones
#   LINEA 265  - calcular_limite()             -> ALGORITMO PRINCIPAL (orquesta todo)
#   LINEA 325  - BLOQUE 2: GRAFICACION
#   LINEA 328  - graficar_funcion()            -> dibuja la curva con Matplotlib
#   LINEA 380  - BLOQUE 3: INTERFAZ GRAFICA
#   LINEA 383  - mostrar_sintaxis()            -> ventana con guia de escritura
#   LINEA 425  - mostrar_ejemplos()            -> ejemplos resueltos en panel
#   LINEA 455  - exportar_resultado()          -> guarda resultado en .txt
#   LINEA 465  - construir_interfaz()          -> construye toda la GUI con pestanas
#   LINEA 700  - MAIN
 
import sympy as sp
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
 
# Silencia errores de fondo de Tkinter al cerrar (compatibilidad Python 3.14).
def _silenciar_errores(err, *args):
    pass
 
# Variable simbolica x que SymPy usara en todas las expresiones matematicas.
x = sp.Symbol('x')
 
# Variable global para guardar el ultimo resultado y poder exportarlo.
ultimo_resultado = ""
 
 
# BLOQUE 1: FUNCIONES MATEMATICAS
# Aqui esta toda la logica de calculo de limites.
 
 
# FUNCION: parsear_funcion  (linea 48)
# Convierte el texto ingresado por el usuario en una expresion de SymPy.

def parsear_funcion(texto):
    texto = texto.replace("^", "**")     # Permite usar ^ en vez de ** para potencias.
    texto = texto.replace("sen", "sin")  # Acepta "sen" como variante en espanol de seno.
    permitidas = {                        # Diccionario con funciones matematicas reconocidas.
        'x': x, 'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
        'sqrt': sp.sqrt, 'log': sp.log, 'exp': sp.exp,
        'Abs': sp.Abs, 'pi': sp.pi, 'oo': sp.oo
    }
    return sp.sympify(texto, locals=permitidas)  # sympify transforma el texto en objeto simbolico.
 
 

# FUNCION: parsear_c  (linea 60)
# Convierte el texto del valor c en un valor simbolico de SymPy.

def parsear_c(texto):
    texto = texto.replace("inf", "oo")  # Acepta "inf" como sinonimo de infinito.
    permitidas = {'oo': sp.oo, 'pi': sp.pi}
    return sp.sympify(texto, locals=permitidas)
 
 

# FUNCION: sustitucion_directa  (linea 70)
# PASO 1 del algoritmo: evalua f(c) directamente.
# Si el resultado es finito, el limite es ese valor y no se necesita mas.

def sustitucion_directa(expr, c_val):
    resultado = expr.subs(x, c_val)    # subs reemplaza x por c_val en la expresion.
    resultado = sp.simplify(resultado)  # simplify reduce a la forma mas simple.
    if resultado == sp.nan:             # nan significa resultado no definido.
        return None
    if resultado.is_finite:             # Numero finito: sustitucion exitosa.
        return resultado
    if resultado in (sp.oo, -sp.oo):   # Infinito: tambien es resultado valido.
        return resultado
    return None                         # Retorna None si hay indeterminacion (0/0).
 
 

# FUNCION: detectar_indeterminacion  (linea 84)
# PASO 2: determina el tipo de indeterminacion detectada.

def detectar_indeterminacion(expr, c_val):
    num, den = expr.as_numer_denom()           # Separa en numerador y denominador.
    val_num = sp.simplify(num.subs(x, c_val))  # Evalua el numerador en c.
    val_den = sp.simplify(den.subs(x, c_val))  # Evalua el denominador en c.
    if val_num == 0 and val_den == 0:
        return "0/0"
    if val_num in (sp.oo, -sp.oo) and val_den in (sp.oo, -sp.oo):
        return "inf/inf"
    return "otra"
 
 

# FUNCION: factorizar_expresion  (linea 96)
# PASO 3a: resuelve 0/0 factorizando y cancelando factores comunes.
# Ejemplo: (x^2-4)/(x-2) -> (x-2)(x+2)/(x-2) -> x+2 -> evaluar en c.

def factorizar_expresion(expr, c_val):
    pasos = []
    num, den = expr.as_numer_denom()
    num_fact = sp.factor(num)           # factor() factoriza el numerador.
    den_fact = sp.factor(den)           # factor() factoriza el denominador.
    pasos.append(f"  Numerador:   {num} -> {num_fact}")
    pasos.append(f"  Denominador: {den} -> {den_fact}")
    expr_simp = sp.cancel(expr)         # cancel() cancela factores comunes.
    pasos.append(f"  Simplificado: {expr_simp}")
    resultado = sp.simplify(expr_simp.subs(x, c_val))
    if resultado.is_finite or resultado in (sp.oo, -sp.oo):
        pasos.append(f"  Sustitucion x={c_val}: {resultado}")
        return resultado, pasos
    return None, pasos
 
 

# FUNCION: resolver_trigonometrico  (linea 115)
# PASO 3b: reconoce limites trigonometricos notables cuando c = 0.
# Patrones: sin(u)/u = 1  |  (1-cos(u))/u^2 = 1/2

def resolver_trigonometrico(expr, c_val):
    pasos = []
    if c_val != 0:
        return None, pasos
    num, den = expr.as_numer_denom()
 
    # Patron sin(u)/u = 1
    if num.has(sp.sin) and not den.has(sp.sin):
        for atomo in sp.preorder_traversal(num):  # Recorre cada elemento del numerador.
            if isinstance(atomo, sp.sin):
                arg = atomo.args[0]               # Extrae el argumento del seno.
                cociente = sp.simplify(den / arg)
                if cociente.is_number:
                    resultado = sp.simplify(sp.simplify(num / atomo) / cociente)
                    pasos.append(f"  Patron: sin({arg}) / {den}")
                    pasos.append(f"  Limite notable: lim sin(u)/u = 1 cuando u->0")
                    pasos.append(f"  Resultado = {resultado}")
                    return resultado, pasos
 
    # Patron (1-cos(u))/u^2 = 1/2
    if num.has(sp.cos):
        for atomo in sp.preorder_traversal(num):
            if isinstance(atomo, sp.cos):
                arg = atomo.args[0]
                if sp.simplify(num - sp.expand(1 - atomo)) == 0:
                    cociente_den = sp.simplify(den / arg**2)
                    if cociente_den.is_number:
                        resultado = sp.Rational(1, 2) / cociente_den
                        pasos.append(f"  Patron: (1-cos({arg})) / {den}")
                        pasos.append(f"  Limite notable: lim (1-cos(u))/u^2 = 1/2 cuando u->0")
                        pasos.append(f"  Resultado = {resultado}")
                        return resultado, pasos
    return None, pasos
 
 

# FUNCION: analizar_limite_infinito  (linea 150)
# PASO 3c: calcula limites cuando x -> oo o -oo usando reglas de grado.
# Regla 1: grado(N) < grado(D) -> 0
# Regla 2: grado(N) = grado(D) -> cociente de coeficientes lideres
# Regla 3: grado(N) > grado(D) -> infinito

def analizar_limite_infinito(expr, c_val):
    pasos = []
    if c_val not in (sp.oo, -sp.oo):
        return None, pasos
    if not expr.is_rational_function(x):
        return None, pasos
    num, den = expr.as_numer_denom()
    grado_num = sp.degree(sp.Poly(sp.expand(num), x))  # Calcula el grado del numerador.
    grado_den = sp.degree(sp.Poly(sp.expand(den), x))  # Calcula el grado del denominador.
    lc_num = sp.LC(sp.Poly(sp.expand(num), x))          # Coeficiente lider del numerador.
    lc_den = sp.LC(sp.Poly(sp.expand(den), x))          # Coeficiente lider del denominador.
    pasos.append(f"  Grado num: {grado_num} (lider: {lc_num})  |  Grado den: {grado_den} (lider: {lc_den})")
    if grado_num < grado_den:
        pasos.append(f"  Regla: grado(N) < grado(D)  ->  limite = 0")
        return sp.Integer(0), pasos
    elif grado_num == grado_den:
        resultado = sp.simplify(sp.sympify(lc_num) / sp.sympify(lc_den))
        pasos.append(f"  Regla: grado(N) = grado(D)  ->  {lc_num}/{lc_den} = {resultado}")
        return resultado, pasos
    else:
        pasos.append(f"  Regla: grado(N) > grado(D)  ->  limite = infinito")
        return sp.oo, pasos
 
 

# FUNCION: calcular_lateral_izquierdo  (linea 175)
# Aproxima lim x->c- evaluando f(c-0.1), f(c-0.01), f(c-0.001).

def calcular_lateral_izquierdo(expr, c_val):
    pasos = ["  Limite lateral IZQUIERDO (x -> c-)"]
    if c_val in (sp.oo, -sp.oo):
        return None, pasos
    deltas = [sp.Rational(1, 10), sp.Rational(1, 100), sp.Rational(1, 1000)]
    valores = []
    for delta in deltas:                              # Para cada delta dentro de deltas.
        val = sp.simplify(expr.subs(x, c_val - delta))  # Evalua a la izquierda de c.
        if val == sp.oo:
            pasos.append(f"  f({c_val}-{delta}) -> +inf")
            return sp.oo, pasos
        if val == -sp.oo:
            pasos.append(f"  f({c_val}-{delta}) -> -inf")
            return -sp.oo, pasos
        if val.is_real and val.is_finite:
            valores.append(float(val))
            pasos.append(f"  f({c_val}-{delta}) = {round(float(val), 6)}")
    if len(valores) >= 2 and abs(valores[-1] - valores[-2]) < 0.001:  # Verifica convergencia.
        resultado = sp.nsimplify(valores[-1], rational=True, tolerance=1e-4)
        pasos.append(f"  Convergencia -> limite izq = {resultado}")
        return resultado, pasos
    return None, pasos
 
 

# FUNCION: calcular_lateral_derecho  (linea 200)
# Aproxima lim x->c+ evaluando f(c+0.1), f(c+0.01), f(c+0.001).
# Mismo algoritmo que el izquierdo pero sumando delta.

def calcular_lateral_derecho(expr, c_val):
    pasos = ["  Limite lateral DERECHO (x -> c+)"]
    if c_val in (sp.oo, -sp.oo):
        return None, pasos
    deltas = [sp.Rational(1, 10), sp.Rational(1, 100), sp.Rational(1, 1000)]
    valores = []
    for delta in deltas:
        val = sp.simplify(expr.subs(x, c_val + delta))  # Evalua a la derecha de c.
        if val == sp.oo:
            pasos.append(f"  f({c_val}+{delta}) -> +inf")
            return sp.oo, pasos
        if val == -sp.oo:
            pasos.append(f"  f({c_val}+{delta}) -> -inf")
            return -sp.oo, pasos
        if val.is_real and val.is_finite:
            valores.append(float(val))
            pasos.append(f"  f({c_val}+{delta}) = {round(float(val), 6)}")
    if len(valores) >= 2 and abs(valores[-1] - valores[-2]) < 0.001:
        resultado = sp.nsimplify(valores[-1], rational=True, tolerance=1e-4)
        pasos.append(f"  Convergencia -> limite der = {resultado}")
        return resultado, pasos
    return None, pasos
 
 

# FUNCION: verificar_continuidad  (linea 225)
# Verifica las 3 condiciones de continuidad en x = c:
#   1) f(c) existe
#   2) lim x->c f(x) existe (laterales iguales)
#   3) lim x->c f(x) = f(c)

def verificar_continuidad(expr, c_val):
    lineas = []
    val_en_c = sp.simplify(expr.subs(x, c_val))  # Condicion 1: evalua f(c).
    if val_en_c.is_finite and val_en_c.is_real:
        lineas.append(f"  1. f({c_val}) = {val_en_c}  ->  CUMPLE")
        cond1 = True
    else:
        lineas.append(f"  1. f({c_val}) = {val_en_c}  ->  NO CUMPLE")
        cond1 = False
 
    lim_izq, _ = calcular_lateral_izquierdo(expr, c_val)  # Condicion 2: calcula laterales.
    lim_der, _ = calcular_lateral_derecho(expr, c_val)
    if lim_izq is not None and lim_der is not None:
        dif = sp.simplify(lim_izq - lim_der)
        if dif == 0 or abs(float(dif.evalf())) < 0.0001:  # Laterales iguales: limite existe.
            lineas.append(f"  2. lim izq = lim der = {sp.N(lim_izq, 4)}  ->  CUMPLE")
            cond2, limite = True, lim_izq
        else:
            lineas.append(f"  2. lim izq({sp.N(lim_izq,4)}) != lim der({sp.N(lim_der,4)})  ->  NO CUMPLE")
            cond2, limite = False, None
    else:
        lineas.append(f"  2. No se pudo calcular el limite  ->  NO CUMPLE")
        cond2, limite = False, None
 
    if cond1 and cond2:                    # Condicion 3: solo si las otras dos pasan.
        dif3 = sp.simplify(limite - val_en_c)
        if dif3 == 0 or abs(float(dif3.evalf())) < 0.0001:
            lineas.append(f"  3. lim f(x) = f({c_val}) = {sp.N(val_en_c, 4)}  ->  CUMPLE")
            cond3 = True
        else:
            lineas.append(f"  3. lim f(x) != f({c_val})  ->  NO CUMPLE")
            cond3 = False
    else:
        lineas.append(f"  3. No se puede verificar (condiciones previas fallaron)")
        cond3 = False
 
    return cond1 and cond2 and cond3, lineas
 
 

# FUNCION: calcular_limite  (linea 265)
# ALGORITMO PRINCIPAL: orquesta todos los pasos en orden.
# Paso 1 -> Sustitucion directa
# Paso 2 -> Detectar indeterminacion
# Paso 3 -> Estrategia segun el tipo (trig / factorizacion / infinito)
# Paso 4 -> Limites laterales

def calcular_limite(expr, c_val):
    global ultimo_resultado
    lineas = ["•" * 48, f"  f(x) = {expr}", f"  lim x->{c_val} f(x)", "•" * 48]
 
    if c_val in (sp.oo, -sp.oo):           # Caso especial: c infinito -> analisis de grados.
        lineas.append("PASO 1: c = infinito -> analisis de grados")
        resultado, pasos = analizar_limite_infinito(expr, c_val)
        lineas.extend(pasos)
        if resultado is not None:
            lineas.append(f"\n  RESULTADO = {resultado}")
            ultimo_resultado = "\n".join(lineas)
            return resultado, lineas
        return None, lineas
 
    lineas.append("PASO 1: Sustitucion directa")   # Paso 1: sustitucion directa.
    resultado = sustitucion_directa(expr, c_val)
    if resultado is not None:
        lineas.append(f"  f({c_val}) = {resultado}  ->  Exitosa!")
        lineas.append(f"\n  RESULTADO = {resultado}")
        lineas.append("  Metodo: Sustitucion directa")
        ultimo_resultado = "\n".join(lineas)
        return resultado, lineas
 
    lineas.append(f"  f({c_val}) indeterminado -> continuar...")
    lineas.append("PASO 2: Tipo de indeterminacion")
    tipo = detectar_indeterminacion(expr, c_val)   # Paso 2: detectar indeterminacion.
    lineas.append(f"  Tipo detectado: {tipo}")
 
    tiene_trig = expr.has(sp.sin) or expr.has(sp.cos) or expr.has(sp.tan)
    if tiene_trig and c_val == 0:                  # Paso 3a: limite trigonometrico notable.
        lineas.append("PASO 3: Identidades trigonometricas notables")
        resultado, pasos = resolver_trigonometrico(expr, c_val)
        lineas.extend(pasos)
        if resultado is not None:
            lineas.append(f"\n  RESULTADO = {resultado}")
            lineas.append("  Metodo: Limite trigonometrico notable")
            ultimo_resultado = "\n".join(lineas)
            return resultado, lineas
 
    if tipo == "0/0":                              # Paso 3b: factorizacion.
        lineas.append("PASO 3: Factorizacion")
        resultado, pasos = factorizar_expresion(expr, c_val)
        lineas.extend(pasos)
        if resultado is not None:
            lineas.append(f"\n  RESULTADO = {resultado}")
            lineas.append("  Metodo: Factorizacion y cancelacion")
            ultimo_resultado = "\n".join(lineas)
            return resultado, lineas
 
    lineas.append("PASO 4: Limites laterales")     # Paso 4: limites laterales.
    lim_izq, p_izq = calcular_lateral_izquierdo(expr, c_val)
    lim_der, p_der = calcular_lateral_derecho(expr, c_val)
    lineas.extend(p_izq)
    lineas.extend(p_der)
 
    if lim_izq is not None and lim_der is not None:
        dif = sp.simplify(lim_izq - lim_der)
        if dif == 0 or abs(float(dif.evalf())) < 0.0001:
            lineas.append(f"\n  RESULTADO = {sp.N(lim_izq, 6)}")
            lineas.append("  Metodo: Limites laterales")
            ultimo_resultado = "\n".join(lineas)
            return lim_izq, lineas
        else:
            lineas.append(f"\n  RESULTADO: El limite NO EXISTE (laterales distintos)")
            ultimo_resultado = "\n".join(lineas)
            return sp.nan, lineas
 
    ultimo_resultado = "\n".join(lineas)
    return None, lineas
 
 
# .
# BLOQUE 2: GRAFICACION  (linea 325)
# .
 

# FUNCION: graficar_funcion  (linea 328)
# Dibuja la funcion con Matplotlib usando un ciclo for (sin NumPy).
# Marca la linea vertical en c y el punto del limite con circulo hueco.

def graficar_funcion(ax, expr, c_val, resultado):
    ax.clear()
    ax.set_facecolor("#FFF5FB")          # Fondo oscuro coherente con el modo dark.
 
    if c_val in (sp.oo, -sp.oo):
        x_min, x_max, c_numerico = -10, 10, None
    else:
        c_num = float(c_val.evalf())
        c_numerico = c_num
        margen = max(4.0, abs(c_num) + 3)
        x_min, x_max = c_num - margen, c_num + margen
 
    N = 300                              # Cantidad de puntos del grafico.
    paso = (x_max - x_min) / N
    lista_x, lista_y = [], []
 
    for i in range(N + 1):              # Ciclo for para generar puntos sin NumPy.
        xi = x_min + i * paso
        if c_numerico is not None and abs(xi - c_numerico) < 0.03:
            lista_x.append(None)        # None separa segmentos en discontinuidades.
            lista_y.append(None)
            continue
        try:
            yi = float(expr.subs(x, sp.Float(xi)).evalf())
            lista_x.append(None if abs(yi) > 50 else xi)
            lista_y.append(None if abs(yi) > 50 else yi)
        except Exception:
            lista_x.append(None)
            lista_y.append(None)
 
    seg_x, seg_y = [], []               # Dibuja la curva por segmentos continuos.
    for xi, yi in zip(lista_x, lista_y):
        if xi is None:
            if seg_x:
                ax.plot(seg_x, seg_y, color="#EA4383", linewidth=2.2)
            seg_x, seg_y = [], []
        else:
            seg_x.append(xi)
            seg_y.append(yi)
    if seg_x:
        ax.plot(seg_x, seg_y, color="#EA4383", linewidth=2.2, label="f(x)")
 
    if c_numerico is not None:          # Linea vertical en x = c.
        ax.axvline(x=c_numerico, color="#2E0513", linestyle="--",
                   linewidth=1.8, label=f"x={c_val}")
 
    if (resultado is not None and
            resultado not in (sp.nan, sp.oo, -sp.oo) and
            c_numerico is not None):
        try:                            # Punto hueco que marca el valor del limite.
            res_float = float(resultado.evalf())
            ax.plot(c_numerico, res_float, "o", color="#2E0513", markersize=10,
                    markerfacecolor="#FFF5FB", markeredgewidth=2.5,
                    label=f"lim={sp.N(resultado, 4)}")
        except Exception:
            pass
 
    ax.axhline(y=0, color="#2E0513", linewidth=0.8)
    ax.axvline(x=0, color="#2E0513", linewidth=0.8)
    ax.grid(True, linestyle="--", alpha=0.2, color="#2E0513")
    ax.set_xlabel("x", fontsize=11, color="#2E0513")
    ax.set_ylabel("f(x)", fontsize=11, color="#2E0513")
    ax.set_title(f"lim x\u2192{c_val}  f(x)", fontsize=12,
                 fontweight="bold", color="#2E0513")
    ax.tick_params(colors="#2E0513")
    for spine in ax.spines.values():
        spine.set_color("#2E0513")
    ax.figure.patch.set_facecolor("#FFF5FB")
    ax.legend(loc="upper right", fontsize=9,
              facecolor="#FFF5FB", edgecolor="#2E0513", labelcolor="#2E0513")
 
 
# .
# BLOQUE 3: INTERFAZ GRAFICA  (linea 380)
# .
 

# FUNCION: mostrar_sintaxis  (linea 383)
# Abre una ventana secundaria con la guia de como escribir funciones.

def mostrar_sintaxis(ventana_padre):
    win = ctk.CTkToplevel(ventana_padre)  # Ventana secundaria sobre la principal.
    win.title("Guia de Sintaxis")
    win.geometry("460x560")
    win.configure(fg_color="#F0E9ED")
    win.after(100, win.lift)              # Fuerza el foco en Linux (evita ventana vacia).
    win.after(150, lambda: win.grab_set()) # grab_set despues de lift para evitar conflicto.
    ctk.CTkLabel(win, text="Como escribir funciones",
                 font=ctk.CTkFont(size=13, weight="bold"), text_color="#2E0513").pack(pady=(12, 4))
    guia = (
        "POTENCIAS Y RAICES\n"
        "  x al cuadrado    ->  x**2  o  x^2\n"
        "  x al cubo        ->  x**3\n"
        "  raiz de x        ->  sqrt(x)\n\n"
        "TRIGONOMETRICOS\n"
        "  seno              ->  sin(x)  o  sen(x)\n"
        "  coseno            ->  cos(x)\n"
        "  tangente          ->  tan(x)\n"
        "  valor absoluto    ->  Abs(x)\n\n"
        "LIMITES NOTABLES (c=0)\n"
        "  sin(x)/x          ->  sin(x)/x\n"
        "  tan(x)/x          ->  tan(x)/x\n"
        "  (1-cos(x))/x^2    ->  (1-cos(x))/x**2\n\n"
        "LIMITES LATERALES\n"
        "  Abs(x)/x  ,  1/x  ,  1/(x-2)\n\n"
        "LIMITES AL INFINITO\n"
        "  c positivo        ->  oo  o  inf\n"
        "  c negativo        ->  -oo\n\n"
        "CONTINUIDAD\n"
        "  continuo          ->  x**2\n"
        "  discontinuo en 0  ->  1/x\n\n"
        "VALOR DE c\n"
        "  entero            ->  0 / 2 / -3\n"
        "  infinito          ->  oo  o  -oo\n\n"
        "OPERADORES\n"
        "  multiplicacion    ->  3*x  (no 3x)\n"
        "  se acepta ^ o ** ->  x^2 = x**2\n"
    )
    cuadro = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Courier New", size=11), fg_color="#FFF5FB", text_color="#2E0513")
    cuadro.pack(padx=15, pady=4, fill="both", expand=True)
    cuadro.insert("end", guia)
    cuadro.configure(state="disabled")
    ctk.CTkButton(win, text="Cerrar", command=win.destroy, fg_color="#EA4383", text_color="#FFF5FB").pack(pady=8)
 
 

# FUNCION: mostrar_ejemplos  (linea 425)
# Muestra ejemplos resueltos de todos los tipos de la Unidad 2.

def mostrar_ejemplos(cuadro_texto):
    texto = (
        "EJEMPLOS RESUELTOS - UNIDAD 2\n" + "•" * 46 + "\n\n"
        "1. Sustitucion directa:\n"
        "   f(x) = x**2+3*x+1 , c = 2\n"
        "   f(2) = 4+6+1 = 11  ->  RESULTADO = 11\n\n"
        "2. Factorizacion (0/0):\n"
        "   f(x) = (x**2-4)/(x-2) , c = 2\n"
        "   (x-2)(x+2)/(x-2) = x+2 -> 4  ->  RESULTADO = 4\n\n"
        "3. Limite trig sin(x)/x:\n"
        "   f(x) = sin(x)/x , c = 0\n"
        "   Patron sin(u)/u=1  ->  RESULTADO = 1\n\n"
        "4. Limite trig (1-cos)/x^2:\n"
        "   f(x) = (1-cos(x))/x**2 , c = 0\n"
        "   Patron (1-cos(u))/u^2=1/2  ->  RESULTADO = 1/2\n\n"
        "5. Limite al infinito:\n"
        "   f(x) = (2*x**2+1)/(x**2+3) , c = oo\n"
        "   Grado N = Grado D -> 2/1  ->  RESULTADO = 2\n\n"
        "6. Limite NO existe:\n"
        "   f(x) = 1/x , c = 0\n"
        "   lim izq=-inf , lim der=+inf  ->  NO EXISTE\n\n"
        "7. Continuidad:\n"
        "   f(x) = x**2 , c = 3  ->  CONTINUA\n"
        "   f(x) = 1/x  , c = 0  ->  DISCONTINUA\n"
    )
    cuadro_texto.configure(state="normal")
    cuadro_texto.delete("1.0", "end")
    cuadro_texto.insert("end", texto)
    cuadro_texto.configure(state="disabled")
 
 

# FUNCION: exportar_resultado  (linea 455)
# Guarda el ultimo resultado calculado en un archivo .txt

def exportar_resultado():
    global ultimo_resultado
    if not ultimo_resultado:
        print("  Calcule un limite primero para poder exportar.")
        return
    with open("resultado_limite.txt", "w", encoding="utf-8") as archivo:
        archivo.write("ANALIZADOR DE LIMITES - MATE1133\n" + "•" * 48 + "\n")
        archivo.write(ultimo_resultado)
    print("  Guardado en: resultado_limite.txt")
 
 

# FUNCION: construir_interfaz  (linea 465)
# Construye la GUI con 2 pestanas como en la demo original:
#   Pestana "Inicio"          -> bienvenida e instrucciones.
#   Pestana "Calcular Limite" -> herramienta completa con layout 20-60-20.

def construir_interfaz():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
 
    ventana = ctk.CTk()
    ventana.title("Analizador de Limites - MATE1133")
    ventana.configure(fg_color="#FFCFDA")
 
    # Maximizar compatible con Linux y Windows.
    try:
        ventana.state("zoomed")
    except Exception:
        ventana.attributes("-zoomed", True)
 
    # Layout principal: una sola columna y fila que ocupa toda la ventana.
    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_rowconfigure(0, weight=1)
 
    # ── TABVIEW con 2 pestanas (estructura del main.py original)
    tabs = ctk.CTkTabview(ventana)
    tabs.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    tabs.configure(fg_color="#FFCFDA")
 
    tab_inicio = tabs.add("Inicio")
    tab_limite = tabs.add("Calcular Limite")
 
    tab_inicio.configure(fg_color="#FFCFDA")
    tab_limite.configure(fg_color="#F0E9ED")
 
    # ── PESTANA 1: INICIO ────────────────────────────────────────
    tab_inicio.grid_columnconfigure(0, weight=1)
    tab_inicio.grid_rowconfigure(1, weight=1)
 
    ctk.CTkLabel(
        tab_inicio,
        text="Analizador y Visualizador de Limites",
        font=ctk.CTkFont(size=26, weight="bold"),
        text_color="#000000"
    ).pack(pady=(28, 4))
 
    ctk.CTkLabel(
        tab_inicio,
        text="MATE1133  —  Universidad Católica de Temuco",
        font=ctk.CTkFont(size=13),
        text_color="#000000"
    ).pack(pady=(0, 20))
 
    texto_pt1 = (
        "Bienvenido al Analizador de Limites.\n\n"
        "Esta herramienta permite ingresar una funcion f(x) y calcular\n"
        "su limite cuando x tiende a un valor c.\n\n"
    )
    
    texto_titulo = "INSTRUCCIONES DE USO\n\n"
    
    texto_pt2 = (
        "1. Dirigete a la pestana 'Calcular Limite'.\n\n"
        "2. En el primer campo ingresa la funcion f(x).\n"
        "   Ejemplos validos:\n"
        "     (x**2 - 1) / (x - 1)\n"
        "     sin(x) / x\n"
        "     (x**3 - 8) / (x - 2)\n"
        "     (2*x**2 + 1) / (x**2 + 3)\n\n"
        "3. En el segundo campo ingresa el valor c.\n"
        "   Escribe 'oo'  para representar +infinito.\n"
        "   Escribe '-oo' para representar -infinito.\n\n"
        "4. Usa los botones segun lo que necesites:\n"
        "   - 'Calcular Limite'       -> calcula y grafica automaticamente.\n"
        "   - 'Limites Laterales'     -> muestra lim izq y lim der por separado.\n"
        "   - 'Verificar Continuidad' -> verifica las 3 condiciones de continuidad.\n"
        "   - 'Sintaxis'              -> guia de como escribir funciones.\n"
        "   - 'Ejemplos'              -> ejemplos resueltos de cada tipo.\n"
        "   - 'Exportar TXT'          -> guarda el desarrollo en un archivo .txt\n\n"
        "──────────────────────────────────────────\n"
        "NOTA IMPORTANTE\n"
        "──────────────────────────────────────────\n\n"
        "La logica del calculo esta implementada con ciclos y estructuras\n"
        "propias, sin numpy ni sympy.limit(). El algoritmo aplica:\n"
        "  Paso 1: Sustitucion directa\n"
        "  Paso 2: Deteccion del tipo de indeterminacion\n"
        "  Paso 3: Factorizacion / Trig. notable / Reglas de grado\n"
        "  Paso 4: Limites laterales por aproximacion numerica\n"
    )
 
    caja_inicio = ctk.CTkTextbox(
        tab_inicio,
        width=860,
        height=440,
        fg_color="#FFFFFF",
        text_color="#000000",
        corner_radius=10
    )
    caja_inicio.pack(pady=6, padx=40)
    
    caja_inicio.insert("end", texto_pt1, "normal")
    caja_inicio.insert("end", texto_titulo, "titulo")
    caja_inicio.insert("end", texto_pt2, "normal")
    
    # Se aplican los tags internamente para evitar el error de CustomTkinter
    caja_inicio._textbox.tag_configure("normal", font=("Courier New", 12))
    caja_inicio._textbox.tag_configure("titulo", font=("Courier New", 16, "bold"))
    
    caja_inicio.configure(state="disabled")  # Evita que el usuario edite el contenido.
 
    ctk.CTkLabel(
        tab_inicio,
        text="Integrantes: Sofia Morales  |  Macarena Melin  |  Angel Obreque",
        font=ctk.CTkFont(size=12),
        text_color="#000000"
    ).pack(pady=(8, 18))
 
    # ── PESTANA 2: CALCULAR LIMITE ───────────────────────────────
    tab_limite.grid_columnconfigure(0, weight=2)  # Panel izquierdo  20%.
    tab_limite.grid_columnconfigure(1, weight=6)  # Panel central    60%.
    tab_limite.grid_columnconfigure(2, weight=2)  # Panel derecho    20%.
    tab_limite.grid_rowconfigure(0, weight=1)
 
    # ── PANEL IZQUIERDO: entradas y botones
    panel_izq = ctk.CTkFrame(tab_limite, corner_radius=8, fg_color="#F0E9ED")
    panel_izq.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=8)
 
    ctk.CTkLabel(
        panel_izq,
        text="Calcular Limite",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color="#2E0513"
    ).pack(pady=(18, 4))
 
    ctk.CTkLabel(
        panel_izq,
        text="MATE1133 - UCTemuco",
        font=ctk.CTkFont(size=11),
        text_color="#2E0513"
    ).pack(pady=(0, 16))
 
    ctk.CTkLabel(panel_izq, text="Funcion f(x):",
                 font=ctk.CTkFont(size=12), text_color="#2E0513").pack(anchor="w", padx=18)
    ctk.CTkLabel(
        panel_izq,
        text="Ej: sin(x)/x  |  (x**2-1)/(x-1)  |  1/x",
        font=ctk.CTkFont(size=10),
        text_color="#2E0513"
    ).pack(anchor="w", padx=18)
 
    campo_funcion = ctk.CTkEntry(
        panel_izq, placeholder_text="Escribe f(x) aqui", height=36,
        fg_color="#FFF5FB", text_color="#2E0513")
    campo_funcion.pack(padx=18, pady=(4, 12), fill="x")
 
    ctk.CTkLabel(panel_izq, text="Valor de c (x -> c):",
                 font=ctk.CTkFont(size=12), text_color="#2E0513").pack(anchor="w", padx=18)
    ctk.CTkLabel(
        panel_izq,
        text="Ej: 0  |  2  |  -3  |  oo  |  -oo",
        font=ctk.CTkFont(size=10),
        text_color="#2E0513"
    ).pack(anchor="w", padx=18)
 
    campo_c = ctk.CTkEntry(
        panel_izq, placeholder_text="Escribe c aqui", height=36,
        fg_color="#FFF5FB", text_color="#2E0513")
    campo_c.pack(padx=18, pady=(4, 16), fill="x")
 
    # Botones de accion creados con un ciclo for.
    botones = [
        ("Calcular y Graficar",    lambda: btn_calcular()),
        ("Limites Laterales",      lambda: btn_laterales()),
        ("Verificar Continuidad",  lambda: btn_continuidad()),
        ("Sintaxis",               lambda: mostrar_sintaxis(ventana)),
        ("Ejemplos",               lambda: mostrar_ejemplos(cuadro_der)),
        ("Limpiar",                lambda: btn_limpiar()),
        ("Exportar TXT",           lambda: exportar_resultado()),
    ]
    for texto_btn, cmd in botones:  # Crea todos los botones con un ciclo for.
        ctk.CTkButton(
            panel_izq, text=texto_btn, command=cmd, height=34,
            fg_color="#EA4383", text_color="#FFF5FB"
        ).pack(padx=18, pady=3, fill="x")
 
    # ── PANEL CENTRAL: grafico grande
    panel_centro = ctk.CTkFrame(tab_limite, corner_radius=8, fg_color="#F0E9ED")
    panel_centro.grid(row=0, column=1, sticky="nsew", padx=4, pady=8)
    panel_centro.grid_rowconfigure(0, weight=1)
    panel_centro.grid_columnconfigure(0, weight=1)
 
    fig, ax = plt.subplots(figsize=(7, 5))   # Figura de Matplotlib para el grafico.
    fig.patch.set_facecolor("#FFF5FB")
    ax.set_facecolor("#FFF5FB")
 
    canvas = FigureCanvasTkAgg(fig, master=panel_centro)  # Incrusta la figura.
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
 
    # Texto inicial del grafico.
    ax.text(0.5, 0.5, "Ingrese una funcion\ny presione Calcular",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=13, color="#2E0513")
    ax.axis("off")
    canvas.draw()
 
    # ── PANEL DERECHO: resultado y desarrollo matematico
    panel_der = ctk.CTkFrame(tab_limite, corner_radius=8, fg_color="#F0E9ED")
    panel_der.grid(row=0, column=2, sticky="nsew", padx=(4, 8), pady=8)
    panel_der.grid_rowconfigure(2, weight=1)
    panel_der.grid_columnconfigure(0, weight=1)
 
    ctk.CTkLabel(
        panel_der,
        text="Resultado",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#2E0513"
    ).grid(row=0, column=0, pady=(14, 2))
 
    etiqueta_res = ctk.CTkLabel(
        panel_der,
        text="lim x->c\nf(x) = ?",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="#2E0513",
        wraplength=200
    )
    etiqueta_res.grid(row=1, column=0, pady=(8, 4))
 
    cuadro_der = ctk.CTkTextbox(
        panel_der, font=ctk.CTkFont(family="Courier New", size=10),
        fg_color="#FFF5FB", text_color="#2E0513")
    cuadro_der.grid(row=2, column=0, padx=10, pady=(4, 10), sticky="nsew")
    cuadro_der.insert("end",
        "El desarrollo matematico\naparecera aqui.\n\n"
        "Ejemplos rapidos:\n"
        "  (x**2-4)/(x-2)   c=2\n"
        "  sin(x)/x          c=0\n"
        "  1/x               c=0\n"
        "  (2*x**2+1)/\n"
        "  (x**2+3)          c=oo")
    cuadro_der.configure(state="disabled")
 
    
    # FUNCIONES INTERNAS DE LOS BOTONES
    # Definidas dentro de construir_interfaz() para acceder
    # a los campos y paneles directamente sin parametros.
    
 
    def _leer_campos():
        # Lee y parsea los dos campos de entrada.
        texto_f = campo_funcion.get().strip()
        texto_c = campo_c.get().strip()
        if not texto_f or not texto_c:
            etiqueta_res.configure(
                text="Ingrese funcion\ny valor c", text_color="#2E0513")
            return None, None
        try:
            return parsear_funcion(texto_f), parsear_c(texto_c)
        except Exception as e:
            etiqueta_res.configure(text="Error de\nsintaxis", text_color="#2E0513")
            _escribir(
                f"Error al leer la expresion:\n{e}\n\n"
                "Usa ** para potencias (x**2).\n"
                "Presiona 'Sintaxis' para ver la guia.")
            return None, None
 
    def _escribir(texto):
        # Actualiza el cuadro de texto del panel derecho.
        # Habilita, borra, escribe y vuelve a bloquear.
        cuadro_der.configure(state="normal")
        cuadro_der.delete("1.0", "end")
        cuadro_der.insert("end", texto)
        cuadro_der.configure(state="disabled")
 
    def btn_calcular():
        # Calcula el limite, actualiza etiqueta, grafico y panel derecho.
        expr, c_val = _leer_campos()
        if expr is None:
            return
        try:
            resultado, lineas = calcular_limite(expr, c_val)  # Algoritmo principal.
            _escribir("\n".join(lineas))
            if resultado is not None and resultado != sp.nan:
                etiqueta_res.configure(
                    text=f"lim x\u2192{c_val}\nf(x) = {resultado}",
                    text_color="#2E0513")
            elif resultado == sp.nan:
                etiqueta_res.configure(
                    text="El limite\nNO EXISTE", text_color="#2E0513")
            else:
                etiqueta_res.configure(
                    text="No\ndeterminado", text_color="#2E0513")
            ax.axis("on")
            graficar_funcion(ax, expr, c_val, resultado)  # Graficacion.
            canvas.draw()                                  # Redibuja el canvas.
        except Exception as e:
            etiqueta_res.configure(text="Error de\ncalculo", text_color="#2E0513")
            _escribir(f"Ocurrio un error:\n{e}")
 
    def btn_laterales():
        # Calcula y muestra los dos limites laterales por separado.
        expr, c_val = _leer_campos()
        if expr is None:
            return
        lim_izq, p_izq = calcular_lateral_izquierdo(expr, c_val)
        lim_der, p_der = calcular_lateral_derecho(expr, c_val)
        lineas = ["LIMITES LATERALES", "•" * 38]
        lineas.extend(p_izq)
        lineas.extend(p_der)
        if lim_izq is not None and lim_der is not None:
            dif = sp.simplify(lim_izq - lim_der)
            if dif == 0 or abs(float(dif.evalf())) < 0.0001:
                lineas.append(f"\n  => EXISTE = {sp.N(lim_izq, 4)}")
                etiqueta_res.configure(
                    text=f"lim = {sp.N(lim_izq, 4)}", text_color="#2E0513")
            else:
                lineas.append(f"\n  => NO EXISTE")
                etiqueta_res.configure(text="NO EXISTE", text_color="#2E0513")
        _escribir("\n".join(lineas))
 
    def btn_continuidad():
        # Verifica las 3 condiciones de continuidad.
        expr, c_val = _leer_campos()
        if expr is None:
            return
        es_continua, lineas_cond = verificar_continuidad(expr, c_val)
        lineas = [
            "VERIFICACION DE CONTINUIDAD", "•" * 38,
            f"  f(x) = {expr}  en  x = {c_val}", "•" * 38
        ]
        lineas.extend(lineas_cond)
        lineas.append("•" * 38)
        if es_continua:
            lineas.append(f"  => CONTINUA en x={c_val}")
            etiqueta_res.configure(
                text=f"CONTINUA\nen x={c_val}", text_color="#2E0513")
        else:
            lineas.append(f"  => DISCONTINUA en x={c_val}")
            etiqueta_res.configure(
                text=f"DISCONTINUA\nen x={c_val}", text_color="#2E0513")
        _escribir("\n".join(lineas))
 
    def btn_limpiar():
        # Vacia todos los campos y el grafico.
        campo_funcion.delete(0, "end")
        campo_c.delete(0, "end")
        etiqueta_res.configure(
            text="lim x->c\nf(x) = ?", text_color="#2E0513")
        _escribir("Campos limpiados.\n\nIngresa una nueva funcion.")
        ax.clear()
        ax.set_facecolor("#FFF5FB")
        ax.figure.patch.set_facecolor("#FFF5FB")
        ax.text(0.5, 0.5, "Ingrese una funcion\ny presione Calcular",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=13, color="#2E0513")
        ax.axis("off")
        canvas.draw()
 
    ventana.report_callback_exception = _silenciar_errores
    try:
        ventana.mainloop()           # Inicia el bucle principal de la interfaz.
    finally:
        plt.close('all')             # Cierra las figuras de Matplotlib al salir.
 
 
# .
# MAIN: punto de entrada del programa  (linea 700)
# .
def main():
    print("Iniciando Analizador de Limites - MATE1133")
    construir_interfaz()             # Llama a la funcion que construye la interfaz.
 
 
if __name__ == "__main__":
    main()                           # Ejecuta solo si se corre directamente.
    
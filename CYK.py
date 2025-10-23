###############################################################################
# Joel Antonio Jaquez López - 23369 y Juan Francisco Martínez - 23611       #
# Proyecto 2 - Implementación de CYK (Cocke-Younger-Kasami)                 #
# con Forma Normal de Chomsky y programación dinámica                       #
###############################################################################

import time
import sys
from typing import Dict, Set, List, Tuple, Optional
from collections import defaultdict
from itertools import combinations
import copy


# Clase que representa una gramática libre de contexto
class Grammar:
    def __init__(self):
        self.productions = defaultdict(list)
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = 'S'
    
    # Agrega una producción a la gramática
    def add_production(self, lhs: str, rhs: List[str]):
        self.productions[lhs].append(rhs)
        self.non_terminals.add(lhs)

        for symbol in rhs:
            if symbol in ['e', 'ε', 'EPSILON', '']:
                continue     

            if symbol.islower() or symbol in ['a', 'the', '(', ')', '+', '*', '-', '/', 'id']:
                self.terminals.add(symbol)
            else:
                self.non_terminals.add(symbol)
    
    #Imprime la gramática de forma legible
    def print_grammar(self):
        for lhs in sorted(self.productions.keys()):
            for rhs in self.productions[lhs]:
                print(f"{lhs} -> {' '.join(rhs)}")

# Convierte una gramatica CFG a Forma Normal de Chomsky
class CNFConverter:
    def __init__(self, grammar: Grammar):
        self.grammar = copy.deepcopy(grammar)
        self.new_non_terminal_counter = 0
    
    #Verifica si la gramática ya cumple con las reglas de CNF
    def is_in_cnf(self) -> bool:
        for lhs, productions in self.grammar.productions.items():
            for rhs in productions:
                # No puede haber producciones de más de 2 símbolos
                if len(rhs) > 2:
                    return False
                
                if len(rhs) == 1:
                    if rhs[0] not in self.grammar.terminals:
                        pass
                
                # Si tiene 2 símbolos, ambos deben ser no-terminales
                if len(rhs) == 2:
                    if rhs[0] in self.grammar.terminals or rhs[1] in self.grammar.terminals:
                        return False
        return True
    
    #Convierte la gramática a CNF ejecutando los 5 pasos
    def convert_to_cnf(self) -> Grammar:
        print("\nIniciando conversión a Forma Normal de Chomsky (CNF)...")
        print("=" * 70)
        
        # Paso 1: Eliminar símbolos inútiles
        print("\nPASO 1: Eliminando símbolos inútiles (Useless)...")
        print("-" * 70)
        initial_non_terminals = len(self.grammar.non_terminals)
        initial_productions = sum(len(prods) for prods in self.grammar.productions.values())
        
        self._eliminate_useless_symbols()
        
        final_non_terminals = len(self.grammar.non_terminals)
        final_productions = sum(len(prods) for prods in self.grammar.productions.values())
        
        print(f"   No-terminales: {initial_non_terminals} → {final_non_terminals}")
        print(f"   Producciones: {initial_productions} → {final_productions}")
        
        if initial_non_terminals == final_non_terminals:
            print("   ✓ No se encontraron símbolos inútiles")
        else:
            print(f"   ✓ Se eliminaron {initial_non_terminals - final_non_terminals} símbolos")
        
        print("\n   Gramática después del Paso 1:")
        self._print_grammar_compact()
        
        # Paso 2: Eliminar producciones epsilon (anulables)
        print("\nPASO 2: Eliminando producciones epsilon/anulables (ε)...")
        print("-" * 70)
        initial_productions = sum(len(prods) for prods in self.grammar.productions.values())
        
        epsilon_found = self._eliminate_epsilon_productions()
        
        final_productions = sum(len(prods) for prods in self.grammar.productions.values())
        
        if not epsilon_found:
            print("   ✓ No se encontraron producciones epsilon")
        else:
            print(f"   ✓ Producciones epsilon eliminadas")
            print(f"   Producciones: {initial_productions} → {final_productions}")
        
        print("\n   Gramática después del Paso 2:")
        self._print_grammar_compact()
        
        # Paso 3: Eliminar producciones unitarias
        print("\nPASO 3: Eliminando producciones unitarias (A -> B)...")
        print("-" * 70)
        initial_productions = sum(len(prods) for prods in self.grammar.productions.values())
        
        unit_count = self._eliminate_unit_productions()
        
        final_productions = sum(len(prods) for prods in self.grammar.productions.values())
        
        if unit_count == 0:
            print("   ✓ No se encontraron producciones unitarias")
        else:
            print(f"   ✓ Se eliminaron {unit_count} producciones unitarias")
            print(f"   Producciones: {initial_productions} → {final_productions}")
        
        print("\n   Gramática después del Paso 3:")
        self._print_grammar_compact()
        
        # Paso 4: Reemplazar terminales en producciones binarias
        print("\nPASO 4: Reemplazando terminales en producciones binarias...")
        print("-" * 70)
        
        terminals_replaced = self._replace_terminals_in_long_productions()
        
        if terminals_replaced == 0:
            print("   ✓ No se requirieron reemplazos de terminales")
        else:
            print(f"   ✓ Se crearon {terminals_replaced} nuevos no-terminales para terminales")
        
        print("\n   Gramática después del Paso 4:")
        self._print_grammar_compact()
        
        # Paso 5: Romper producciones largas
        print("\nPASO 5: Rompiendo producciones largas (A -> BCD)...")
        print("-" * 70)
        
        long_broken = self._break_long_productions()
        
        if long_broken == 0:
            print("   ✓ No se encontraron producciones largas")
        else:
            print(f"   ✓ Se rompieron {long_broken} producciones largas")
        
        print("\n   Gramática después del Paso 5:")
        self._print_grammar_compact()
        
        print("\n" + "=" * 70)
        print("Conversión a CNF completada exitosamente")
        print("=" * 70)
        
        return self.grammar
    
    #Imprime la gramática de forma compacta
    def _print_grammar_compact(self):
        for lhs in sorted(self.grammar.productions.keys()):
            alternatives = []
            for rhs in self.grammar.productions[lhs]:
                alternatives.append(' '.join(rhs) if rhs else 'ε')
            print(f"   {lhs} -> {' | '.join(alternatives)}")
    
    #Genera un nuevo no-terminal único
    def _get_new_non_terminal(self) -> str:
        self.new_non_terminal_counter += 1
        return f"X{self.new_non_terminal_counter}"
    
    # Elimina símbolos inútiles en dos pasos:
    def _eliminate_useless_symbols(self):
        # Paso 1: Encontrar símbolos productivos (que generan terminales)
        generating = set()
        changed = True
        
        while changed:
            changed = False
            for lhs, productions in list(self.grammar.productions.items()):
                if lhs in generating:
                    continue
                    
                for rhs in productions:
                    # Reconoce epsilon como productivo
                    if len(rhs) == 0 or (len(rhs) == 1 and rhs[0] in ['e', 'ε', 'EPSILON', '']):
                        # Producción epsilon: el símbolo es productivo
                        generating.add(lhs)
                        changed = True
                        break

                    # Verifica símbolos normales
                    elif all(s in self.grammar.terminals or s in generating for s in rhs):
                        generating.add(lhs)
                        changed = True
                        break
        
        # Eliminar producciones con símbolos no productivos
        new_productions = defaultdict(list)
        for lhs in generating:
            if lhs in self.grammar.productions:
                for rhs in self.grammar.productions[lhs]:
                    # Mantener producciones epsilon
                    if len(rhs) == 1 and rhs[0] in ['e', 'ε', 'EPSILON', '']:
                        new_productions[lhs].append(rhs)
                    # Mantener producciones normales productivas
                    elif all(s in self.grammar.terminals or s in generating for s in rhs):
                        new_productions[lhs].append(rhs)
        
        self.grammar.productions = new_productions
        
        # Paso 2: Encontrar símbolos alcanzables desde S
        reachable = {self.grammar.start_symbol}
        changed = True
        
        while changed:
            changed = False
            for lhs in list(reachable):
                if lhs in self.grammar.productions:
                    for rhs in self.grammar.productions[lhs]:
                        for symbol in rhs:
                            if symbol in self.grammar.non_terminals and symbol not in reachable:
                                reachable.add(symbol)
                                changed = True
        
        # Mantener solo símbolos alcanzables
        final_productions = defaultdict(list)
        for lhs in reachable:
            if lhs in self.grammar.productions:
                final_productions[lhs] = self.grammar.productions[lhs]
        
        self.grammar.productions = final_productions
        self.grammar.non_terminals = reachable & self.grammar.non_terminals
    
    #Elimina producciones anulables (A -> ε)
    def _eliminate_epsilon_productions(self):
        # Encontrar símbolos anulables (que pueden derivar a epsilon)
        nullable = set()
        changed = True
        
        while changed:
            changed = False
            for lhs, productions in self.grammar.productions.items():
                if lhs in nullable:
                    continue
                    
                for rhs in productions:
                    # Producción epsilon directa (vacía o 'e' o 'EPSILON')
                    if len(rhs) == 0 or (len(rhs) == 1 and rhs[0] in ['e', 'ε', 'EPSILON', '']):
                        nullable.add(lhs)
                        changed = True
                        break
                    # Todos los símbolos son no-terminales y todos son anulables
                    elif len(rhs) > 0 and all(s in self.grammar.non_terminals for s in rhs) and all(s in nullable for s in rhs):
                        nullable.add(lhs)
                        changed = True
                        break
        
        # Si no hay símbolos anulables, no hay nada que hacer
        if not nullable:
            return False
        
        # Generar nuevas producciones sin epsilon
        new_productions = defaultdict(list)
        
        for lhs, productions in self.grammar.productions.items():
            for rhs in productions:
                # Ignorar producciones epsilon
                if len(rhs) == 0 or (len(rhs) == 1 and rhs[0] in ['e', 'ε', 'EPSILON', '']):
                    continue
                
                # Generar todas las combinaciones eliminando símbolos anulables
                nullable_positions = [i for i, s in enumerate(rhs) if s in nullable]
                
                # Si no hay símbolos anulables, agregamos la producción tal cual
                if not nullable_positions:
                    new_productions[lhs].append(rhs)
                else:
                    # Generar todas las combinaciones (2^n)
                    for r in range(len(nullable_positions) + 1):
                        for positions_to_remove in combinations(nullable_positions, r):
                            new_rhs = [rhs[i] for i in range(len(rhs)) if i not in positions_to_remove]
                            if new_rhs and new_rhs not in new_productions[lhs]:
                                new_productions[lhs].append(new_rhs)
        
        self.grammar.productions = new_productions
        return True

    # Elimina producciones unitarias (A -> B donde B es no-terminal)
    def _eliminate_unit_productions(self):
        # Contar producciones unitarias iniciales
        unit_count = 0
        for lhs, productions in self.grammar.productions.items():
            for rhs in productions:
                if len(rhs) == 1 and rhs[0] in self.grammar.non_terminals:
                    unit_count += 1
        
        if unit_count == 0:
            return 0
        
        # Encontrar clausura transitiva de producciones unitarias
        unit_pairs = defaultdict(set)
        
        # Inicializar con pares reflexivos
        for nt in self.grammar.non_terminals:
            unit_pairs[nt].add(nt)
        
        # Encontrar clausura transitiva
        changed = True
        while changed:
            changed = False
            for lhs, productions in self.grammar.productions.items():
                for rhs in productions:
                    if len(rhs) == 1 and rhs[0] in self.grammar.non_terminals:
                        B = rhs[0]
                        for C in unit_pairs[B]:
                            if C not in unit_pairs[lhs]:
                                unit_pairs[lhs].add(C)
                                changed = True
        
        # Generar nuevas producciones sin unitarias
        new_productions = defaultdict(list)
        
        for A in self.grammar.non_terminals:
            for B in unit_pairs[A]:
                if B in self.grammar.productions:
                    for rhs in self.grammar.productions[B]:
                        # Solo agregar si NO es producción unitaria
                        if not (len(rhs) == 1 and rhs[0] in self.grammar.non_terminals):
                            if rhs not in new_productions[A]:
                                new_productions[A].append(rhs)
        
        self.grammar.productions = new_productions
        return unit_count
    
    # Reemplaza terminales en producciones binarias
    def _replace_terminals_in_long_productions(self):
        terminal_to_nt = {}
        new_productions = defaultdict(list)
        terminals_replaced = 0

        for lhs, productions in self.grammar.productions.items():
            for rhs in productions:
                if len(rhs) == 1:
                    # Producción A -> a (ya está en CNF)
                    new_productions[lhs].append(rhs)
                
                elif len(rhs) == 2:
                    # Revisamos si hay terminales que necesiten reemplazo
                    new_rhs = []
                    for symbol in rhs:
                        if symbol in self.grammar.terminals:
                            # Creamos un nuevo no-terminal para este terminal
                            if symbol not in terminal_to_nt:
                                new_nt = self._get_new_non_terminal()
                                terminal_to_nt[symbol] = new_nt
                                new_productions[new_nt].append([symbol])
                                self.grammar.non_terminals.add(new_nt)
                                terminals_replaced += 1
                            new_rhs.append(terminal_to_nt[symbol])
                        else:
                            new_rhs.append(symbol)
                    new_productions[lhs].append(new_rhs)
                else:
                    # Producción larga, la manejamos en el siguiente paso
                    new_productions[lhs].append(rhs)
        
        self.grammar.productions = new_productions
        return terminals_replaced
    
    # Rompe producciones largas en producciones binarias
    def _break_long_productions(self):
        new_productions = defaultdict(list)
        long_count = 0

        for lhs, productions in self.grammar.productions.items():
            for rhs in productions:
                if len(rhs) <= 2:
                    new_productions[lhs].append(rhs)
                else:
                    # Romper producción larga
                    long_count += 1
                    current_lhs = lhs
                    for i in range(len(rhs) - 2):
                        new_nt = self._get_new_non_terminal()
                        new_productions[current_lhs].append([rhs[i], new_nt])
                        self.grammar.non_terminals.add(new_nt)
                        current_lhs = new_nt
                    
                    # Última producción
                    new_productions[current_lhs].append([rhs[-2], rhs[-1]])
        
        self.grammar.productions = new_productions
        return long_count



# Clase que representa un nodo en el árbol de parsing
class ParseTreeNode:
    def __init__(self, symbol: str, children: List['ParseTreeNode'] = None):
        self.symbol = symbol
        self.children = children or []

    # Imprime el árbol de forma visual
    def print_tree(self, level=0, prefix=""):
        indent = "  " * level
        print(f"{indent}{prefix}{self.symbol}")
        for i, child in enumerate(self.children):
            is_last = i == len(self.children) - 1
            child_prefix = "└─ " if is_last else "├─ "
            child.print_tree(level + 1, child_prefix)
    
    #Convierte el árbol a string
    def to_string_tree(self, level=0) -> str:
        indent = "  " * level
        result = f"{indent}{self.symbol}\n"
        for child in self.children:
            result += child.to_string_tree(level + 1)
        return result


# Implementa el algoritmo CYK con programación dinámica
class CYKParser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.table = None
        self.back_pointer = None
    
    # Ejecuta el algoritmo CYK usando programación dinámica
    def parse(self, sentence: str) -> Tuple[bool, Optional[ParseTreeNode], float]:
        start_time = time.time()
        words = sentence.lower().split()
        n = len(words)

        # Si no hay palabras, no hay nada que analizar
        if n == 0:
            return False, None, 0.0
        
        # Tabla de programación dinámica
        # table[i][j] guarda los símbolos que pueden generar la subcadena
        self.table = [[set() for _ in range(n)] for _ in range(n)]
        
        # Back pointers para reconstruir el árbol
        self.back_pointer = [[defaultdict(list) for _ in range(n)] for _ in range(n)]

        # Paso 1: Llenar la diagonal (palabras individuales)
        for i in range(n):
            word = words[i]
            for lhs, productions in self.grammar.productions.items():
                for rhs in productions:
                    if len(rhs) == 1 and rhs[0] == word:
                        self.table[i][0].add(lhs)
                        self.back_pointer[i][0][lhs].append(('terminal', word, None))
        
        # Paso 2: Llenar la tabla para subcadenas más largas
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = length - 1

                # Probar todas las divisiones posibles
                for k in range(length - 1):
                    left_symbols = self.table[i][k]
                    right_symbols = self.table[i + k + 1][j - k - 1]

                    # Buscar reglas que combinen estas partes
                    for lhs, productions in self.grammar.productions.items():
                        for rhs in productions:
                            if len(rhs) == 2:
                                B, C = rhs
                                if B in left_symbols and C in right_symbols:
                                    self.table[i][j].add(lhs)
                                    self.back_pointer[i][j][lhs].append((k, B, C))
        
        # Verificar si se puede formar el símbolo inicial
        accepted = self.grammar.start_symbol in self.table[0][n - 1]

        end_time = time.time()
        execution_time = end_time - start_time

        # Construir el árbol si fue aceptada
        parse_tree = None
        if accepted:
            parse_tree = self._build_parse_tree(0, n - 1, self.grammar.start_symbol, words)
        
        return accepted, parse_tree, execution_time

    # Construye el árbol recursivamente
    def _build_parse_tree(self, i: int, j: int, symbol: str, words: List[str]) -> ParseTreeNode:
        node = ParseTreeNode(symbol)

        # Caso base: llegamos a una palabra
        if j == 0:
            pointers = self.back_pointer[i][j].get(symbol, [])
            if pointers:
                pointer = pointers[0]
                if pointer[0] == 'terminal':
                    terminal_node = ParseTreeNode(pointer[1])
                    node.children.append(terminal_node)
        else:
            # Caso recursivo: construir subárboles
            pointers = self.back_pointer[i][j].get(symbol, [])
            if pointers:
                k, B, C = pointers[0]

                left_child = self._build_parse_tree(i, k, B, words)
                node.children.append(left_child)

                right_child = self._build_parse_tree(i + k + 1, j - k - 1, C, words)
                node.children.append(right_child)
        
        return node

# Lee una gramática desde un archivo de texto
def load_grammar_from_file(filename: str) -> Grammar:

    g = Grammar()
    first_non_terminal = None
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Ignorar comentarios y líneas vacías
                if not line or line.startswith('#'):
                    continue
                
                # Debe tener formato: LHS -> RHS
                if '->' not in line:
                    print(f"⚠ Línea {line_num} ignorada (formato inválido): {line}")
                    continue
                
                parts = line.split('->')
                if len(parts) != 2:
                    print(f"⚠ Línea {line_num} ignorada (formato inválido): {line}")
                    continue
                
                lhs = parts[0].strip()
                rhs_full = parts[1].strip()
                
                # Guardar el primer no-terminal como símbolo inicial
                if first_non_terminal is None:
                    first_non_terminal = lhs
                
                # Separar alternativas (|)
                alternatives = [alt.strip() for alt in rhs_full.split('|')]
                
                for alt in alternatives:
                    if alt and alt not in ['e', 'ε', 'EPSILON']:  # Ignorar epsilon explícito
                        symbols = alt.split()
                        g.add_production(lhs, symbols)
                    elif alt in ['e', 'ε', 'EPSILON']:
                        # Producción epsilon
                        g.add_production(lhs, [alt])
        
        # Establecer el símbolo inicial
        if first_non_terminal:
            g.start_symbol = first_non_terminal
        
        print(f"✓ Gramática cargada desde '{filename}'")
        print(f"  Símbolo inicial: {g.start_symbol}")
        print(f"  No-terminales: {len(g.non_terminals)}")
        print(f"  Terminales: {len(g.terminals)}")
        print(f"  Producciones: {sum(len(prods) for prods in g.productions.values())}")
        
        return g
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{filename}'")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        sys.exit(1)

# Modo interactivo para ingresar frases
def interactive_mode(parser: CYKParser):
    print("\n" + "=" * 70)
    print("MODO INTERACTIVO - INGRESO DE FRASES")
    print("=" * 70)
    print("\nInstrucciones:")
    print("  • Ingrese frases para analizar")
    print("  • Escriba 'salir' para terminar")
    print("  • Escriba 'ayuda' para ver comandos")

    while True:
        print("\n" + "-" * 70)
        user_input = input("Ingrese una frase: ").strip()

        if user_input.lower() in ['salir', 'exit', 'quit', 'q']:
            print("\n¡Gracias por usar el parser CYK!")
            break

        if user_input.lower() in ['ayuda', 'help', 'h']:
            print("\nCOMANDOS DISPONIBLES:")
            print("-" * 70)
            print("  salir   - Terminar el programa")
            print("  ayuda   - Mostrar esta ayuda")
            continue

        if not user_input:
            print("⚠ Por favor ingrese una frase válida")
            continue

        # Analizar la frase
        print(f"\nANALIZANDO: \"{user_input}\"")
        print("-" * 70)

        accepted, parse_tree, exec_time = parser.parse(user_input)

        if accepted:
            print("\nRESULTADO: SÍ")
            print(f"   La frase PERTENECE al lenguaje")
            print(f"\nTIEMPO: {exec_time:.6f} segundos")

            if parse_tree:
                print("\nÁRBOL DE PARSING:")
                print("-" * 70)
                parse_tree.print_tree()
        else:
            print("\nRESULTADO: NO")
            print(f"   La frase NO PERTENECE al lenguaje")
            print(f"\n⏱  TIEMPO: {exec_time:.6f} segundos")


# Función principal
def main():
    print("=" * 70)
    print("  PROYECTO 2: ALGORITMO CYK - PARSER DE GRAMÁTICAS CFG")
    print("  Teoría de la Computación 2025")
    print("=" * 70)

    # Verificar argumentos de línea de comandos
    if len(sys.argv) < 2:
        print("\nError: Debe especificar un archivo de gramática")
        print("\nUso:")
        print(f"  python {sys.argv[0]} <archivo_gramatica.txt>")
        print("\nEjemplo:")
        print(f"  python {sys.argv[0]} grammar.txt")
        sys.exit(1)
    
    grammar_file = sys.argv[1]

    # Cargar gramática desde archivo
    print(f"\n1. CARGANDO GRAMÁTICA DESDE: {grammar_file}")
    print("-" * 70)
    original_grammar = load_grammar_from_file(grammar_file)
    print("\nGramática original:")
    original_grammar.print_grammar()

    # Convertir a CNF
    converter = CNFConverter(original_grammar)
    cnf_grammar = converter.convert_to_cnf()
    print("\n2. GRAMÁTICA EN CNF:")
    print("-" * 70)
    cnf_grammar.print_grammar()

    # Crear parser CYK
    parser = CYKParser(cnf_grammar)

    # Menú principal
    while True:
        print("\n" + "=" * 70)
        print("MENÚ PRINCIPAL")
        print("=" * 70)
        print("1. Modo interactivo (ingresar frases manualmente)")
        print("2. Ingresar una frase directamente")
        print("3. Salir")

        opcion = input("\nSeleccione una opción (1-3): ").strip()

        if opcion == '1':
            interactive_mode(parser)
        
        elif opcion == '2':
            print("\n" + "-" * 70)
            frase = input("Ingrese la frase a analizar: ").strip()

            if not frase:
                print("⚠ Frase vacía")
                continue

            print(f"\nANALIZANDO: \"{frase}\"")
            print("-" * 70)

            accepted, parse_tree, exec_time = parser.parse(frase)

            if accepted:
                print("\nRESULTADO: SÍ - La frase pertenece al lenguaje")
                print(f"TIEMPO: {exec_time:.6f} segundos")
                if parse_tree:
                    print("\nÁRBOL DE PARSING:")
                    parse_tree.print_tree()
            else:
                print("\nRESULTADO: NO - La frase NO pertenece al lenguaje")
                print(f"TIEMPO: {exec_time:.6f} segundos")
        
        elif opcion == '3':
            print("\n¡Gracias por usar el parser CYK!")
            print("=" * 70)
            break
        
        else:
            print("\n⚠ Opción inválida. Por favor seleccione 1, 2 o 3.")


if __name__ == "__main__":
    main()



                

                                    
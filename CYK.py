#################################################################################################################
# Joel Antonio Jaquez López - 23369  y Juan Francisco Martínez - 2361                                           #
# Proyecto 2 - Implementacion de CYK (Cocke-Younger-Kasami) con Forma Normal de Chomsky y programación dinámica #                 
#################################################################################################################

import time
from typing import Dict, Set, List, Tuple, Optional
from collections import defaultdict
import copy

# Clase que representa una gramática libre de contexto
class Grammar:
    def __init__ (self):
        self.productions = defaultdict(list)
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = 'S'
    
    # Funcion para agregar una produccion a la gramatica
    def add_production(self, lhs: str, rhs: List[str]):
        self.productions[lhs].append(rhs)
        self.non_terminals.add(lhs)

        for symbol in rhs:
            if symbol.islower() or symbol in ['a', 'the']:
                self.terminals.add(symbol)
            else:
                self.non_terminals.add(symbol)
    
    # Funcion para imprimir la gramatica
    def print_grammar(self):
        for lhs in sorted(self.productions.keys()):
            for rhs in self.productions[lhs]:
                print(f"{lhs} -> {' '.join(rhs)}")

# Convierte una gramatica CFG a Forma Normal de Chomsky
class CNFConverter:
    def __init__(self, grammar: Grammar):
        self.grammar = copy.deepcopy(grammar)
        self.new_non_terminal_counter = 0
    
    # Verifica si la gramatica esta en CNF
    def is_in_cnf(self) -> bool:
        for lhs, productions in self.grammar.productions.items():
            for rhs in productions:
                if len(rhs) > 2:
                    return False
                
                if len(rhs) == 1:
                    if rhs[0] not in self.grammar.terminals:
                        pass
                
                if len(rhs) == 2:
                    if rhs[0] in self.grammar.terminals or rhs[1] in self.grammar.terminals:
                        return False
        return True
    
    # Convierte la gramatica a CNF 
    def convert_to_cnf(self) -> Grammar:
        if self.is_in_cnf():
            print("La gramatica ya esta en forma normal de Chomsky.")
            return self.grammar
        
        print("Convirtiendo la gramatica a CNF...")
        self._replace_terminals_in_long_productions()
        self._break_long_productions()
        return self.grammar
    
    # Funcion para generar nuevos no terminales
    def _get_new_non_terminal(self) -> str:
        self.new_non_terminal_counter += 1
        return f"X{self.new_non_terminal_counter}"
    
    # Funcion para reemplazar terminales en producciones largas
    def _replace_terminals_in_long_productions(self):
        terminal_to_nt = {}
        new_productions = defaultdict(list)

        for lhs, productions in self.grammar.productions.items():
            for rhs in productions:
                if len(rhs) == 1:
                    # Produccion A -> a (ya esta en CNF)
                    new_productions[lhs].append(rhs)
                
                elif len(rhs) == 2:
                    # Produccion A -> BC (ya esta en CNF)
                    new_rhs = []
                    for symbol in rhs:
                        if symbol in self.grammar.terminals:
                            if symbol not in terminal_to_nt:
                                new_nt = self._get_new_non_terminal()
                                terminal_to_nt[symbol] = new_nt
                                new_productions[new_nt].append([symbol])
                                self.grammar.non_terminals.add(new_nt)
                            new_rhs.append(terminal_to_nt[symbol])
                        else:
                            new_rhs.append(symbol)
                    new_productions[lhs].append(new_rhs)
                else:
                    # Produccion largar (>2), la manejaremos despues
                    new_productions[lhs].append(rhs)
        self.grammar.productions = new_productions
    
    # Paso 2: Romper producciones de longitud mayor a 2 en producciones binarias
    def _break_long_productions(self):
        new_productions = defaultdict(list)

        for lhs, productions in self.grammar.productions.items():
            for rhs in productions:
                if len(rhs) <= 2:
                    new_productions[lhs].append(rhs)
                else:
                    # Romper produccion larga
                    current_lhs = lhs
                    for i in range(len(rhs) - 2):
                        new_nt = self._get_new_non_terminal()
                        new_productions[current_lhs].append([rhs[i], new_nt])
                        self.grammar.non_terminals.add(new_nt)
                        current_lhs = new_nt
                    
                    # Ultima produccion
                    new_productions[current_lhs].append([rhs[-2], rhs[-1]])
        self.grammar.productions = new_productions

# Clase que representa un nodo en el árbol de parsing
class ParseTreeNode:
    def __init__(self, symbol: str, children: List['ParseTreeNode'] = None):
        self.symbol = symbol
        self.children = children or []

    # Imprime el arbol de forma visual
    def print_tree(self, level=0, prefix=""):
        indent = "  " * level
        print(f"{indent}{prefix}{self.symbol}")
        for i, child in enumerate(self.children):
            is_last = i == len(self.children) - 1
            child_prefix = "└─ " if is_last else "├─ "
            child.print_tree(level + 1, child_prefix)
    
    # Funcion para representar el arbol como string
    def to_string_tree(self, level=0) -> str:
        indent = "  " * level
        result = f"{indent}{self.symbol}\n"
        for child in self.children:
            result += child.to_string_tree(level + 1)
        return result

# Implementa el algoritmo CYK para el parsing de gramaticas en CNF
class CYKParser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.table = None
        self.back_pointer = None
    
    # Funcion que ejecuta el algoritmo de CYK con programacion dinamica
    def parse(self, sentence: str) -> Tuple[bool, Optional[ParseTreeNode], float]:
        start_time = time.time()
        words = sentence.lower().split()
        n = len(words)

        # Validar entrada vacia
        if n == 0:
            return False, None, 0.0
        
        # Inicializar la tabla CYK
        self.table = [[set() for _ in range(n)] for i in range(n)]

        # Guardar todas las derivaciones posibles
        self.back_pointer = [[defaultdict(list) for _ in range(n)] for _ in range(n)]

        # Paso 1: Llenar la tabla para las producciones de longitud 1
        for i in range(n):
            word = words[i]
            for lhs, productions in self.grammar.productions.items():
                for rhs in productions:
                    if len(rhs) == 1 and rhs[0] == word:
                        self.table[i][0].add(lhs)
                        # Para terminales, guardamos el simbolo terminal
                        self.back_pointer[i][0][lhs].append(('terminal', word, None))

        # Paso 2: Llenar la tabla para producciones de longitud > 1
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = length - 1

                # Probar todas las particiones posibles
                for k in range(length - 1):
                    left_symbols = self.table[i][k]
                    right_symbols = self.table[i + k + 1][j - k - 1]

                    # Buscar producciones A -> BC
                    for lhs, productions in self.grammar.productions.items():
                        for rhs in productions:
                            if len(rhs) == 2:
                                B, C = rhs
                                if B in left_symbols and C in right_symbols:
                                    self.table[i][j].add(lhs)
                                    self.back_pointer[i][j][lhs].append((k, B, C))
        
        accepted = self.grammar.start_symbol in self.table[0][n - 1]

        end_time = time.time()
        execution_time = end_time - start_time

        # Contruir el arbol de parsing si la cadena es aceptada
        parse_tree = None
        if accepted:
            parse_tree = self._build_parse_tree(0, n - 1, self.grammar.start_symbol, words)
        return accepted, parse_tree, execution_time

    def _build_parse_tree(self, i: int, j: int, symbol: str, words: List[str]) -> ParseTreeNode:

        node = ParseTreeNode(symbol)

        if j == 0:
            pointers = self.back_pointer[i][j].get(symbol, [])
            if pointers:
                pointer = pointers[0]
                
                if pointer[0] == 'terminal':
                    terminal_node = ParseTreeNode(pointer[1])
                    node.children.append(terminal_node)
        else:
            pointers = self.back_pointer[i][j].get(symbol, [])
            if pointers:
                K, B, C = pointers[0]

                left_child = self._build_parse_tree(i, K, B, words)
                node.children.append(left_child)

                right_child = self._build_parse_tree(i + K + 1, j - K - 1, C, words)
                node.children.append(right_child)
        return node

    # Imprime la tabla CYK
    def print_table(self, words: List[str]):
        n = len(words)
        print("\nTabla CYK:")
        print("----------------------------------")
        for j in range(n - 1, -1, -1):
            for i in range(n - j):
                symbols = self.table[i][j]
                print(f"[{i},{j}]: {symbols if symbols else '∅'}", end="  ")
            print()
        print("----------------------------------")

# Función para crear la gramática en inglés
def create_english_grammar() -> Grammar:
    g = Grammar()
    
    # S -> NP VP
    g.add_production('S', ['NP', 'VP'])
    
    # VP -> VP PP
    g.add_production('VP', ['VP', 'PP'])
    
    # VP -> V NP
    g.add_production('VP', ['V', 'NP'])
    
    # VP -> cooks | drinks | eats | cuts
    g.add_production('VP', ['cooks'])
    g.add_production('VP', ['drinks'])
    g.add_production('VP', ['eats'])
    g.add_production('VP', ['cuts'])
    
    # PP -> P NP
    g.add_production('PP', ['P', 'NP'])
        
    # NP -> Det N
    g.add_production('NP', ['Det', 'N'])
        
    # NP -> he | she
    g.add_production('NP', ['he'])
    g.add_production('NP', ['she'])
        
    # V -> cooks | drinks | eats | cuts
    g.add_production('V', ['cooks'])
    g.add_production('V', ['drinks'])
    g.add_production('V', ['eats'])
    g.add_production('V', ['cuts'])
        
    # P -> in | with
    g.add_production('P', ['in'])
    g.add_production('P', ['with'])
        
    # N -> cat | dog | beer | cake | juice | meat | soup | fork | knife | oven | spoon
    g.add_production('N', ['cat'])
    g.add_production('N', ['dog'])
    g.add_production('N', ['beer'])
    g.add_production('N', ['cake'])
    g.add_production('N', ['juice'])
    g.add_production('N', ['meat'])
    g.add_production('N', ['soup'])
    g.add_production('N', ['fork'])
    g.add_production('N', ['knife'])
    g.add_production('N', ['oven'])
    g.add_production('N', ['spoon'])
        
    # Det -> a | the
    g.add_production('Det', ['a'])
    g.add_production('Det', ['the'])
        
    return g

# Función para el modo interactivo
def interactive_mode(parser: CYKParser):
    print("======================================")
    print("MODO INTERACTIVO - INGRESO DE FRASES")
    print("======================================")
    print("Instrucciones: ")
    print("  • Ingrese frases en inglés usando el vocabulario de la gramática")
    print("  • Escriba 'salir' para terminar")
    print("  • Escriba 'ayuda' para ver el vocabulario disponible")
    print("  • Escriba 'ejemplos' para ver ejemplos válidos")

    while True:
        print("-----------------------")
        user_input = input("Ingrese una frase: ").strip()

        if user_input.lower() in ['salir', 'exit', 'quit', 'q']:
            print("Graciar por usar el parser CYK")
            break

        if user_input.lower() in ['ayuda', 'help', 'h']:
            print("\n Vocabulario disponible: ")
            print("====================================")
            print("Pronombres: he, she")
            print("Verbos: cooks, drinks, eats, cuts")
            print("Determinantes: a, the")
            print("Sustantivos: cat, dog, beer, cake, juice, meat, soup,")
            print("             fork, knife, oven, spoon")
            print("Preposiciones: in, with")
            print("\n Las frases deben seguir la estructura:")
            print("   [Pronombre/Det+Sustantivo] [Verbo] [Det+Sustantivo] [Prep+Det+Sustantivo]")
            continue

        if user_input.lower() in ['ejemplos', 'examples', 'e']:
            print("\n✓ EJEMPLOS DE FRASES VÁLIDAS:")
            print("--------------------------------")
            print("  • she eats a cake")
            print("  • the cat drinks the beer")
            print("  • he cooks the meat with a fork")
            print("  • she cuts a cake with a knife")
            print("  • the dog eats the soup in the oven")
            continue

        if not user_input:
            print("Por favor ingrese una frase válida.")
            continue

        print("\n Analizando frase: \"" + user_input + "\"")
        print("-------------------------------------------")

        accepted, parse_tree, exec_time = parser.parse(user_input)

        if accepted:
            print("Resultado: SI")
            print(f"La frase pertenece al lenguaje generado por la gramática.")
            print(f"\n Tiempo de ejecución: {exec_time:.6f} segundos")

            if parse_tree:
                print("\n ÁRBOL DE PARSING ")
                print("---------------------")
                parse_tree.print_tree()
        else:
            print("Resultado: NO")
            print(f"La frase NO pertenece al lenguaje generado por la gramática.")
            print(f"\n Tiempo de ejecución: {exec_time:.6f} segundos")
            print("-----------------------")

# Función principal para ejecutar el programa
def main():
    print("======================================")
    print("Proyecto 2 Teoria de la Computacion - Algoritmo CYK")
    print("======================================")

    print("\n 1. Gramatica Original (CFG): ")
    original_grammar = create_english_grammar()
    original_grammar.print_grammar()

    print("\n 2. Convertir a Forma Normal de Chomsky (CNF): ")
    converter = CNFConverter(original_grammar)
    cnf_grammar = converter.convert_to_cnf()
    print("\n Gramatica en CNF: ")
    cnf_grammar.print_grammar()

    # Crear el parser CYK
    parser = CYKParser(cnf_grammar)

    while True:
        print("=======================================")
        print("Menu Principal")
        print("=======================================")
        print("1. Modo interactivo - Ingresar frases manualmente")
        print("2. Ingresar una frase directamente")
        print("3. Salir")

        opcion = input("Seleccione una opción (1-4): ").strip()

        if opcion == '1':
            interactive_mode(parser)
        elif opcion == '2':
            print("=====================")
            frase = input("Ingrese una frase en inglés para analizar: ").strip()

            if not frase:
                print("Frase vacia")
                continue

            print(f"\n Analizando: \"{frase}\"")
            print("============================")

            accepted, parse_tree, exec_time = parser.parse(frase)

            if accepted:
                print("Resultado: SI")
                print(f"La frase pertenece al lenguaje generado por la gramática.")
                print(f"\n Tiempo de ejecución: {exec_time:.6f} segundos")

                if parse_tree:
                    print("\n ÁRBOL DE PARSING ")
                    print("---------------------")
                    parse_tree.print_tree()
            else:
                print("Resultado: NO")
                print(f"La frase NO pertenece al lenguaje generado por la gramática.")
                print(f"\n Tiempo de ejecución: {exec_time:.6f} segundos")
                print("-----------------------")

        elif opcion == '3':
            print("Gracias por usar el parser CYK")
            break

        else:
            print("Opción inválida. Por favor seleccione 1, 2 o 3")

if __name__ == "__main__":
    main()


                

                                    
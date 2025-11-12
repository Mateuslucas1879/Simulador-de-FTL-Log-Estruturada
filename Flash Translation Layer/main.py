from Flash import FlashMemory
from FTL import FTL, NoFreePageError
from Garbage_collector import GarbageCollector
import random

def pretty_print_stats(ftl):
    s = ftl.stats()
    print("=== ESTATÍSTICAS ===")
    print(f"Escritas lógicas: {s['logical_writes']}")
    print(f"Escritas físicas: {s['physical_writes']}")
    print(f"Erasures totais (soma dos erase_counts): {s['physical_erases']}")
    print(f"Páginas livres: {s['total_free_pages']}")
    print(f"Páginas válidas: {s['total_valid_pages']}")
    print(f"Páginas inválidas: {s['total_invalid_pages']}")
    print(f"Entradas na tabela de mapeamento: {s['mapping_entries']}")
    print("====================\n")

def run_random_workload(ftl, n_ops=200, logical_space=64, trim_probability=0.02):
    """
    Executa um workload aleatório de leitura/escrita para provocar GC e gerar métricas.
    """
    for i in range(n_ops):
        op = random.random()
        lpage = random.randint(0, logical_space - 1)

        if op < 0.8:

            data = f"v_{i}"
            try:
                ftl.write(lpage, data)
            except NoFreePageError:

                if ftl.gc is not None:
                    ftl.gc.collect()
                try:
                    ftl.write(lpage, data)
                except Exception as e:
                    print("Falha ao escrever mesmo após GC:", e)
                    break
        else:

            _ = ftl.read(lpage)


        if random.random() < trim_probability:
            to_trim = random.randint(0, logical_space - 1)
            ftl.trim(to_trim)

if __name__ == "__main__":

    flash = FlashMemory(num_blocks=6, pages_per_block=8)
    ftl = FTL(flash)
    gc = GarbageCollector(flash, ftl, aggressive=False)
    ftl.attach_gc(gc)

    print("Estado inicial da memória:")
    print(flash)
    pretty_print_stats(ftl)


    run_random_workload(ftl, n_ops=800, logical_space=64, trim_probability=0.03)

    print("Estado final da memória:")
    print(flash)
    pretty_print_stats(ftl)


    print("Exemplo de mapeamento (algumas entradas):")
    items = list(ftl.mapping.items())[:20]
    for k, v in items:
        print(f"Log {k} -> Bloco {v[0]} Página {v[1]}")

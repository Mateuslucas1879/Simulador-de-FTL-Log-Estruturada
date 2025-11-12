from collections import defaultdict

class NoFreePageError(Exception):
    pass

class FTL:
    def __init__(self, flash: object, gc=None):
        self.flash = flash
        self.mapping = dict()
        self.physical_writes = 0
        self.logical_writes = 0
        self.physical_erases = 0
        self.gc = gc

    def attach_gc(self, gc):
        self.gc = gc

    def _allocate_physical_page(self):
        block, page = self.flash.find_free_page()
        if page is not None:
            return block, page

        if self.gc is not None:
            self.gc.collect()
            block, page = self.flash.find_free_page()
            if page is not None:
                return block, page

        raise NoFreePageError("Sem páginas livres e GC não conseguiu liberar espaço.")

    def _physical_write(self, block, page, data):
        page.write(data)
        self.physical_writes += 1

    def write(self, logical_id, data):
        self.logical_writes += 1
        if logical_id in self.mapping:
            old_block_id, old_page_idx = self.mapping[logical_id]
            old_block = self.flash.blocks[old_block_id]
            old_page = old_block.pages[old_page_idx]
            old_page.invalidate()

        block, page = self._allocate_physical_page()
        self._physical_write(block, page, data)

        page_index = int(page.id.split("-")[1])
        self.mapping[logical_id] = (block.block_id, page_index)

    def trim(self, logical_id):
        # Simula a operação TRIM do SSD, liberando uma página lógica
        if logical_id not in self.mapping:
            return

        block_id, page_idx = self.mapping[logical_id]
        block = self.flash.blocks[block_id]
        page = block.pages[page_idx]

        page.invalidate()
        del self.mapping[logical_id]

    def read(self, logical_id):
        if logical_id not in self.mapping:
            return None
        b_id, p_idx = self.mapping[logical_id]
        page = self.flash.blocks[b_id].pages[p_idx]
        if page.state != "valid":
            return None
        return page.data

    def stats(self):
        return {
            "logical_writes": self.logical_writes,
            "physical_writes": self.physical_writes,
            "physical_erases": sum(b.erase_count for b in self.flash.blocks),
            "total_free_pages": self.flash.total_free_pages(),
            "total_invalid_pages": self.flash.total_invalid_pages(),
            "total_valid_pages": self.flash.total_valid_pages(),
            "mapping_entries": len(self.mapping)
        }

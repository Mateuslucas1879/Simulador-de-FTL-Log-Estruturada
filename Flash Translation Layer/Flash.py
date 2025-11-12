class Page:
    def __init__(self, block_id, page_index):
        self.id = f"{block_id}-{page_index}"
        self.state = "free"
        self.data = None

    def write(self, data):
        if self.state != "free":
            raise ValueError(f"Página {self.id} não está livre (estado={self.state}).")
        self.data = data
        self.state = "valid"

    def invalidate(self):
        if self.state == "valid":
            self.data = None
            self.state = "invalid"

    def erase(self):
        self.data = None
        self.state = "free"


class Block:
    def __init__(self, block_id, pages_per_block):
        self.block_id = block_id
        self.pages = [Page(block_id, i) for i in range(pages_per_block)]
        self.erase_count = 0

    def get_free_page(self):
        for p in self.pages:
            if p.state == "free":
                return p
        return None

    def is_full(self):
        return all(p.state != "free" for p in self.pages)

    def count_invalid(self):
        return sum(1 for p in self.pages if p.state == "invalid")

    def count_valid(self):
        return sum(1 for p in self.pages if p.state == "valid")

    def erase_block(self):
        for p in self.pages:
            p.erase()
        self.erase_count += 1

    def __str__(self):
        states = [p.state[0].upper() for p in self.pages]
        return f"Bloco {self.block_id}: {' '.join(states)} | Erases: {self.erase_count}"


class FlashMemory:
    def __init__(self, num_blocks=8, pages_per_block=16):
        self.num_blocks = num_blocks
        self.pages_per_block = pages_per_block
        self.blocks = [Block(i, pages_per_block) for i in range(num_blocks)]

    def find_free_page(self):
        for b in self.blocks:
            p = b.get_free_page()
            if p is not None:
                return b, p
        return None, None

    def total_free_pages(self):
        return sum(1 for b in self.blocks for p in b.pages if p.state == "free")

    def total_invalid_pages(self):
        return sum(1 for b in self.blocks for p in b.pages if p.state == "invalid")

    def total_valid_pages(self):
        return sum(1 for b in self.blocks for p in b.pages if p.state == "valid")

    def get_block_with_most_invalid(self):
        best = None
        max_invalid = -1
        for b in self.blocks:
            inv = b.count_invalid()
            if inv > max_invalid and inv > 0:
                best = b
                max_invalid = inv
        return best

    def erase_block(self, block):
        block.erase_block()

    def __str__(self):
        output = []
        for b in self.blocks:
            states = [p.state[0].upper() for p in b.pages]
            output.append(f"Bloco {b.block_id}: {' '.join(states)} | Erases: {b.erase_count}")
        return "\n".join(output)



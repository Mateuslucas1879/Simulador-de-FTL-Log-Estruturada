class GarbageCollector:
    def __init__(self,flash, ftl, aggressive=False):
        self.flash = flash
        self.ftl = ftl
        self.aggressive = aggressive
        self.collect_count = 0

    def collect(self):
        candidate = self.flash.get_block_with_most_invalid()
        if candidate is None:
            if self.aggressive:
                for b in self.flash.blocks:
                    if b.count_invalid() > 0 or b.count_valid() > 0:
                        candidate = b
                        break
            if candidate is None:
                return

        if not self.aggressive and candidate.count_invalid() == 0:
            return
        self.collect_count += 1
        block = candidate

        valid_pages = []
        for idx, p in enumerate(block.pages):
            if p.state == "valid":
                valid_pages.append((idx, p.data))

        for page_idx, data in valid_pages:
            logicals = [l for l, phys in self.ftl.mapping.items() if phys == (block.block_id, page_idx) ]
            if len(logicals) == 0:
                continue
            logical_id = logicals[0]

            try:
                new_block, new_page = self.ftl._allocate_physical_page()

            except Exception as e:
                print("GC: não há espaço para mover páginas válidas:", e)
                return
            self.ftl._physical_write(new_block, new_page, data)
            new_page_index = int(new_page.id.split("-")[1])
            self.ftl.mapping[logical_id] = (new_block.block_id, new_page_index)

            old_page = block.pages[page_idx]
            old_page.invalidate()

        self.flash.erase_block(block)




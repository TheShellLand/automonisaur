import queue


class UniqueQueue(queue.Queue):
    def _init(self, maxsize):
        super()._init(maxsize)
        # Create a set to track items currently inside the queue
        self.all_items = set()

    def _put(self, item):
        # Only add to the underlying deque if it's not in our set
        if item not in self.all_items:
            super()._put(item)
            self.all_items.add(item)

    def _get(self):
        # Remove from the set when the item is popped
        item = super()._get()
        self.all_items.remove(item)
        return item

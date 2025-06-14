from typing import List


class Draw:

    def __init__(self):

        self._item_list = List[None]

    def clear(self):
        self._item_list = {}

    def add_item(self, item):
        self._item_list.append(item)

    def remove_item(self, item):
        self._item_list.remove(item)



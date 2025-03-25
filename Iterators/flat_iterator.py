class FlatIterator:

    def __init__(self, list_of_list):
        self.list_of_list = list_of_list
        self.outer_index = 0
        self.inner_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.outer_index >= len(self.list_of_list):
            raise StopIteration

        current_list = self.list_of_list[self.outer_index]

        if self.inner_index >= len(current_list):
            self.outer_index += 1
            self.inner_index = 0
            if self.outer_index >= len(self.list_of_list):
                raise StopIteration
            current_list = self.list_of_list[self.outer_index]

        item = current_list[self.inner_index]
        self.inner_index += 1
        return item


def test_1():
    list_of_lists_1 = [
        ['a', 'b', 'c'],
        ['d', 'e', 'f', 'h', False],
        [1, 2, None]
    ]

    for flat_iterator_item, check_item in zip(
            FlatIterator(list_of_lists_1),
            ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None]
    ):
        assert flat_iterator_item == check_item

    assert list(FlatIterator(list_of_lists_1)) == ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None]


if __name__ == '__main__':
    test_1()
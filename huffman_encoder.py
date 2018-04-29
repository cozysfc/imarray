# coding:utf-8


from heapq import heappop, heappush
from collections import defaultdict
from prettytable import PrettyTable


class FrequencyTable:
    def __init__(self, sequences):
        self.frequency = defaultdict(int)
        self.isnested = False

        if self.is_nested_sequences(sequences):
            self.isnested = True

        self.build_frequency_table(sequences)

    def build_frequency_table(self, sequences):
        if self.isnested:
            for s in sequences:
                self.frequency[s.__str__()] += 1
        else:
            for s in sequences:
                self.frequency[s] += 1

    def is_nested_sequences(self, sequences):
        if isinstance(sequences, str):
            return False
        elif all([isinstance(s, (str, int)) for s in sequences]):
            return False
        return True

    def __getitem__(self, key):
        if self.isnested:
            return self.frequency[key.__str__()]
        else:
            return self.frequency[key]


class Node:
    def __init__(self, value, count, right=None, left=None):
        self.value = value
        self.count = count
        self.right = right
        self.left = left

    def __cmp__(x, y):
        return x.count-y.count


class HuffmanEncoder:
    def __init__(self, sequences):
        # Calculate frequency for each sequence
        self.sequences = sequences
        self.frequency_table = FrequencyTable(sequences)
        self.isnested = self.frequency_table.isnested

        # Build huffman coding
        self.value2code = {}
        self.code2value = {}

        if len(self.frequency_table.frequency)>1:
            self.root = self.make_tree()
            self.make_code("", self.root)
        else:
            value = self.frequency_table.frequency.keys()[0]
            self.value2code[value] = "0"
            self.code2value["0"] = value

    def make_tree(self):
        queue = []

        for value, count in self.frequency_table.frequency.items():
            heappush(queue, Node(value, count))

        # Create initial node
        init_node1, init_node2 = heappop(queue), heappop(queue)
        root = Node(None, init_node1.count+init_node2.count, init_node1, init_node2)

        while True:
            if len(queue) == 0:
                return root

            node = heappop(queue)
            root = Node(None, node.count + root.count, root, node)

    def make_code(self, bitstream, node):
        if node is None:
            pass

        elif node.value:
            if not bitstream:
                self.value2code[node.value] = "0"
                self.code2value["0"] = node.value
            else:
                self.value2code[node.value] = bitstream
                self.code2value[bitstream] = node.value
        else:
            self.make_code(bitstream+"0", node.left)
            self.make_code(bitstream+"1", node.right)

    def encode(self, sequences):
        return [self.value2code[s.__str__()] for s in sequences]

    def decode(self, sequences):
        return [self.code2value[s] for s in sequences]

    def __repr__(self):
        sorted_frequency_table = sorted(self.frequency_table.frequency.items(),
            key=lambda k: k[1], reverse=True)

        table = PrettyTable(["frequency", "value", "code"])
        table.align['value'] = table.align['code'] = 'l'
        for k, v in sorted_frequency_table:
            table.add_row([v, k, self.value2code[k]])

        return table.__str__()

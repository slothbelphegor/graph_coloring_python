"""
Với đầu vào là danh sách vị trí các node, trả về các node tương ứng

Nếu 2 node có khoảng cách lớn hơn DISC_LIMIT thì sẽ dùng 2 điểm phát sóng khác nhau -> Tô màu khác nhau
-> 2 node nối nhau
"""
from numpy import sqrt


class Node:
    def __init__(self, id, adjacent_nodes_id):
        self.id = id
        self.adjacent_nodes_id = adjacent_nodes_id
        self.color = 0

        if adjacent_nodes_id == []:
            self.degree = 1
        else:
            self.degree = len(adjacent_nodes_id)  # Khởi tạo bậc cho mỗi node

    def get_neighbors(self, nodes):
        return [nodes[node_id - 1] for node_id in self.adjacent_nodes_id]

    def set_color(self, color):
        self.color = color

    def decrease_degree(self):
        if self.degree > 1:
            self.degree -= 1


def distance(node1, node2):
    return round(sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2), 2)


def calculateNodeDistance(node_positions):
    result = []
    for i in range(1, len(node_positions) + 1):
        newRow = []
        for j in range(1, len(node_positions) + 1):
            firstnode = node_positions[i]
            secondnode = node_positions[j]
            newRow.append(distance(firstnode, secondnode))
        result.append(newRow)
    return result


def createNodeList(node_distance_map, disc_limit):
    nodeList = []
    for i in range(len(node_distance_map)):
        # danh sách chứa các điểm nối với node này
        # điều kiện là khoảng cách lớn hơn DISC_LIMIT
        adjacent_nodes = []
        for j in range(len(node_distance_map[i])):
            if node_distance_map[i][j] > disc_limit:
                adjacent_nodes.append(j + 1)
        nodeList.append(Node(i + 1, adjacent_nodes))
    return nodeList


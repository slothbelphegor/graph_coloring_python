import matplotlib.pyplot as plt
import networkx as nx
from PyQt5.QtCore import QEventLoop
from matplotlib import colors

from create_nodes_from_input import calculateNodeDistance, createNodeList

"""
Bài toán: Một công viên giải trí đang thực hiện nâng cấp cơ sở hạ tầng toàn khu. Một trong các chỉ tiêu được đưa ra là 
toàn bộ diện tích công viên được phủ sóng Wi-Fi không dây, sao cho mọi khách hàng đều có thể truy cập Internet mọi nơi trong công viên.
Để tăng hiệu suất và giảm chi phí lắp đặt các điểm phát sóng, một số khu vực sẽ dùng chung một điểm phát sóng. Điểm phát sóng 
có càng nhiều khu vực dùng chung thì càng phải được đầu tư loại có tốc độ cao hơn. 
Với đầu vào là khoảng cách giữa các khu vực, dùng thuật toán tô màu để xác định những khu vực nào sẽ dùng chung điểm phát sóng.
"""



def drawNodes(node_positions):
    # Vẽ các điểm trong đồ thị
    for node_id, position in node_positions.items():
        plt.plot(position[0], position[1], 'o', markersize=15, markerfacecolor='lightblue', markeredgewidth=2,
                 markeredgecolor='blue')
        plt.text(position[0], position[1], str(node_id), ha='center', va='center', fontsize=12, fontweight='bold',
                 color='black')


def drawEdges(node_positions, nodes):
    # Duyệt qua các Node trong đồ thị, vẽ các cạnh
    for node in nodes:
        for neighbor in node.get_neighbors(nodes):
            node_pos = node_positions[node.id]
            neighbor_pos = node_positions[neighbor.id]
            plt.plot([node_pos[0], neighbor_pos[0]], [node_pos[1], neighbor_pos[1]], 'b',
                     alpha=0.4)  # Đường màu xanh, độ mờ 0.7


def drawGraph(node_positions, nodes):
    drawEdges(node_positions, nodes)
    drawNodes(node_positions)
    drawColor(node_positions, nodes)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis('off')  # Tắt hiển thị trục
    plt.show(block=True)


def drawColor(node_positions, nodes):
    # Tô màu cho đồ thị
    for node_id, position in node_positions.items():
        node = nodes[node_id - 1]
        if node.color == 0:
            nodeColor = 'white'
        else:
            nodeColor = f"C{node.color}"
        plt.plot(position[0], position[1], 'o', markersize=15, markerfacecolor=nodeColor, markeredgewidth=2,
                 markeredgecolor='blue')
        plt.text(position[0], position[1], str(node_id), ha='center', va='center', fontsize=12, fontweight='bold',
                 color='black')


def degree_coloring(node_positions, log_area, disc_limit):
    # Tạo danh sách khoảng cách node và đối tượng node
    node_distance_map = calculateNodeDistance(node_positions)
    nodes = createNodeList(node_distance_map, disc_limit)

    # Sắp xếp các node theo thứ tự bậc giảm dần
    nodes_by_degree = sorted(nodes, key=lambda node: node.degree, reverse=True)

    # Khởi tạo màu cho mỗi node là None
    for node in nodes_by_degree:
        node.set_color(0)

    # Duyệt qua các node theo thứ tự bậc giảm dần (lặp cho đến khi mọi node đều có màu)
    while nodes_by_degree[0].color == 0:

        log_area.append(f"Danh sách các node theo bậc: {[node.id for node in nodes_by_degree]}")
        log_area.append(f"Danh sách bậc các node: {[node.degree for node in nodes]}")
        # Lấy node bậc cao nhất
        node = nodes_by_degree[0]

        # Tô màu node nào thì bậc = 0
        node.degree = 0

        # Lấy danh sách các node kề
        neighbors = [neighbor for neighbor in node.get_neighbors(nodes)]

        # Lấy danh sách màu của các node kề
        neighbor_colors = {neighbor.color for neighbor in neighbors if neighbor.color != 0}

        # print(f"Xét node {node.id} kề các node {[n.id for n in neighbors]}, màu kề là {neighbor_colors}")
        log_area.append(f"Xét node {node.id} kề các node {[n.id for n in neighbors]}, màu kề là {neighbor_colors}")
        # Tìm màu khả dụng cho node hiện tại
        for color in range(1, len(nodes) + 1):
            if color not in neighbor_colors:
                node.set_color(color)
                # print(f"Đặt màu {color}")
                log_area.append(f"Đặt màu {color}")
                # Giảm bậc của các node kề
                for neighbor in node.get_neighbors(nodes):
                    neighbor.decrease_degree()
                break

        # Vẽ đồ thị cho lần tô này
        drawGraph(node_positions, nodes)

        # Tạo một vòng lặp sự kiện tạm thời
        event_loop = QEventLoop()
        plt.gcf().canvas.mpl_connect('close_event', lambda event: event_loop.quit())
        plt.show(block=True)  # Hiển thị cửa sổ đồ thị không chặn vòng lặp
        event_loop.exec_()  # Chờ cho đến khi cửa sổ đồ thị được đóng

        # Sắp xếp lại danh sách node bậc giảm dần sau khi hạ bậc các node kề
        nodes_by_degree = sorted(nodes, key=lambda node: node.degree, reverse=True)
        log_area.append("\n")
        # Số màu sử dụng

    # Số màu sử dụng
    num_colors = max(node.color for node in nodes)
    return num_colors


def welsh_powell_coloring(node_positions, log_area, disc_limit):
    node_distance_map = calculateNodeDistance(node_positions)
    nodes = createNodeList(node_distance_map, disc_limit)

    # Sắp xếp các node theo thứ tự bậc giảm dần
    nodes_copies = nodes.copy()
    nodes_by_degree = sorted(nodes_copies, key=lambda node: node.degree, reverse=True)

    # Khởi tạo màu cho mỗi node
    for node in nodes_by_degree:
        node.set_color(0)

    # Duyệt qua màu có thể tô
    for color in range(1, len(nodes) + 1):
        # Mảng lưu các node đã tô màu đang xét
        colored_nodes = []
        log_area.append(f"Đổi sang màu {color}")
        for current_node in nodes_by_degree:
            neighbors = current_node.get_neighbors(nodes)
            log_area.append(f"Các node xếp theo bậc: {[node.id for node in nodes_by_degree]}")
            log_area.append(f"Danh sách bậc các node: {[node.degree for node in nodes]}")
            log_area.append(f"Các node đã tô màu {color}: {[node.id for node in colored_nodes]}")
            log_area.append(f"Xét node {current_node.id} kề các node {[n.id for n in neighbors]}")
            # Nếu node đang xét không kề bất kì node nào đã tô màu hiện tại
            if all(neighbor not in colored_nodes for neighbor in neighbors):

                log_area.append(f"Tô màu {color}\n")
                current_node.set_color(color)
                colored_nodes.append(current_node)
                drawGraph(node_positions, nodes)
                # Tạo một vòng lặp sự kiện tạm thời
                event_loop = QEventLoop()
                plt.gcf().canvas.mpl_connect('close_event', lambda event: event_loop.quit())
                plt.show(block=True)  # Hiển thị cửa sổ đồ thị không chặn vòng lặp
                event_loop.exec_()  # Chờ cho đến khi cửa sổ đồ thị được đóng

                log_area.clear()
            else:
                for neighbor in neighbors:
                    if neighbor in colored_nodes:
                        log_area.append(f"Kề node {neighbor.id}, không tô\n")
                        break
        for colored_node in colored_nodes:
            nodes_by_degree.remove(colored_node)
        if not colored_nodes:
            break

        log_area.clear()
        log_area.append(f"Loại bỏ các node tô màu {color} khỏi danh sách")

    # Số màu sử dụng
    log_area.clear()
    num_colors = max(node.color for node in nodes)
    return num_colors



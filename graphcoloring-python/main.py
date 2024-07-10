import sys
import matplotlib
from PyQt5.QtWidgets import QApplication, QSizePolicy, QWidget, QMainWindow, QMenu, QVBoxLayout, QSpinBox, QLineEdit, \
    QPushButton, QHBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import Qt, QEventLoop
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import graph_coloring
from create_nodes_from_input import calculateNodeDistance, createNodeList

matplotlib.use("Qt5Agg")

nodes_positions = {}


class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=30, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.axes.plot()
        self.plot_data = []  # List to store node positions
        self.drawn_objects = []
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.cid = self.mpl_connect('button_press_event', self.on_click)

    def draw_node(self, x, y, new_node_id):
        circle = plt.Circle((x, y), radius=0.6, color='white')
        self.axes.add_patch(circle)
        text = self.axes.text(x, y + 0.1, f"{new_node_id}", ha='center', va='center', fontsize=12)
        self.drawn_objects.append(circle)
        self.drawn_objects.append(text)
        self.draw()

    def reset_plot(self):
        # Xóa tất cả các đối tượng đã vẽ trên đồ thị
        for obj in self.drawn_objects:
            obj.remove()
        self.drawn_objects = []  # Đặt lại danh sách các đối tượng đã vẽ
        # Cập nhật lại canvas
        self.draw()

    def on_click(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            # Generate a unique node ID
            new_node_id = len(nodes_positions) + 1

            # Update nodes_pos with new node and position
            nodes_positions[new_node_id] = (round(x, 2), round(y, 2))

            # Update plot_data with new node and position
            self.plot_data.append((x, y))

            # Draw this node with labels
            self.draw_node(x, y, new_node_id)

            # Update position_field with clicked coordinates
            pos_string = ""
            for node_id in range(1, len(nodes_positions) + 1):
                pos_string += str(nodes_positions[node_id]) + ';'
            self.parent().parent().position_field.setText(pos_string.rstrip(';'))
            self.draw()


class MyStaticMplCanvas(MyMplCanvas):
    def __init__(self, f):
        # Set axis limits and tick values
        super().__init__()
        self.f = f
        self.axes.set_xlim(0, 100)  # Set x-axis range
        self.axes.set_ylim(0, 100)  # Set y-axis range
        self.axes.set_xticks(np.arange(0, 110, 10))  # Set x-axis ticks every 10 units
        self.axes.set_yticks(np.arange(0, 110, 10))  # Set y-axis ticks every 10 units
        self.draw()


class ApplicationWindow(QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.close, Qt.CTRL + Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.main_widget = QWidget()
        layout = QVBoxLayout(self.main_widget)

        # Distance Limit label and line edit
        distance_label = QLabel("Distance Limit:")
        self.distance_limit_field = QLineEdit(str(21))

        # Position field
        self.position_field = QLineEdit(
            "(10, 20);(10, 10);(8, 32);(20, 8);(30, 20);(30, 10);(32, 32);(20, 22);(15, 40);(25, 40)")

        self.sc = MyStaticMplCanvas(self.main_widget)  # Pass self as parent

        self.log_area = QTextEdit()
        self.log_area.setFontPointSize(10)

        self.save_button = QPushButton("Save Nodes")
        self.save_button.clicked.connect(self.handle_save_button)
        self.draw_button_optimal = QPushButton("Draw Graph (Optimal)")
        self.draw_button_optimal.clicked.connect(
            lambda: self.handle_draw_button_optimal(float(self.distance_limit_field.text()))
        )
        self.draw_button_welshpowell = QPushButton("Draw Graph (WelshPowell)")
        self.draw_button_welshpowell.clicked.connect(
            lambda: self.handle_draw_button_welshpowell(float(self.distance_limit_field.text()))
        )

        # Vertical box layout for distance and position fields
        vbox_fields = QVBoxLayout()
        vbox_fields.addWidget(self.position_field)
        hbox_distance = QHBoxLayout()
        hbox_distance.addWidget(distance_label)
        hbox_distance.addWidget(self.distance_limit_field)
        vbox_fields.addLayout(hbox_distance)

        # Horizontal box layout for buttons
        hbox_button = QHBoxLayout()
        hbox_button.addWidget(self.save_button)
        hbox_button.addWidget(self.draw_button_optimal)
        hbox_button.addWidget(self.draw_button_welshpowell)

        # Main vertical box layout
        vbox = QVBoxLayout()
        vbox.addLayout(vbox_fields)
        vbox.addLayout(hbox_button)
        layout.addLayout(vbox)  # Add vbox to the main layout

        # Horizontal box layout for log_area and sc
        hbox = QHBoxLayout()
        hbox.addWidget(self.log_area)
        hbox.addWidget(self.sc)
        layout.addLayout(hbox)  # Add hbox to the main layout

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def handle_save_button(self):
        # Get text from position_field
        positions_text = self.position_field.text()
        distance_text = self.distance_limit_field.text()

        # Validate and parse positions (handle errors appropriately)
        try:
            if positions_text == "":
                nodes_positions.clear()
                self.sc.reset_plot()
            else:
                # Split positions based on semi-colons
                positions = [tuple(map(float, item[1:-1].split(','))) for item in positions_text.split(";")]

                # Reset the graph
                self.sc.reset_plot()

                nodes_positions.clear()  # Clear existing dictionary (optional)
                for position in positions:
                    # Split each position into id and coordinates (adjust format if needed)
                    node_id = len(nodes_positions) + 1

                    # Create a dictionary entry for each node
                    nodes_positions[node_id] = position
                    self.sc.draw_node(position[0], position[1], node_id)
        except ValueError:
            # Show error message if parsing fails
            self.log_area.append("Invalid positions format. Please use format '(x,y)' separated by ';'.")
            return


        # Add "Button Pressed" message to the log area
        self.log_area.clear()
        self.log_area.append("Nodes Saved")
        self.log_area.append(f"Distance limit: {float(self.distance_limit_field.text())}")
        node_distance_map = calculateNodeDistance(nodes_positions)
        print(node_distance_map)

        # Refresh the canvas
        self.sc.draw()

    def handle_draw_button_optimal(self, disc_limit):
        num_colors = graph_coloring.degree_coloring(nodes_positions, self.log_area, disc_limit)
        self.log_area.append(f"\nSố màu sử dụng: {num_colors}")

    def handle_draw_button_welshpowell(self, disc_limit):
        num_colors = graph_coloring.welsh_powell_coloring(nodes_positions, self.log_area, disc_limit)
        self.log_area.append(f"\nSố màu sử dụng: {num_colors}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.setWindowTitle("Coloring Algorithm")
    aw.show()
    sys.exit(app.exec_())

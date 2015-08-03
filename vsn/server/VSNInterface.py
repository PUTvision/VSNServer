from PyQt5 import QtCore, QtWidgets, QtGui
from pyqtgraph import PlotWidget
from vsn.common.VSNUtility import CameraStatisticsTuple, Config
from vsn.server.VSNGraph import VSNGraphController, VSNGraph
from vsn.server.VSNCameras import VSNCameras


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.__controls()
        self.__titles()
        self.__layout()

        self.__camera_widgets = set()

        self.camerasTabWidget.setCurrentIndex(0)

    def __layout(self):
        self.resize(953, 673)

        # Menu bar
        self.menubar.setGeometry(QtCore.QRect(0, 0, 953, 25))

        self.setMenuBar(self.menubar)
        self.menuVSN.addAction(self.actionClose)
        self.menubar.addAction(self.menuVSN.menuAction())

        # Central widget
        self.setCentralWidget(self.centralwidget)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.camerasTabWidget = QtWidgets.QTabWidget(self.centralwidget)

        self.horizontalLayout.addWidget(self.camerasTabWidget)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.previewGroupBox)
        self.verticalLayout.addWidget(self.preview1)
        self.verticalLayout.addWidget(self.preview2)
        self.verticalLayout.addWidget(self.preview3)
        self.horizontalLayout.addWidget(self.previewGroupBox)

        # Status bar
        self.setStatusBar(self.statusbar)

    def __titles(self):
        self.setWindowTitle("VSNServer")
        self.previewGroupBox.setTitle("Most active")
        self.menuVSN.setTitle("VSNServer")
        self.actionClose.setText("Close")

    def __controls(self):
        self.menubar = QtWidgets.QMenuBar(self)
        self.menuVSN = QtWidgets.QMenu(self.menubar)
        self.actionClose = QtWidgets.QAction(self)

        self.centralwidget = QtWidgets.QWidget(self)

        self.previewGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.preview1 = QtWidgets.QLabel(self.previewGroupBox)
        self.preview2 = QtWidgets.QLabel(self.previewGroupBox)
        self.preview3 = QtWidgets.QLabel(self.previewGroupBox)
        VSNCameras.add_preview_widget(self.preview1)
        VSNCameras.add_preview_widget(self.preview2)
        VSNCameras.add_preview_widget(self.preview3)

        self.statusbar = QtWidgets.QStatusBar(self)

    def set_status(self, status: str):
        self.statusbar.showMessage(status)

    def add_new_camera_tab(self, camera_id: int, camera_name: str):
        try:
            getattr(self, 'cam%i' % camera_id)
        except AttributeError:
            new_camera_widget = CameraWidget(camera_id, self.__camera_widgets)
            self.__camera_widgets.add(new_camera_widget)
            setattr(self, 'cam%i' % camera_id, new_camera_widget)
            self.camerasTabWidget.addTab(new_camera_widget, "")
            self.camerasTabWidget.setTabText(self.camerasTabWidget.indexOf(new_camera_widget), camera_name)

    def update_camera_statistics(self, camera_id: int, statistics: CameraStatisticsTuple):
        camera_widget = getattr(self, 'cam%i' % camera_id)
        camera_widget.set_statistics(statistics)


class CameraWidget(QtWidgets.QWidget):
    def __init__(self, camera_id: int, neighbours: set):
        super().__init__()

        self.__id = camera_id

        self.__controls()
        self.__handlers()
        self.__titles()
        self.__layout()

        self.__neighbours = neighbours

        for neighbour in neighbours:
            self.add_dependency(neighbour.id)
            neighbour.add_dependency(camera_id)

    @property
    def id(self):
        return self.__id

    @property
    def plot_controller(self):
        return self.__plot_controller

    def add_dependency(self, neighbour_id):
        new_dependency_label = QtWidgets.QLabel(self.dependenciesGroupBox)
        new_dependency_spin_box = QtWidgets.QDoubleSpinBox(self.dependenciesGroupBox)

        new_dependency_label.setText('Camera %i' % neighbour_id)
        new_dependency_spin_box.setValue(Config.get_dependency_value(self.__id, neighbour_id))

        setattr(self, 'dependencyCam%iLabel' % neighbour_id, new_dependency_label)
        setattr(self, 'dependencyCam%iDoubleSpinBox' % neighbour_id, new_dependency_spin_box)

        self.gridLayout_5.addWidget(new_dependency_label, neighbour_id, 0, 1, 1)
        self.gridLayout_5.addWidget(new_dependency_spin_box, neighbour_id, 1, 1, 1)

    def __controls(self):
        self.cameraSettingsGroupBox = QtWidgets.QGroupBox(self)
        self.activationLevelThresholdLabel = QtWidgets.QLabel(self.cameraSettingsGroupBox)
        self.activationLevelThresholdSpinBox = QtWidgets.QSpinBox(self.cameraSettingsGroupBox)

        self.parametersBelowThresholdGroupBox = QtWidgets.QGroupBox(self.cameraSettingsGroupBox)
        self.gainBelowThresholdLabel = QtWidgets.QLabel(self.parametersBelowThresholdGroupBox)
        self.sampleTimeBelowThresholdLabel = QtWidgets.QLabel(self.parametersBelowThresholdGroupBox)
        self.gainBelowThresholdDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.parametersBelowThresholdGroupBox)
        self.sampleTimeBelowThresholdDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.parametersBelowThresholdGroupBox)

        self.parametersAboveThresholdGroupBox = QtWidgets.QGroupBox(self.cameraSettingsGroupBox)
        self.gainAboveThresholdLabel = QtWidgets.QLabel(self.parametersAboveThresholdGroupBox)
        self.sampleTimeAboveThresholdLabel = QtWidgets.QLabel(self.parametersAboveThresholdGroupBox)
        self.gainAboveThresholdDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.parametersAboveThresholdGroupBox)
        self.sampleTimeAboveThresholdDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.parametersAboveThresholdGroupBox)

        self.dependenciesGroupBox = QtWidgets.QGroupBox(self.cameraSettingsGroupBox)
        self.dependencySelfLabel = QtWidgets.QLabel(self.dependenciesGroupBox)
        self.dependencySelfDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.dependenciesGroupBox)
        self.setSettingsPushButton = QtWidgets.QPushButton(self.cameraSettingsGroupBox)
        self.saveSettingsPushButton = QtWidgets.QPushButton(self.cameraSettingsGroupBox)

        self.cameraStatisticsGroupBox = QtWidgets.QGroupBox(self)
        self.gainTextLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.lowPowerTicksLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.normalTicksTextLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.normalTicksLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.activityLevelLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.neighboursActivationLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.activePixelsLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.lowPowerTicksTextLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.sampleTimeLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.sampleTimeTextLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.gainLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.activePixelsTextLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.activityLevelTextLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.neighboursActivationTextLabel = QtWidgets.QLabel(self.cameraStatisticsGroupBox)
        self.cameraActivityGraph = PlotWidget(self.cameraStatisticsGroupBox, background='w')
        self.__plot_controller = VSNGraphController.create_plot(self.__id, self.cameraActivityGraph)

    def __handlers(self):
        self.setSettingsPushButton.clicked.connect(self.__set_settings)
        self.saveSettingsPushButton.clicked.connect(Config.save_settings)

    def __titles(self):
        self.cameraSettingsGroupBox.setTitle("Camera settings")
        self.activationLevelThresholdLabel.setText("Activation level threshold:")
        self.parametersBelowThresholdGroupBox.setTitle("Below threshold")
        self.gainBelowThresholdLabel.setText("Gain:")
        self.sampleTimeBelowThresholdLabel.setText("Sample time:")
        self.parametersAboveThresholdGroupBox.setTitle("Above threshold")
        self.sampleTimeAboveThresholdLabel.setText("Sample time:")
        self.gainAboveThresholdLabel.setText("Gain:")
        self.dependenciesGroupBox.setTitle("Dependencies")
        self.dependencySelfLabel.setText("Self:")
        self.setSettingsPushButton.setText("Set")
        self.saveSettingsPushButton.setText("Save")
        self.cameraStatisticsGroupBox.setTitle("Camera statistics")
        self.gainTextLabel.setText("Gain:")
        self.lowPowerTicksLabel.setText("0")
        self.normalTicksTextLabel.setText("Normal ticks:")
        self.normalTicksLabel.setText("0")
        self.activityLevelLabel.setText("0")
        self.neighboursActivationLabel.setText("0")
        self.activePixelsLabel.setText("0")
        self.lowPowerTicksTextLabel.setText("Low power ticks:")
        self.sampleTimeLabel.setText("0")
        self.sampleTimeTextLabel.setText("Sample time:")
        self.gainLabel.setText("0")
        self.activePixelsTextLabel.setText("Active pixels:")
        self.activityLevelTextLabel.setText("Activity level:")
        self.neighboursActivationTextLabel.setText("Neighbours activation:")

        self.activationLevelThresholdSpinBox.setValue(Config.settings['clients']['activation_level_threshold'])
        self.gainBelowThresholdDoubleSpinBox.setValue(Config.settings['clients']['parameters_below_threshold']['gain'])
        self.sampleTimeBelowThresholdDoubleSpinBox.setValue(Config.settings['clients']['parameters_below_threshold']['sample_time'])
        self.gainAboveThresholdDoubleSpinBox.setValue(Config.settings['clients']['parameters_above_threshold']['gain'])
        self.sampleTimeAboveThresholdDoubleSpinBox.setValue(Config.settings['clients']['parameters_above_threshold']['sample_time'])
        self.dependencySelfDoubleSpinBox.setValue(Config.get_dependency_value(self.__id, self.__id))

    def __layout(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)

        self.gridLayout_2 = QtWidgets.QGridLayout(self.cameraSettingsGroupBox)
        self.gridLayout_2.addWidget(self.activationLevelThresholdLabel, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.activationLevelThresholdSpinBox, 1, 1, 1, 1)

        self.gridLayout_3 = QtWidgets.QGridLayout(self.parametersBelowThresholdGroupBox)
        self.gridLayout_3.addWidget(self.gainBelowThresholdLabel, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.sampleTimeBelowThresholdLabel, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gainBelowThresholdDoubleSpinBox, 0, 1, 1, 1)
        self.gridLayout_3.addWidget(self.sampleTimeBelowThresholdDoubleSpinBox, 1, 1, 1, 1)
        self.gainBelowThresholdLabel.raise_()
        self.sampleTimeBelowThresholdLabel.raise_()
        self.gainBelowThresholdDoubleSpinBox.raise_()
        self.sampleTimeBelowThresholdDoubleSpinBox.raise_()
        self.gridLayout_2.addWidget(self.parametersBelowThresholdGroupBox, 0, 0, 1, 1)

        self.gridLayout_4 = QtWidgets.QGridLayout(self.parametersAboveThresholdGroupBox)
        self.gridLayout_4.addWidget(self.sampleTimeAboveThresholdLabel, 1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.gainAboveThresholdLabel, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.gainAboveThresholdDoubleSpinBox, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.sampleTimeAboveThresholdDoubleSpinBox, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.parametersAboveThresholdGroupBox, 0, 1, 1, 1)

        self.gridLayout_5 = QtWidgets.QGridLayout(self.dependenciesGroupBox)
        self.gridLayout_5.addWidget(self.dependencySelfLabel, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.dependencySelfDoubleSpinBox, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.dependenciesGroupBox, 2, 0, 1, 2)
        self.gridLayout_2.addWidget(self.setSettingsPushButton, 3, 0, 1, 1)
        self.gridLayout_2.addWidget(self.saveSettingsPushButton, 3, 1, 1, 1)
        self.horizontalLayout.addWidget(self.cameraSettingsGroupBox)

        self.gridLayout = QtWidgets.QGridLayout(self.cameraStatisticsGroupBox)
        self.gridLayout.addWidget(self.gainTextLabel, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.lowPowerTicksLabel, 5, 1, 1, 1)
        self.gridLayout.addWidget(self.normalTicksTextLabel, 6, 0, 1, 1)
        self.gridLayout.addWidget(self.normalTicksLabel, 6, 1, 1, 1)
        self.gridLayout.addWidget(self.activityLevelLabel, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.neighboursActivationLabel, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.activePixelsLabel, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.lowPowerTicksTextLabel, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.sampleTimeLabel, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.sampleTimeTextLabel, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.gainLabel, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.activePixelsTextLabel, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.activityLevelTextLabel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.neighboursActivationTextLabel, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.cameraActivityGraph, 7, 0, 1, 2)
        self.horizontalLayout.addWidget(self.cameraStatisticsGroupBox)

    def __set_settings(self):
        dependency_table = {}

        for neighbour in self.__neighbours:
            neighbour_id = neighbour.id

            if neighbour_id != self.__id:
                dependency_widget = getattr(self, 'dependencyCam%iDoubleSpinBox' % neighbour_id)
            else:
                dependency_widget = self.dependencySelfDoubleSpinBox

            dependency_table[self.id] = {}
            dependency_table[self.id][neighbour_id - 1] = dependency_widget.value()

        Config.set_settings(self.gainBelowThresholdDoubleSpinBox.value(),
                            self.sampleTimeBelowThresholdDoubleSpinBox.value(),
                            self.gainAboveThresholdDoubleSpinBox.value(),
                            self.sampleTimeAboveThresholdDoubleSpinBox.value(),
                            self.activationLevelThresholdSpinBox.value(),
                            dependency_table)

    def set_statistics(self, statistics: CameraStatisticsTuple):
        self.activePixelsLabel.setText('%.2f' % statistics.active_pixels)
        self.activityLevelLabel.setText('%.2f' % statistics.activity_level)
        self.neighboursActivationLabel.setText('%.2f' % statistics.neighbours_activation)
        self.gainLabel.setText('%.2f' % statistics.gain)
        self.sampleTimeLabel.setText('%.2f' % statistics.sample_time)
        self.lowPowerTicksLabel.setText('%i' % statistics.low_power_ticks)
        self.normalTicksLabel.setText('%i' % statistics.normal_ticks)

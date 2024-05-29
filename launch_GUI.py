"""
Shape Memory Alloy Rendering of Experimental Analysis and Calibration Tool
(SMA-REACT)

Main launch script

Last updated: May 20th, 2024 (see GitHub for updates)
"""

import cgitb
import json
import os
from datetime import date
from PyQt5 import QtGui, QtWidgets


from data_input.create_data_input import (
    DataInputWidget
    )

from calibration.model_funcs.test_optimizer_v2 import main
from calibration.create_calibration_parameters import (
    CalibrationParametersWidget,
    )

from calibration_progress.create_calibration_progress_widget import (
    CalibrationProgressWidget
    )


class App(QtWidgets.QMainWindow):
    '''
    Master GUI with all required tabs
    (implemented as different classes). Inherits the
    QtWidgets.QMainWindow class.
    '''
    def __init__(self):
        '''
        Creates the main GUI page and calls all other
        tabs.

        Returns
        -------
        None.

        '''
        super().__init__()
        # Formatting
        self.title = 'Shape Memory Alloy REACT \
    (Rendering of Experimental Analysis and Calibration Tool)'

        #FIXME Start
        app = QtWidgets.QApplication(sys.argv)
        screen = app.primaryScreen()
        rect = screen.availableGeometry()

        left = int(rect.width()*0.05)
        top = int(rect.height()*0.05)
        width = 2000
        height = 800

        self.setGeometry(left, top, width, height)
        #FIXME End


        #Set window icon to be the A&M Logo (of course)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("TAM-LogoBox.ico"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
            )

        self.setWindowIcon(icon)
        self.setWindowTitle(self.title)


        self.tabs = QtWidgets.QTabWidget()
        self.tabs.resize(width,height)


        self.calibration_parameters_widget = CalibrationParametersWidget()

        self.data_input_widget = DataInputWidget()

        self.calibration_plotting_widget = CalibrationProgressWidget()

        self.tabs.addTab(
            self.data_input_widget,
            'Data Input'
            )
        self.tabs.addTab(
            self.calibration_parameters_widget,
            "Material Property Calibration"
            )


        self.tabs.addTab(
            self.calibration_plotting_widget,
            "Calibration Plotting Utility"
            )


        self.setCentralWidget(self.tabs)

        self.tabs.setTabEnabled(1,False)
        self.tabs.setTabEnabled(2,False)

        #connect the continue button to changing a tab
        self.data_input_widget.continue_button.clicked.connect(
            lambda: self.change_tabs(
                index=1
                )
            )

        #connect the calibration button to the optimization
        self.calibration_parameters_widget.pushButton.clicked.connect(
            self.run_calibration
            )

        self.calibration_plotting_widget.export_button.clicked.connect(
            self.export_solution)

        self.show()

    def change_tabs(
            self,
            index,
            ):
        '''Enables the specified tab and changes to that tab.
        To connect this to a pushButton or another widget,
        you must use a lambda function, like so:

            widget.clicked.connect(
                lambda : self.changeTabs(
                    index = some_index
                    )
                )


        Parameters
        ----------
        index : INT
            Tab index that you would like to change to.

        Returns
        -------
        None.

        '''
        self.tabs.setTabEnabled(index,True)
        self.tabs.setCurrentIndex(index)

    def run_calibration(self):
        '''
        Runs the calibration optimization and changes to the progress
        plotting tab.

        #FIXME To-do: Include an export function here to make an
        Abaqus material model or export all required properties as a
        JSON or something similar.

        Returns
        -------
        None.

        '''
        self.calibration_parameters_widget.getSpecifiedValues()
        bounds = self.calibration_parameters_widget.getBounds()
        print(self.calibration_parameters_widget.known_values)

        app.processEvents()

        self.change_tabs(index=2)

        self.optimization_error = main(
            bounds,
            self.calibration_parameters_widget,
            self.data_input_widget.data,
            self.calibration_plotting_widget
            )

        self.calibration_plotting_widget.export_button.setEnabled(True)

    def export_solution(self):
        '''
        Prints and exports the calibrated solution,
        with all of the important intermediary data.

        Returns
        -------
        None.

        '''
        self.calibration_parameters_widget.getSpecifiedValues()
        bounds = self.calibration_parameters_widget.getBounds()

        print('Known Values \n')
        print(self.calibration_parameters_widget.known_values)

        print('Bounds \n')
        print(bounds)

        print('Optimization History \n')
        print(self.calibration_plotting_widget.gens)
        print(self.calibration_plotting_widget.mins)

        print('Optimization parameters \n')
        print(
            'Population size = ',
            int(self.calibration_parameters_widget.pop_size)
            )  # Population size for GA (must be divisible by 4)
        print(
            'Number of generations = ',
            int(self.calibration_parameters_widget.num_gens)
            ) # Number of generations for GA
        print('Number of gradient iterations =',int(self.calibration_parameters_widget.num_iters))

        print('Final Optimization Error \n')
        print(self.optimization_error)

        data_to_export = {
            'population size':
                int(self.calibration_parameters_widget.pop_size),
            'number of generations':
                int(self.calibration_parameters_widget.num_gens),
            'number of gradient-based iterations':
                int(self.calibration_parameters_widget.num_iters),
            'optimization history (generations + iterations)':
                self.calibration_plotting_widget.gens,
            'optimization history (min objective value)':
                self.calibration_plotting_widget.mins,
            'final_error':
                self.optimization_error,
            'final_solution':
                self.calibration_parameters_widget.known_values,
            'bounds':
                bounds,
            'date':
                str(date.today()),
            }

        file_name = os.path.join(
            os.getcwd(),
            'output',
            str(date.today())+'_calibration.json'
            )


        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(
                data_to_export,
                file,
                ensure_ascii=False,
                indent=4
                )


if __name__ == "__main__":
    import sys

    cgitb.enable(format="text") #for more detailed traceback reports
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ex = App()
    sys.exit(app.exec_())

from application.mainfunction import *

if __name__ == "__main__": 
	QApplication.setAttribute(Qt.AA_EnableHighDpiScaling) 
	app = QApplication(sys.argv) 
	window = main_function()
	window.show()
	sys.exit(app.exec_())
	
import json
import logging

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QTreeWidgetItem
from PySide6.QtCore import QFile

from exception import UserInterfaceException


class UserInterface(QApplication):
    def __init__(self, args, ui_file_name, packet_manager) -> None:
        super().__init__(args)

        ui_file = QFile(ui_file_name)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        if not self.window:
            raise UserInterfaceException(f"Could not load window {loader.errorString()}")

        self.packet_manager = packet_manager
        self.packet_manager.ui_signal.connect(lambda signal: self.update_ui(signal))

        self.window.ping_button.clicked.connect(lambda arg: self.on_push_button_click(arg))
        self.window.new_file_button.clicked.connect(lambda arg: self.on_new_file_click(arg))
        self.window.edit_file_button.clicked.connect(lambda arg: self.on_edit_file_click(arg))
        self.window.move_file_button.clicked.connect(lambda arg: self.on_move_file_click(arg))
        self.window.delete_file_button.clicked.connect(lambda arg: self.on_delete_file_click(arg))
        self.window.directory.clicked.connect(lambda arg: self.on_tree_item_activated(arg))
        self.window.new_folder.clicked.connect(lambda arg: self.on_new_folder_click(arg))
        self.window.delete_2.clicked.connect(lambda arg: self.on_delete_click(arg))
        self.window.print_path.clicked.connect(lambda arg: self.on_print_path_click_click(arg))

        self.last_directory_item_clicked = None

    def decode_json(self, json_file, content):
        if json_file != "":
            content = json.loads(content)
            for arr in content:
                v = content[arr]
                for i in v:
                    a = v[i]
                    self.last_directory_item_clicked = None
                    while a['children'] != "":
                        new_item = QTreeWidgetItem()
                        new_item.setText(0, a['name'])
                        new_item.setText(1, a['type'])
                        new_item.setText(2, a['size'])
                        new_item.setText(3, a['path'])
                        new_item.setToolTip(0, a['name'])
                        if self.last_directory_item_clicked is None:
                            if a['type'] == "folder":
                                logging.info(f'Folder created!')
                            else:
                                logging.info(f'File created!')
                            self.window.directory.addTopLevelItem(new_item)
                        else:
                            if a['type'] == "folder":
                                logging.info(f'Folder created inside {self.last_directory_item_clicked.text(0)}')
                            else:
                                logging.info(f'File created inside {self.last_directory_item_clicked.text(0)}')
                            self.last_directory_item_clicked.addChild(new_item)

                        if len(a['children']) == 5 and list(a['children'].keys())[0] == 'name':
                            a = a['children']
                        else:
                            a = a['children']
                            self.last_directory_item_clicked = new_item
                            for c in a:
                                r = a[c]
                                while r != "":
                                    new_item = QTreeWidgetItem()
                                    new_item.setText(0, r['name'])
                                    new_item.setText(1, r['type'])
                                    new_item.setText(2, r['size'])
                                    new_item.setText(3, r['path'])
                                    new_item.setToolTip(0, r['name'])
                                    if self.last_directory_item_clicked is None:
                                        if r['type'] == "folder":
                                            logging.info(f'Folder created!')
                                        else:
                                            logging.info(f'File created!')
                                        self.window.directory.addTopLevelItem(new_item)
                                    else:
                                        if r['type'] == "folder":
                                            logging.info(
                                                f'Folder created inside {self.last_directory_item_clicked.text(0)}')
                                        else:
                                            logging.info(
                                                f'File created inside {self.last_directory_item_clicked.text(0)}')
                                        self.last_directory_item_clicked.addChild(new_item)

                                    if r['children'] != "":
                                        if len(r['children']) == 5 and list(r['children'].keys())[0] == 'name':
                                            r = r['children']
                                            self.last_directory_item_clicked = new_item
                                        else:
                                            r = r['children']
                                            self.last_directory_item_clicked = new_item
                                            for c2 in r:
                                                r2 = r[c2]
                                                while r2 != "":
                                                    new_item = QTreeWidgetItem()
                                                    new_item.setText(0, r2['name'])
                                                    new_item.setText(1, r2['type'])
                                                    new_item.setText(2, r2['size'])
                                                    new_item.setText(3, r2['path'])
                                                    new_item.setToolTip(0, r2['name'])
                                                    if self.last_directory_item_clicked is None:
                                                        if r2['type'] == "folder":
                                                            logging.info(f'Folder created!')
                                                        else:
                                                            logging.info(f'File created!')
                                                        self.window.directory.addTopLevelItem(new_item)
                                                    else:
                                                        if r2['type'] == "folder":
                                                            logging.info(
                                                                f'Folder created inside {self.last_directory_item_clicked.text(0)}')
                                                        else:
                                                            logging.info(
                                                                f'File created inside {self.last_directory_item_clicked.text(0)}')
                                                        self.last_directory_item_clicked.addChild(new_item)
                                                    if r2['children'] != "":
                                                        r2 = r2['children']
                                                    else:

                                                        break
                                            break
                                    else:
                                        break
                        if a != "" and (len(a) == 5 and list(a.keys())[0] == 'name'):
                            if a['children'] == "":
                                self.last_directory_item_clicked = new_item
                                last_new_item = QTreeWidgetItem()
                                last_new_item.setText(0, a['name'])
                                last_new_item.setText(1, a['type'])
                                last_new_item.setText(2, a['size'])
                                last_new_item.setText(3, a['path'])
                                new_item.setToolTip(0, a['name'])
                                if a['type'] == "Folder":
                                    logging.info(f'Folder created inside {self.last_directory_item_clicked.text(0)}')
                                else:
                                    logging.info(f'File created inside {self.last_directory_item_clicked.text(0)}')
                                self.last_directory_item_clicked.addChild(last_new_item)
                            else:
                                self.last_directory_item_clicked = new_item
                        else:
                            break

    def on_push_button_click(self, args):
        self.packet_manager.get_all_files(self.window.CON.isChecked())


    def update_ui(self, signal):
        #logging.info(signal.data)
        if signal.type == 'allFiles':
            self.window.directory.clear()
            self.decode_json(' ', signal.data)
            return
        if signal.type == 'file':
            self.window.fileEditor.insertPlainText(signal.data)

    def on_new_file_click(self, arg):
        if self.last_directory_item_clicked and self.last_directory_item_clicked.isSelected():
            if self.last_directory_item_clicked.text(1) == 'folder':
                logging.info(f'should create a file inside {self.last_directory_item_clicked.text(0)}')
                path = self.get_path()
                if path:
                    self.packet_manager.new_file(self.get_path() + "\\" + "new_file",self.window.CON.isChecked())
                    new_item = QTreeWidgetItem()
                    new_item.setText(0, 'new_file')
                    new_item.setText(1, 'file')
                    new_item.setText(2, 'new_file_size')
                    self.last_directory_item_clicked.addChild(new_item)
        else:
            logging.info(f'can not create a folder in a file !')
            new_item = QTreeWidgetItem()
            new_item.setText(0, 'new_file')
            new_item.setText(1, 'file')
            new_item.setText(2, 'new_file_size')
            self.window.directory.addTopLevelItem(new_item)

    def on_edit_file_click(self, arg):
        path = self.get_path()
        if path:
            self.packet_manager.get_file(path,self.window.CON.isChecked())


    path1 = path2 = file_name = ""

    def on_move_file_click(self, arg):
        global path1, path2, file_name
        press = 0
        if self.last_directory_item_clicked and self.last_directory_item_clicked.isSelected() and self.window.move_file_button.text() == "Move":
            path1 = self.last_directory_item_clicked.text(3) + "\\" + self.last_directory_item_clicked.text(0)
            file_name = self.last_directory_item_clicked.text(0)
            self.window.move_file_button.setText('Paste')
            self.last_directory_item_clicked = None
            press = 1

        if self.last_directory_item_clicked and self.last_directory_item_clicked.isSelected() and self.window.move_file_button.text() == "Paste":
            path2 = self.last_directory_item_clicked.text(3) + "\\" + self.last_directory_item_clicked.text(0)
            logging.info(f'Should move {file_name} from {path1} to {path2} !')
            self.window.move_file_button.setText('Move')
            self.packet_manager.move_file(path1, path2 + "\\" + file_name,self.window.CON.isChecked())
        elif self.window.move_file_button.text() == "Paste" and press != 1:
            path2 = "\\"
            self.window.move_file_button.setText('Move')
            logging.info(f'Should move {file_name} from {path1} to {path2} !')
            self.packet_manager.move_file(path1, path2 + "\\" + file_name,self.window.CON.isChecked())

    def on_delete_file_click(self, arg):
        path = self.get_path()
        if path:
            self.packet_manager.delete_file(path,self.window.CON.isChecked())

    def on_tree_item_activated(self, arg):
        self.last_directory_item_clicked = self.window.directory.selectedItems()[0]
        # TODO: validate interface

    def start(self):
        self.window.show()
        return self.exec()

    def on_new_folder_click(self, arg):
        if self.last_directory_item_clicked and self.last_directory_item_clicked.isSelected():
            if self.last_directory_item_clicked.text(1) != 'file':
                logging.info(f'should create a folder inside {self.last_directory_item_clicked.text(0)}')
                path = self.get_path()
                if path:
                    self.packet_manager.new_folder(self.get_path() + "\\" + "new_folder",self.window.CON.isChecked())
                    new_item = QTreeWidgetItem()
                    new_item.setText(0, 'new_folder')
                    new_item.setText(1, 'folder')
                    new_item.setText(2, '')
                    self.last_directory_item_clicked.addChild(new_item)
        else:
            logging.info(f'should create a folder outside')
            new_item = QTreeWidgetItem()
            new_item.setText(0, 'new_folder')
            new_item.setText(1, 'folder')
            new_item.setText(2, '')
            self.window.directory.addTopLevelItem(new_item)

    def on_delete_click(self, arg):
        if self.last_directory_item_clicked and self.last_directory_item_clicked.isSelected():
            logging.info(f'should delete a file inside {self.last_directory_item_clicked.text(0)}')
            parent = self.last_directory_item_clicked.parent()
            if parent:
                parent.removeChild(self.last_directory_item_clicked)
            else:
                self.window.directory.takeTopLevelItem(
                    self.window.directory.indexOfTopLevelItem(self.last_directory_item_clicked))

    def on_print_path_click_click(self, arg):
        if self.last_directory_item_clicked and self.last_directory_item_clicked.isSelected():
            self.window.pongLabel.setText(f'Path : {self.last_directory_item_clicked.text(3) + " " + self.last_directory_item_clicked.text(0) } ')

    def get_path(self):
        if self.last_directory_item_clicked and self.last_directory_item_clicked.isSelected():
            return self.last_directory_item_clicked.text(3) + "\\" + self.last_directory_item_clicked.text(0)
        return None

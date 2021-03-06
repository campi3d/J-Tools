# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Export selected Image Manager images in your specified file type
# coding: utf-8
# Written by Jorel Latraille
# ------------------------------------------------------------------------------
# DISCLAIMER & TERMS OF USE:
#
# Copyright (c) The Foundry 2014.
# All rights reserved.
#
# This software is provided as-is with use in commercial projects permitted.
# Redistribution in commercial projects is also permitted
# provided that the above copyright notice and this paragraph are
# duplicated in accompanying documentation,
# and acknowledge that the software was developed
# by The Foundry.  The name of the
# The Foundry may not be used to endorse or promote products derived
# from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

import mari, os
import PySide.QtGui as QtGui

version = "0.04"

USER_ROLE = 34

# ------------------------------------------------------------------------------
def exportImageManagerImages():
    "Export images from the image manager with either original extension or chosen extension to the path provided"
    if not isProjectSuitable():
        return

    file_types = ['.' + format for format in mari.images.supportedWriteFormats()]
    list.sort(file_types)
    dialog = exportImageManagerImagesUI(file_types)
    if dialog.exec_():
        export_path = dialog.getExportPath()
        image_list = dialog.getImagesToExport()
        combo_text = dialog.getComboText()
        mari.app.startProcessing('Exporting images...', len(image_list), can_cancel=False)
        for image in image_list:
            mari.app.stepProgress()
            image_object = image.data(USER_ROLE)
            for type_ in file_types:
                if image.text().endswith(type_):
                    image_name = image.text().split(type_)
                    image_name = "".join(image_name)
                    break
            image_object.saveAs(os.path.join(export_path, image_name + combo_text), None, 0)
        mari.app.stopProcessing()
        mari.utils.message("Export Complete.")        
        
# ------------------------------------------------------------------------------
class exportImageManagerImagesUI(QtGui.QDialog):
    #Create UI
    def __init__(self, file_types, parent=None):
        super(exportImageManagerImagesUI, self).__init__(parent)

        eimi_layout = QtGui.QVBoxLayout()
        self.setLayout(eimi_layout)
        self.setWindowTitle("Export Image Manager Images")
        
        #Create layout for middle section
        centre_layout = QtGui.QHBoxLayout()
        
        #Create images layout, label, and widget. Finally populate.
        images_layout = QtGui.QVBoxLayout()
        images_header_layout = QtGui.QHBoxLayout()
        images_label = QtGui.QLabel("<strong>Images</strong>")
        images_list = QtGui.QListWidget()
        images_list.setSelectionMode(images_list.ExtendedSelection)
        
        filter_box = QtGui.QLineEdit()
        mari.utils.connect(filter_box.textEdited, lambda: updateFilter(filter_box, images_list))
        
        images_header_layout.addWidget(images_label)
        images_header_layout.addStretch()
        images_search_icon = QtGui.QLabel()
        search_pixmap = QtGui.QPixmap(mari.resources.path(mari.resources.ICONS) + '/Lookup.png')
        images_search_icon.setPixmap(search_pixmap)
        images_header_layout.addWidget(images_search_icon)
        images_header_layout.addWidget(filter_box)
        
        image_list = []
        for image in mari.images.list():
            split_image_path = os.path.abspath(image.filePath()).split(os.sep)
            image_list.extend(split_image_path[-1:])    
        
        for image in mari.images.list():
            images_list.addItem("".join(os.path.abspath(image.filePath()).split(os.sep)[-1:]))
            images_list.item(images_list.count() - 1).setData(USER_ROLE, image)
        
        images_layout.addLayout(images_header_layout)
        images_layout.addWidget(images_list)
        
        #Create middle button section
        middle_button_layout = QtGui.QVBoxLayout()
        add_button = QtGui.QPushButton("+")
        remove_button = QtGui.QPushButton("-")
        middle_button_layout.addStretch()
        middle_button_layout.addWidget(add_button)
        middle_button_layout.addWidget(remove_button)
        middle_button_layout.addStretch()
        
        #Add wrapped QtGui.QListWidget with custom functions
        images_to_export_layout = QtGui.QVBoxLayout()
        images_to_export_label = QtGui.QLabel("<strong>Images to export</strong>")
        self.images_to_export = ImagesToExportList()
        images_to_export_layout.addWidget(images_to_export_label)
        images_to_export_layout.addWidget(self.images_to_export)
        
        #Hook up add/remove buttons
        remove_button.clicked.connect(self.images_to_export.removeImages)
        add_button.clicked.connect(lambda: self.images_to_export.addImages(images_list))

        #Add widgets to centre layout
        centre_layout.addLayout(images_layout)
        centre_layout.addLayout(middle_button_layout)
        centre_layout.addLayout(images_to_export_layout)

        #Add centre layout to main layout
        eimi_layout.addLayout(centre_layout)

        #Add bottom layout.
        bottom_layout = QtGui.QHBoxLayout()
        
        #Add file type options
        file_type_combo_text = QtGui.QLabel('File Types:')
        self.file_type_combo = QtGui.QComboBox()
        for file_type in file_types:
            self.file_type_combo.addItem(file_type)
        self.file_type_combo.setCurrentIndex(self.file_type_combo.findText('.tif'))
        
        #Add path line input and button
        path_label = QtGui.QLabel('Path:')
        self.path = QtGui.QLineEdit()
        path_pixmap = QtGui.QPixmap(mari.resources.path(mari.resources.ICONS) + '/ExportImages.png')
        icon = QtGui.QIcon(path_pixmap)
        path_button = QtGui.QPushButton(icon, "")
        path_button.clicked.connect(self.getPath)
        
        bottom_layout.addWidget(path_label)
        bottom_layout.addWidget(self.path)
        bottom_layout.addWidget(path_button)
        bottom_layout.addWidget(file_type_combo_text)
        bottom_layout.addWidget(self.file_type_combo)
        
        #Add OK Cancel buttons layout, buttons and add
        main_apply_button = QtGui.QPushButton("Apply")
        main_cancel_button = QtGui.QPushButton("Cancel")
        main_apply_button.clicked.connect(self.accepting)
        main_cancel_button.clicked.connect(self.reject)
        
        bottom_layout.addWidget(main_apply_button)
        bottom_layout.addWidget(main_cancel_button)
        
        #Add browse lines to main layout
        eimi_layout.addLayout(bottom_layout)

    def getPath(self):
        "Get export path and set the text in path LineEdit widget"
        file_path = mari.utils.misc.getExistingDirectory(caption='Export Path')
        if file_path == "":
            return
        else:
            self.path.setText(file_path)
    
    def accepting(self):
        if len(self.images_to_export.currentImageNames()) == 0:
            mari.utils.message('Please add some images to export.')
            return
        if self.path.text() == "":
            mari.utils.message('Please provide a path to export to.')
            return
        if not os.path.exists(os.path.abspath(self.path.text())):
            mari.utils.message('The path "%s" does not exist.' %(os.path.abspath(self.path.text())))
            return
        self.accept()
        
    def getExportPath(self):
        return os.path.abspath(r'%s' %self.path.text())
        
    def getImagesToExport(self):
        return self.images_to_export.currentImageNames()
        
    def getComboText(self):
        return self.file_type_combo.currentText()
    
# ------------------------------------------------------------------------------   
class ImagesToExportList(QtGui.QListWidget):
    "Stores a list of operations to perform."
    
    def __init__(self, title="For Export"):
        super(ImagesToExportList, self).__init__()
        self._title = title
        self.setSelectionMode(self.ExtendedSelection)
        
    def currentImages(self):
        return [self.item(index).data(USER_ROLE) for index in range(self.count())]
        
    def currentImageNames(self):
        return [self.item(index) for index in range(self.count())]
        
    def addImages(self, images_list):
        "Adds an operation from the current selections of images and directories."
        selected_items = images_list.selectedItems()
        
        # Add images that aren't already added
        current_images = set(self.currentImages())
        for item in selected_items:
            image = item.data(USER_ROLE)
            if image not in current_images:
                current_images.add(image)
                self.addItem(item.text())
                self.item(self.count() - 1).setData(USER_ROLE, image)
        
    def removeImages(self):
        "Removes any currently selected operations."
        for item in reversed(self.selectedItems()):     # reverse so indices aren't modified
            index = self.row(item)
            self.takeItem(index)
        
# ------------------------------------------------------------------------------
def updateFilter(filter_box, images_list):
    "For each item in the image list display, set it to hidden if it doesn't match the filter text."
    match_words = filter_box.text().lower().split()
    for item_index in range(images_list.count()):
        item = images_list.item(item_index)
        item_text_lower = item.text().lower()
        matches = all([word in item_text_lower for word in match_words])
        item.setHidden(not matches)

# ------------------------------------------------------------------------------
def isProjectSuitable():
    "Checks project state and Mari version."
    MARI_2_0V1_VERSION_NUMBER = 20001300    # see below
    if mari.app.version().number() >= MARI_2_0V1_VERSION_NUMBER:

        return True
        
    else:
        mari.utils.message("You can only run this script in Mari 2.0v1 or newer.")
        return False

# ------------------------------------------------------------------------------    
if __name__ == "__main__":
    exportImageManagerImages()

# ------------------------------------------------------------------------------
# Add action to Mari menu.
action = mari.actions.create(
    "Export Image Manager Images", "mari.jtools.exportImageManagerImages()"
    )
mari.menus.addAction(action, 'MainWindow/&Selection')
mari.menus.addSeparator('MainWindow/&Selection', 'Export Image Manager Images')
mari.menus.addAction(action, 'MriImageManager/ItemContext')
mari.menus.addSeparator('MriImageManager/ItemContext', 'Export Image Manager Images')
icon_filename = "SaveFileAs.png"
icon_path = mari.resources.path(mari.resources.ICONS) + '/' + icon_filename
action.setIconPath(icon_path)
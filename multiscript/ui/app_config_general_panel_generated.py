# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app_config_general_panel.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_GeneralAppConfigPanel(object):
    def setupUi(self, GeneralAppConfigPanel):
        if not GeneralAppConfigPanel.objectName():
            GeneralAppConfigPanel.setObjectName(u"GeneralAppConfigPanel")
        GeneralAppConfigPanel.resize(369, 89)
        self.verticalLayout = QVBoxLayout(GeneralAppConfigPanel)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.savePlansBeforeExecutionCheckBox = QCheckBox(GeneralAppConfigPanel)
        self.savePlansBeforeExecutionCheckBox.setObjectName(u"savePlansBeforeExecutionCheckBox")

        self.verticalLayout.addWidget(self.savePlansBeforeExecutionCheckBox)

        self.keepExistingTemplateFilesCheckBox = QCheckBox(GeneralAppConfigPanel)
        self.keepExistingTemplateFilesCheckBox.setObjectName(u"keepExistingTemplateFilesCheckBox")

        self.verticalLayout.addWidget(self.keepExistingTemplateFilesCheckBox)

        self.keepExistingOutputFilesCheckbox = QCheckBox(GeneralAppConfigPanel)
        self.keepExistingOutputFilesCheckbox.setObjectName(u"keepExistingOutputFilesCheckbox")

        self.verticalLayout.addWidget(self.keepExistingOutputFilesCheckbox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(GeneralAppConfigPanel)

        QMetaObject.connectSlotsByName(GeneralAppConfigPanel)
    # setupUi

    def retranslateUi(self, GeneralAppConfigPanel):
        GeneralAppConfigPanel.setWindowTitle(QCoreApplication.translate("GeneralAppConfigPanel", u"Form", None))
        self.savePlansBeforeExecutionCheckBox.setText(QCoreApplication.translate("GeneralAppConfigPanel", u"Save plans before executing them", None))
        self.keepExistingTemplateFilesCheckBox.setText(QCoreApplication.translate("GeneralAppConfigPanel", u"Keep existing template files instead of recreating them", None))
        self.keepExistingOutputFilesCheckbox.setText(QCoreApplication.translate("GeneralAppConfigPanel", u"Keep existing output files instead of recreating them", None))
    # retranslateUi


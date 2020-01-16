# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt, pyqtProperty, pyqtSlot
from UM.Qt.ListModel import ListModel
from cura import ApplicationMetadata
from UM.Logger import Logger
from typing import List, Dict, Any


class SubscribedPackagesModel(ListModel):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._items = []
        self._metadata = None
        self._discrepancies = None
        self._sdk_version = ApplicationMetadata.CuraSDKVersion

        self.addRoleName(Qt.UserRole + 1, "package_id")
        self.addRoleName(Qt.UserRole + 2, "display_name")
        self.addRoleName(Qt.UserRole + 3, "icon_url")
        self.addRoleName(Qt.UserRole + 4, "is_compatible")
        self.addRoleName(Qt.UserRole + 5, "is_dismissed")

    @pyqtProperty(bool, constant=True)
    def hasCompatiblePackages(self) -> bool:
        for item in self._items:
            if item['is_compatible']:
                return True
        return False

    @pyqtProperty(bool, constant=True)
    def hasIncompatiblePackages(self) -> bool:
        for item in self._items:
            if not item['is_compatible']:
                return True
        return False

        # Sets the "is_compatible" to True for the given package, in memory

    @pyqtSlot()
    def dismissPackage(self, package_id: str) -> None:
        package = self.find(key="package_id", value=package_id)
        if package != -1:
            self.setProperty(package, property="is_dismissed", value=True)
            Logger.debug("Package {} has been dismissed".format(package_id))

    def setMetadata(self, data: List[Dict[str, List[Any]]]) -> None:
        self._metadata = data

    def addDiscrepancies(self, discrepancy: List[str]) -> None:
        self._discrepancies = discrepancy

    def getCompatiblePackages(self):
        return [x for x in self._items if x["is_compatible"]]

    def initialize(self) -> None:
        self._items.clear()
        for item in self._metadata:
            if item["package_id"] not in self._discrepancies:
                continue
            package = {
                "package_id": item["package_id"],
                "display_name": item["display_name"],
                "sdk_versions": item["sdk_versions"],
                "download_url": item["download_url"],
                "md5_hash": item["md5_hash"],
                "is_dismissed": False,
            }
            if self._sdk_version not in item["sdk_versions"]:
                package.update({"is_compatible": False})
            else:
                package.update({"is_compatible": True})
            try:
                package.update({"icon_url": item["icon_url"]})
            except KeyError:  # There is no 'icon_url" in the response payload for this package
                package.update({"icon_url": ""})
            self._items.append(package)
        self.setItems(self._items)



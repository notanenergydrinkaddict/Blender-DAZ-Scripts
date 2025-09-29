// DAZ Studio version 4.24.0.3 filetype DAZ Script

// SPDX-License-Identifier: Apache-2.0
// Copyright Blender-DAZ-Scripts authors.

// Usage:
// Download and remove `.js` extension (.dsa.js becomes .dsa)
// Place into `C:\Users\Public\Documents\My DAZ 3D Library\Scripts`
// Select scene items in the overview window

// Do note that the Genesis Figures will be exported as empty.
// if you want to export a Genesis Figure,
// you will have to do a manual export for now.

// Once desired objects are selected,
// Run script from `"Content Library"`.

function _main() {
    var prog_name = "Batch OBJ Export";

    var oExportMgr = App.getExportMgr();
    if (!oExportMgr) {
        MessageBox.critical("oExportMgr is nullptr.", prog_name, "&OK");
        return;
    }

    var className = "DzObjExporter";
    var oExporter = oExportMgr.findExporterByClassName(className);
    if (!oExporter) {
        MessageBox.critical("Cannot find " + className + " Aborting.", prog_name, "&OK");
        return;
    }

    var nodes = Scene.getNodeList();
    var figures = [];

    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        var isSelected = node.isSelected();
        if (0 && isSelected) {
            print(node.className());
        }
        var isFigure = node.className() === "DzFigure";
        var isProp = node.className() === "DzNode";
        if (isSelected && (isFigure || isProp)) {
            figures.push(node);
        }
    }

    if (figures.length === 0) {
        MessageBox.critical("No selected figures found. Aborting.", prog_name, "&OK");
        return;
    }

    var originalVis = [];
    for (var i = 0; i < nodes.length; i++) {
        originalVis.push(nodes[i].isVisible());
    }
    var exportFolder = FileDialog.doDirectoryDialog("Select a Directory", "", oExportMgr.getExportPath());
    if (!exportFolder || exportFolder === "") {
        MessageBox.critical("No folder selected. Aborting.", prog_name, "&OK");
        return;
    }

    for (var i = 0; i < nodes.length; i++) {
        nodes[i].setVisible(false);
    }

    for (var f = 0; f < figures.length; f++) {
        var figure = figures[f];
        figure.setVisible(true);

        var fileName = exportFolder + "/" + figure.getName() + ".obj";
        print("Exporting:", fileName);

        var oSettings = new DzFileIOSettings();
        oSettings.setIntValue("FloatPrecision", "6");
        // Fill the settings object with the default options from the exporter
        // oExporter.getDefaultOptions( oSettings );

        // Set the desired settings for the exporter
        oSettings.setStringValue("Preset", "DAZ Studio (1 unit = 1cm)");

        // Do not write a material library
        oSettings.setBoolValue("WriteMtllib", false);
        // Do not collect texture maps
        oSettings.setBoolValue("CollectMaps", false);
        // Do not convert texture maps
        oSettings.setBoolValue("ConvertMaps", false);

        // Do not display the options dialog
        oSettings.setIntValue("RunSilent", 1);
        oExporter.writeFile(fileName, oSettings);
        figure.setVisible(false);
    }

    for (var i = 0; i < nodes.length; i++) {
        nodes[i].setVisible(originalVis[i]);
    }

    print("Done exporting all selected figures.");
}

_main();

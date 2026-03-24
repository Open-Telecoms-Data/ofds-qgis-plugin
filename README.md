# **OFDS Studio -  QGIS Plugin**
A QGIS plugin for creating, editing and interacting with OFDS (Open Fibre Data Standard) data. This is the first release of the plugin. It is an MVP (minimal viable product).

Feedback on its use is welcome via [GitHub issues](https://github.com/Open-Telecoms-Data/ofds-qgis-plugin/issues). To comment or create issues, you need to [sign up for a free GitHub account](https://github.com/signup). If you prefer to provide feedback privately, you can email info@opentelecomdata.net.

For more about the Open Fibre Data Standard, see [ofds.info](https://ofds.info).

**Contents**
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Create a new OFDS project](#create-a-new-ofds-project)
  - [Add and edit network features](#add-and-edit-network-features)
  - [Validate data](#validate-data)
  - [Save data](#save-data)
- [FAQs](#faqs)
- [Development](README.DEV.md)

## **Requirements**

QGIS 3.40 or higher. This was released in October 2024 and is currently (November 2025) the Long Term Version (LTS) release of QGIS.

## **Installation**

This guide assumes you are familiar with QGIS.

(EDIT AFTER #89 IS COMPLETE) 

### **Steps**

1. **Download the Plugin**
    * Click the green Code button of this repository
    * Download the latest `.zip` file (e.g., `ofds-qgis-plugin-v1.0.zip`)
2. **Open QGIS**
    * Start your QGIS application.
3. **Open the Plugin Manager**
    * From the main menu bar, click on **Plugins** > **Manage and Install Plugins...**.
4. **Install from ZIP**
    * In the `Plugins` window, click on the **Install from ZIP** tab on the left-hand side.
    * Click the **<code>...</code>** button next to the "ZIP file" field.
    * Navigate to the `.zip` file you downloaded in Step 1 and select it.
    * Click the **Install Plugin** button.
5. **Enable the Plugin**
    * After installation, you should see a message saying "Plugin installed successfully."
    * Go to the **Installed** tab and ensure the checkbox next to `Open Fibre` is ticked.
    * Close the `Plugins` window.
  
## Usage

### Create a new OFDS project
1. Select **Create OFDS GeoPackage** <img src="https://raw.githubusercontent.com/Open-Telecoms-Data/ofds-qgis-plugin/refs/heads/main/ofdsqgisplugin/button_add.svg">. 
2. Save the geopackage (.gpkg) file to your system. This creates an **Open Fibre** group of layers.
3. Add a base map for context. For example, from the **Browser panel** > **XYZ Tiles** drag the **OpenStreetMap** layer onto your map. Ensure the map is under the **Open Fibre** layer group.
4. To import existing OFDS JSON data:
    1. Select **Import JSON** <img src="https://raw.githubusercontent.com/Open-Telecoms-Data/ofds-qgis-plugin/refs/heads/main/ofdsqgisplugin/button_import_json.svg">. 
    2. Select and open your chosen OFDS JSON file. This adds network data to the **Open Fibre** layer group.

### Add and edit network features
Ensure that snapping is enabled. See the QGIS documentation on [snapping](https://docs.qgis.org/latest/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#snapping-and-digitizing-options).
Provide non-geographic network features first, so that they can be referenced from nodes and spans.

#### Add non-geographic network features
1. Select one of the **Open Fibre** layers: **networks**, **phases**, **organisations**, or **contracts**.
2. Select **Open Attribute Table**.
3. Select **Toggle editing mode** to enable editing.
4. Select **Add feature**.
5. Using the form view, provide information under the **Fields** tab. (Do not provide information under the **Relations** tab. The new feature must be saved to the layer before relations to other layers are added.)
6. Select **Save edits**.
7. Close the attribute table once you have finished adding features.
   
#### Add geographic features
1. Select one of the **Open Fibre** layers: **nodes** or **spans**.
2. Select **Toggle Editing** to enable editing.
3. Select **Add Point Feature** (nodes) or **Add Line Feature** and add your new point or line to the map. See the QGIS documentation on [adding features](https://docs.qgis.org/latest/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#adding-features).
4. The **Feature Attributes** form will appear once your feature is placed. Provide information under the **Field tab** and select **OK**. (Do not provide information under the **Relations** tab. The new feature must be saved to the layer before relations to other layers are added.)
5. Select **Save edits**.
   
#### Edit geographic features
1. Select the relevant **Open Fibre** layer: **nodes** or **spans**.
2. Select **Toggle Editing** to enable editing.
3. To move a feature:
    1. Select **Vertex Tool**.
    2. Tap or click the point, vertex or line segment, then tap or click again in a new position to move it.
4. To edit a feature's attributes:
    1. Select **Open Attribute Table**.
    2. Select the point or line to see its attributes.
    3. Using the form view, update the information under the **Fields* tab.
    4. Under the **Relations** tab, select **Link existing child feature(s)** to add an existing value to a field. (Do not use the **Add child feature** option.)
    5. To remove an existing value from a relations field, select it then select **Unlink selected child feature(s)**. (Do not use the **Delete selected child feature** option.)
5. To bulk edit multiple features' attributes:
    1. Select **Open Attribute Table**.
    2. Select **Toggle multi edit mode**.
    3. Update the information under the **Fields** and **Relations** tabs. See the QGIS documentation on [Editing multiple fields](https://docs.qgis.org/latest/en/docs/user_manual/working_with_vector/attribute_table.html#editing-multiple-fields).
    4. Select **apply changes**.
6. To delete a geographic feature:
    1. Select **Select Features by Area or Single Click**.
    2. Select the point or line.
    3. Select **Delete Selected**.
7. Select **Save edits**.
   
#### Edit non-geographic network features
1. Select one of the **Open Fibre** layers: **networks**, **phases**, **organisations**, or **contracts**.
2. Select **Open Attribute Table**.
3. Select a feature.
4. Update its information via the form view:
    1. Edit values under the **Fields** tab.
    2. Under the **Relations** tab, select **Link existing child feature(s)** to add an existing value to a field. (Do not use the **Add child feature** option.)
    3. To remove an existing value from a relations field, select it then select **Unlink selected child feature(s)**. (Do not use the **Delete selected child feature** option.)
4. To delete a feature, select the box to the left of its name then select **Delete selected features**.
5. Select **Save edits**.
   
### Validate data
* Select **Validate** <img src="https://raw.githubusercontent.com/Open-Telecoms-Data/ofds-qgis-plugin/refs/heads/main/ofdsqgisplugin/button_validate.svg">.
  
Validation errors will be presented in the **OFDS Validation Results** dialog. The message 'No errors found while validating OFDS data!' will appear if your OFDS GeoPackage data is valid.

### Save data
1. To export your project as OFDS JSON:
    1. Select **Export JSON** <img src="https://raw.githubusercontent.com/Open-Telecoms-Data/ofds-qgis-plugin/refs/heads/main/ofdsqgisplugin/button_export_json.svg">.
    2. Save the OFDS JSON file to your system.
2. To save your project as a GeoPackage: select **Project** > **Save To** > **GeoPackage**.
   
## FAQs

**How can I split a span into two spans?**

1. Select the **spans** layer.
2. Select **Toggle Editing** to enable editing.
3. Select **Split Features**. See the QGIS documentation on how to [split features](https://docs.qgis.org/3.44/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#split-features).
4. Update the attributes of the two spans. Ensure that **Identifier** and **Span name** values are distinct and that **Start** and **End** nodes are accurate.

**Can I add new codes to a codelist such as `nodeType`?**

Yes. To add codes to an open codelists like `nodeType`:
1. Select the relevant **codelist_open** layer.
2. Follow the **Add non-geographic network features** procedure above.

**Are the nodes referenced by the **Start** and **End** attributes of a span updated automatically, according to the geographical proximity of nodes?**

No. Currently these values must be manually updated.



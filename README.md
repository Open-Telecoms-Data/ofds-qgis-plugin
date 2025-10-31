# **Open Fibre Data Standard (OFDS) QGIS Plugin**

A QGIS plugin for creating, editing and interacting with OFDS data.


## **Installation**

This guide assumes you are familiar with QGIS.


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

Once installed you will see the OFDS buttons in the top right, with placeholder icons <img width="134" height="37" alt="Screenshot 2025-10-30 at 16 12 03" src="https://github.com/user-attachments/assets/5e08d065-ca3c-422e-b624-0ebd78d2829e" />



### **1. Initial Project Setup**



1. Create a new QGIS project.
2. Add a base map for context. You can drag the **OpenStreetMap** layer from the `XYZ Tiles` section in the **Browser** panel onto your map.
3. **Add OFDS Layers**: Click the **"Add Layers"** button on the plugin toolbar. This will add the necessary empty layers (Nodes, Spans, etc.) to your project, structured for the OFDS standard.


---


### **2. How to Use the Plugin**

You have two main workflows: creating a new dataset from scratch or editing an existing one.


#### **Workflow A: Create a New OFDS Dataset from Scratch**



1. **Add Features**:
    * Select a layer in the `Layers` panel ( "Nodes" or "Spans").
    * Click the **Toggle Editing** (pencil) icon in the QGIS toolbar.
    * Use the **Add Feature** tool to draw your new points or lines on the map.
2. **Edit Attributes**: When you finish drawing a feature, a form will pop up. Fill in the details. The plugin provides helpful dropdown menus with pre-defined codelist values for fields like:
    * Status
    * Node type
    * Access point
    * Power
    * Technologies, etc. 
3. **Save Edits**: When finished, click the **Toggle Editing** (pencil) icon again and save your changes.


#### **Workflow B: Edit an Existing OFDS Dataset**



1. **Import Data**: Click the **"Import"** button on the plugin toolbar.
2. Select an existing OFDS `.json` file from your computer.
3. The plugin will load all the data from that file into the correct layers.
4. **Edit Features**: Use the standard QGIS tools to modify the data as needed.


---


### **3. Validate and Export Your Data**

This is the final step for both workflows.



1. **Validate**: Before exporting, click the **"Validate"** button. This runs a check on your data and produces a report to help you find inconsistencies (e.g., a span that isn't connected to a node at both ends). The report is WIP. 
2. **Export**: Once your data is valid and complete, click the **"Export"** button. You can then save all your data as a new, OFDS-compliant `.json` file.



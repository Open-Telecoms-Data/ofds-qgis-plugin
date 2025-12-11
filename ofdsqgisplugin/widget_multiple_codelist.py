# many_to_many_widget.py
# Python attribute-form widget for editing many-to-many relations via a join table.
# Put this file in a location on QGIS' PYTHONPATH (example: ~/.local/share/QGIS/QGIS3/profiles/default/python/)
# Then configure the field's editor to use a Python widget with module "many_to_many_widget" and class "RelationDragDropWidget".
# Required widget configuration keys:
#   referenced_layer     : layer id OR layer name of the second (target) layer (string)
#   relation_layer       : layer id OR layer name of the relation (join) table (string)
#   left_fk              : field name in relation_layer that stores this (parent) layer's PK (string)
#   right_fk             : field name in relation_layer that stores referenced layer's PK (string)
#   ref_pk               : primary key field name of referenced_layer (string)
#   display_field        : field name in referenced_layer used for display (string)
#
# Example config (used by configure script below):
# {
#   'module': 'many_to_many_widget',
#   'class': 'RelationDragDropWidget',
#   'referenced_layer': 'children',       # layer name or id
#   'relation_layer': 'parents_children', # layer name or id
#   'left_fk': 'parent_id',
#   'right_fk': 'child_id',
#   'ref_pk': 'id',
#   'display_field': 'name'
# }

from qgis.PyQt import QtWidgets, QtCore
from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsFeatureRequest,
)

class RelationDragDropWidget(QtWidgets.QWidget):
    """
    Python attribute widget to manage many-to-many relations (via a relation table).

    QGIS will instantiate this widget with signature __init__(parent, widget_config)
    So we accept (parent, widget_config=None). QGIS typically passes the widget_config
    dictionary you set in the layer's editor setup as the second argument.
    """

    def __init__(self, parent=None, widget_config=None):
        super().__init__(parent)
        self.cfg = widget_config or {}
        self.project = QgsProject.instance()

        # internal state
        self._current_pk_value = None  # value of the parent feature's PK (left key)
        self.referenced_layer = self._resolve_layer(self.cfg.get('referenced_layer'))
        self.relation_layer = self._resolve_layer(self.cfg.get('relation_layer'))
        self.left_fk = self.cfg.get('left_fk')
        self.right_fk = self.cfg.get('right_fk')
        self.ref_pk = self.cfg.get('ref_pk')
        self.display_field = self.cfg.get('display_field')

        # Build UI
        self._build_ui()
        # populate referenced items into the combo
        self._populate_reference_combo()

        # If required config fields are missing, disable the widget and show a brief hint
        if not all([self.referenced_layer, self.relation_layer, self.left_fk, self.right_fk, self.ref_pk, self.display_field]):
            self._set_error_state("Widget configuration incomplete. See widget's docstring for required keys.")
        else:
            self._set_enabled_state(True)

    # ---------- QGIS attribute widget small API methods ----------
    def setValue(self, value):
        """
        QGIS calls this to put the attribute value into the editor.
        For this widget, the field this widget is attached to should be the parent layer's PK.
        setValue receives that PK value and we use it to query the relation table.
        """
        self._current_pk_value = value
        self._populate_current_list()

    def value(self):
        """
        QGIS calls this when it wants the value to write back into the field.
        This widget is attached to the parent's PK field; we don't change it here,
        just return the current value unchanged.
        """
        return self._current_pk_value

    # ---------- internal helpers ----------
    def _resolve_layer(self, identifier):
        """Accept either a layer id or a layer name. Return QgsVectorLayer or None."""
        if not identifier:
            return None
        # try by id
        layer = self.project.mapLayer(identifier)
        if layer:
            return layer
        # try by name (first match)
        layers = self.project.mapLayersByName(identifier)
        if layers:
            return layers[0]
        return None

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Current items area label
        lbl_current = QtWidgets.QLabel("Current items in relation:")
        layout.addWidget(lbl_current)

        # Scroll area with list of current items (each item will have remove button)
        self.current_list = QtWidgets.QListWidget()
        self.current_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        layout.addWidget(self.current_list, 1)

        # Horizontal layout for adding new items: a combo + add button
        h = QtWidgets.QHBoxLayout()
        self.ref_combo = QtWidgets.QComboBox()
        self.ref_combo.setMinimumWidth(250)
        self.ref_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        h.addWidget(self.ref_combo)

        self.btn_add = QtWidgets.QPushButton("Add")
        h.addWidget(self.btn_add)
        layout.addLayout(h)

        # Status / hint label
        self.hint_label = QtWidgets.QLabel()
        self.hint_label.setStyleSheet("color: gray;")
        layout.addWidget(self.hint_label)

        # Connect signals
        self.btn_add.clicked.connect(self._on_add_clicked)

    def _set_error_state(self, message):
        self._set_enabled_state(False)
        self.hint_label.setText(message)

    def _set_enabled_state(self, enabled):
        for w in (self.current_list, self.ref_combo, self.btn_add):
            w.setEnabled(enabled)

    def _populate_reference_combo(self):
        """
        Fill the combo with all features from referenced_layer using display_field.
        Combo item data stores the referenced PK.
        """
        self.ref_combo.clear()
        if not self.referenced_layer or not self.display_field or not self.ref_pk:
            return
        for feat in self.referenced_layer.getFeatures():
            disp = feat[self.display_field]
            pk = feat[self.ref_pk]
            # store PK as Qt user role data
            self.ref_combo.addItem(str(disp) if disp is not None else str(pk), pk)

    def _populate_current_list(self):
        """
        Query relation_layer for all rows where left_fk == self._current_pk_value,
        then populate the current_list with display names and remove buttons.
        """
        self.current_list.clear()
        if self._current_pk_value is None:
            self.hint_label.setText("Primary key for this feature is empty. Save the feature first to edit relations.")
            return

        if not self.relation_layer:
            return

        # find all relation features that link this parent PK to a referenced PK
        matches = []
        for rel_feat in self.relation_layer.getFeatures():
            val = rel_feat[self.left_fk]
            # direct comparison is used (supports numeric or string PK)
            if val == self._current_pk_value:
                ref_id = rel_feat[self.right_fk]
                matches.append((rel_feat.id(), ref_id))

        if not matches:
            self.hint_label.setText("No related items.")
            return
        else:
            self.hint_label.setText("")

        # For each match, show the referenced feature's display value and a remove button
        for rel_fid, ref_id in matches:
            # get display text
            ref_disp = self._lookup_ref_display(ref_id)
            item_widget = QtWidgets.QWidget()
            hl = QtWidgets.QHBoxLayout()
            hl.setContentsMargins(2, 0, 2, 0)
            lbl = QtWidgets.QLabel(str(ref_disp) if ref_disp is not None else str(ref_id))
            hl.addWidget(lbl)
            hl.addStretch()
            btn_rm = QtWidgets.QPushButton("Remove")
            btn_rm.setProperty("rel_fid", rel_fid)
            btn_rm.setProperty("ref_id", ref_id)
            btn_rm.clicked.connect(self._on_remove_clicked)
            hl.addWidget(btn_rm)
            item_widget.setLayout(hl)

            list_item = QtWidgets.QListWidgetItem(self.current_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.current_list.addItem(list_item)
            self.current_list.setItemWidget(list_item, item_widget)

    def _lookup_ref_display(self, ref_pk_value):
        """Return the display_field value for the referenced layer feature with ref_pk == ref_pk_value"""
        if not self.referenced_layer:
            return None
        # use a small filter request to avoid iterating whole layer if possible
        # build a request that filters the ref_pk field equal to ref_pk_value
        req = QgsFeatureRequest()
        # can't build expression robustly for all types, so iterate but short-circuit on match
        for f in self.referenced_layer.getFeatures():
            if f[self.ref_pk] == ref_pk_value:
                return f[self.display_field]
        return None

    def _on_add_clicked(self):
        """Create a new relation row in the relation_layer linking current PK to selected referenced PK."""
        if self._current_pk_value is None:
            QtWidgets.QMessageBox.warning(self, "Cannot add", "Primary key for this feature is empty. Save the feature first.")
            return

        idx = self.ref_combo.currentIndex()
        if idx < 0:
            return
        ref_pk_value = self.ref_combo.itemData(idx)

        # don't add duplicate relation rows: check if already exists
        for f in self.relation_layer.getFeatures():
            if f[self.left_fk] == self._current_pk_value and f[self.right_fk] == ref_pk_value:
                QtWidgets.QMessageBox.information(self, "Already exists", "That relation already exists.")
                return

        # prepare new feature
        new_feat = QgsFeature(self.relation_layer.fields())
        new_feat[self.left_fk] = self._current_pk_value
        new_feat[self.right_fk] = ref_pk_value

        # ensure relation layer is in edit mode and add
        if not self.relation_layer.isEditable():
            self.relation_layer.startEditing()
        ok = self.relation_layer.addFeature(new_feat)
        if not ok:
            QtWidgets.QMessageBox.critical(self, "Add failed", "Failed to add relation feature to relation table.")
            return
        # refresh list
        self._populate_current_list()

    def _on_remove_clicked(self):
        """Remove the relation row from relation_layer that corresponds to the clicked Remove button."""
        btn = self.sender()
        if btn is None:
            return
        rel_fid = btn.property("rel_fid")
        if rel_fid is None:
            # fallback: try to infer from ref_id and left_fk
            ref_id = btn.property("ref_id")
            to_delete = []
            for f in self.relation_layer.getFeatures():
                if f[self.left_fk] == self._current_pk_value and f[self.right_fk] == ref_id:
                    to_delete.append(f.id())
        else:
            to_delete = [rel_fid]

        if not to_delete:
            return

        if not self.relation_layer.isEditable():
            self.relation_layer.startEditing()
        ok = self.relation_layer.deleteFeatures(to_delete)
        if not ok:
            QtWidgets.QMessageBox.critical(self, "Delete failed", "Failed to delete relation feature(s).")
            return
        self._populate_current_list()

    # Optional but helpful when QGIS destroys widget:
    def closeEvent(self, event):
        # nothing special to do; allow normal close
        super().closeEvent(event)
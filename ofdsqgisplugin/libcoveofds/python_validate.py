# This file is very like
# https://github.com/Open-Telecoms-Data/lib-cove-ofds/blob/main/libcoveofds/python_validate.py
# and is heavily copied and pasted from there, with some changes to remove bits we don't need / can't use
#
# We can't just use the lib cove OFDS library directly sadly, using Python packages is very hard in QGIS :-(
#

from collections import defaultdict


class AdditionalCheckForNetwork:
    """Any check that wants to be provided should extend this abstract class and overwrite methods"""

    def __init__(self):
        self._additional_check_results: list = []

    def check_node_first_pass(self, node: dict, path: str):
        pass

    def check_span_first_pass(self, span: dict, path: str):
        pass

    def check_phase_first_pass(self, phase: dict, path: str):
        pass

    def check_organisation_first_pass(self, organisation: dict, path: str):
        pass

    def check_contract_first_pass(self, contract: dict, path: str):
        pass

    def check_node_second_pass(self, node: dict, path: str):
        pass

    def check_span_second_pass(self, span: dict, path: str):
        pass

    def check_phase_second_pass(self, phase: dict, path: str):
        pass

    def check_organisation_second_pass(self, organisation: dict, path: str):
        pass

    def check_contract_second_pass(self, contract: dict, path: str):
        pass

    def get_additional_check_results(self) -> list:
        return self._additional_check_results


class SpansMustHaveValidNodesAdditionalCheckForNetwork(AdditionalCheckForNetwork):
    def __init__(self):
        super().__init__()
        self._node_ids_seen: list = []

    def check_node_first_pass(self, node: dict, path: str):
        id = node.get("id")
        if id:
            self._node_ids_seen.append(id)

    def check_span_second_pass(self, span: dict, path: str):
        span_id = span.get("id")
        start = span.get("start")
        if start and isinstance(start, str) and not start in self._node_ids_seen:
            self._additional_check_results.append(
                {
                    "type": "span_start_node_not_found",
                    "missing_node_id": start,
                    "span_id": span_id,
                    "path": path + "/start",
                }
            )
        end = span.get("end")
        if end and isinstance(end, str) and not end in self._node_ids_seen:
            self._additional_check_results.append(
                {
                    "type": "span_end_node_not_found",
                    "missing_node_id": end,
                    "span_id": span_id,
                    "path": path + "/end",
                }
            )

    def skip_if_any_links_have_external_node_data(self) -> bool:
        return True

    def skip_if_any_links_have_external_span_data(self) -> bool:
        return True


class PhaseReferenceAdditionalCheckForNetwork(AdditionalCheckForNetwork):
    def __init__(self):
        super().__init__()
        self._phases: dict = {}

    def check_phase_first_pass(self, phase: dict, path: str):
        id = phase.get("id")
        name = phase.get("name")
        if id:
            self._phases[id] = name

    def check_node_second_pass(self, node: dict, path: str):
        if "phase" in node and isinstance(node["phase"], dict):
            self._check_related_phase_object(
                node["phase"],
                {
                    "type": "node_phase_reference_id_not_found",
                    "node_id": node.get("id"),
                    "path": path + "/phase/id",
                },
                {
                    "type": "node_phase_reference_name_does_not_match",
                    "node_id": node.get("id"),
                    "path": path + "/phase/name",
                },
                {
                    "type": "node_phase_reference_name_set_but_not_in_original",
                    "node_id": node.get("id"),
                    "path": path + "/phase/name",
                },
            )

    def check_span_second_pass(self, span: dict, path: str):
        if "phase" in span and isinstance(span["phase"], dict):
            self._check_related_phase_object(
                span["phase"],
                {
                    "type": "span_phase_reference_id_not_found",
                    "span_id": span.get("id"),
                    "path": path + "/phase/id",
                },
                {
                    "type": "span_phase_reference_name_does_not_match",
                    "span_id": span.get("id"),
                    "path": path + "/phase/name",
                },
                {
                    "type": "span_phase_reference_name_set_but_not_in_original",
                    "span_id": span.get("id"),
                    "path": path + "/phase/name",
                },
            )

    def check_contract_second_pass(self, contract: dict, path: str):
        if "relatedPhases" in contract and isinstance(contract["relatedPhases"], list):
            for related_phase_idx, related_phase in enumerate(
                contract["relatedPhases"]
            ):
                if isinstance(related_phase, dict):
                    self._check_related_phase_object(
                        related_phase,
                        {
                            "type": "contract_related_phase_reference_id_not_found",
                            "contract_id": contract.get("id"),
                            "path": path
                            + "/relatedPhases/"
                            + str(related_phase_idx)
                            + "/id",
                        },
                        {
                            "type": "contract_related_phase_reference_name_does_not_match",
                            "contract_id": contract.get("id"),
                            "path": path
                            + "/relatedPhases/"
                            + str(related_phase_idx)
                            + "/name",
                        },
                        {
                            "type": "contract_related_phase_reference_name_set_but_not_in_original",
                            "contract_id": contract.get("id"),
                            "path": path
                            + "/relatedPhases/"
                            + str(related_phase_idx)
                            + "/name",
                        },
                    )

    def _check_related_phase_object(
        self,
        related_phase: dict,
        id_not_found_result: dict,
        name_not_match_result: dict,
        name_set_but_not_in_original_result: dict,
    ):
        id = related_phase.get("id")
        name = related_phase.get("name")
        # id is required in JSON Schema - if it is not set we can let that validation raise an error.
        # We'll only carry on with our checks (those that can't be done in JSON Schema) if id exists.
        if id:
            if id in self._phases:
                # check - if name is set on reference but not on original
                if name and not self._phases[id]:
                    name_set_but_not_in_original_result.update(
                        {"name_in_reference": name}
                    )
                    self._additional_check_results.append(
                        name_set_but_not_in_original_result
                    )
                # check - if names are both set, do they match?
                if name and self._phases[id] and name != self._phases[id]:
                    name_not_match_result.update(
                        {"name_in_reference": name, "name_should_be": self._phases[id]}
                    )
                    self._additional_check_results.append(name_not_match_result)
            else:
                # check failed - id is not known
                id_not_found_result.update({"phase_id_not_found": id})
                self._additional_check_results.append(id_not_found_result)


class OrganisationReferenceAdditionalCheckForNetwork(AdditionalCheckForNetwork):
    def __init__(self):
        super().__init__()
        self._organisations: dict = {}

    def check_organisation_first_pass(self, organisation: dict, path: str):
        id = organisation.get("id")
        name = organisation.get("name")
        if id:
            self._organisations[id] = name

    def check_node_second_pass(self, node: dict, path: str):
        if "physicalInfrastructureProvider" in node and isinstance(
            node["physicalInfrastructureProvider"], dict
        ):
            self._check_related_organisation_object(
                node["physicalInfrastructureProvider"],
                {
                    "type": "node_organisation_reference_id_not_found",
                    "node_id": node.get("id"),
                    "field": "physicalInfrastructureProvider",
                    "path": path + "/physicalInfrastructureProvider/id",
                },
                {
                    "type": "node_organisation_reference_name_does_not_match",
                    "node_id": node.get("id"),
                    "field": "physicalInfrastructureProvider",
                    "path": path + "/physicalInfrastructureProvider/name",
                },
                {
                    "type": "node_organisation_reference_name_set_but_not_in_original",
                    "node_id": node.get("id"),
                    "field": "physicalInfrastructureProvider",
                    "path": path + "/physicalInfrastructureProvider/name",
                },
            )
        if "networkProviders" in node and isinstance(node["networkProviders"], list):
            for network_provider_idx, network_provider in enumerate(
                node["networkProviders"]
            ):
                if isinstance(network_provider, dict):
                    self._check_related_organisation_object(
                        network_provider,
                        {
                            "type": "node_organisation_reference_id_not_found",
                            "node_id": node.get("id"),
                            "field": "networkProviders",
                            "path": path
                            + "/networkProviders/"
                            + str(network_provider_idx)
                            + "/id",
                        },
                        {
                            "type": "node_organisation_reference_name_does_not_match",
                            "node_id": node.get("id"),
                            "field": "networkProviders",
                            "path": path
                            + "/networkProviders/"
                            + str(network_provider_idx)
                            + "/name",
                        },
                        {
                            "type": "node_organisation_reference_name_set_but_not_in_original",
                            "node_id": node.get("id"),
                            "field": "networkProviders",
                            "path": path
                            + "/networkProviders/"
                            + str(network_provider_idx)
                            + "/name",
                        },
                    )

    def check_span_second_pass(self, span: dict, path: str):
        if "physicalInfrastructureProvider" in span and isinstance(
            span["physicalInfrastructureProvider"], dict
        ):
            self._check_related_organisation_object(
                span["physicalInfrastructureProvider"],
                {
                    "type": "span_organisation_reference_id_not_found",
                    "span_id": span.get("id"),
                    "field": "physicalInfrastructureProvider",
                    "path": path + "/physicalInfrastructureProvider/id",
                },
                {
                    "type": "span_organisation_reference_name_does_not_match",
                    "span_id": span.get("id"),
                    "field": "physicalInfrastructureProvider",
                    "path": path + "/physicalInfrastructureProvider/name",
                },
                {
                    "type": "span_organisation_reference_name_set_but_not_in_original",
                    "span_id": span.get("id"),
                    "field": "physicalInfrastructureProvider",
                    "path": path + "/physicalInfrastructureProvider/name",
                },
            )
        if "networkProviders" in span and isinstance(span["networkProviders"], list):
            for network_provider_idx, network_provider in enumerate(
                span["networkProviders"]
            ):
                if isinstance(network_provider, dict):
                    self._check_related_organisation_object(
                        network_provider,
                        {
                            "type": "span_organisation_reference_id_not_found",
                            "span_id": span.get("id"),
                            "field": "networkProviders",
                            "path": path
                            + "/networkProviders/"
                            + str(network_provider_idx)
                            + "/id",
                        },
                        {
                            "type": "span_organisation_reference_name_does_not_match",
                            "span_id": span.get("id"),
                            "field": "networkProviders",
                            "path": path
                            + "/networkProviders/"
                            + str(network_provider_idx)
                            + "/name",
                        },
                        {
                            "type": "span_organisation_reference_name_set_but_not_in_original",
                            "span_id": span.get("id"),
                            "field": "networkProviders",
                            "path": path
                            + "/networkProviders/"
                            + str(network_provider_idx)
                            + "/name",
                        },
                    )
        if "supplier" in span and isinstance(span["supplier"], dict):
            self._check_related_organisation_object(
                span["supplier"],
                {
                    "type": "span_organisation_reference_id_not_found",
                    "span_id": span.get("id"),
                    "field": "supplier",
                    "path": path + "/supplier/id",
                },
                {
                    "type": "span_organisation_reference_name_does_not_match",
                    "span_id": span.get("id"),
                    "field": "supplier",
                    "path": path + "/supplier/name",
                },
                {
                    "type": "span_organisation_reference_name_set_but_not_in_original",
                    "span_id": span.get("id"),
                    "field": "supplier",
                    "path": path + "/supplier/name",
                },
            )

    def check_phase_second_pass(self, phase: dict, path: str):
        if "funders" in phase and isinstance(phase["funders"], list):
            for funder_idx, funder in enumerate(phase["funders"]):
                if isinstance(funder, dict):
                    self._check_related_organisation_object(
                        funder,
                        {
                            "type": "phase_organisation_reference_id_not_found",
                            "phase_id": phase.get("id"),
                            "path": path + "/funders/" + str(funder_idx) + "/id",
                        },
                        {
                            "type": "phase_organisation_reference_name_does_not_match",
                            "phase_id": phase.get("id"),
                            "path": path + "/funders/" + str(funder_idx) + "/name",
                        },
                        {
                            "type": "phase_organisation_reference_name_set_but_not_in_original",
                            "phase_id": phase.get("id"),
                            "path": path + "/funders/" + str(funder_idx) + "/name",
                        },
                    )

    def _check_related_organisation_object(
        self,
        related_organisation: dict,
        id_not_found_result: dict,
        name_not_match_result: dict,
        name_set_but_not_in_original_result: dict,
    ):
        id = related_organisation.get("id")
        name = related_organisation.get("name")
        # id is required in JSON Schema - if it is not set we can let that validation raise an error.
        # We'll only carry on with our checks (those that can't be done in JSON Schema) if id exists.
        if id:
            if id in self._organisations:
                # check - if name is set on reference but not on original
                if name and not self._organisations[id]:
                    name_set_but_not_in_original_result.update(
                        {"name_in_reference": name}
                    )
                    self._additional_check_results.append(
                        name_set_but_not_in_original_result
                    )
                # check - if names are both set, do they match?
                if name and self._organisations[id] and name != self._organisations[id]:
                    name_not_match_result.update(
                        {
                            "name_in_reference": name,
                            "name_should_be": self._organisations[id],
                        }
                    )
                    self._additional_check_results.append(name_not_match_result)
            else:
                # check failed - id is not known
                id_not_found_result.update({"organisation_id_not_found": id})
                self._additional_check_results.append(id_not_found_result)


class IsNodeUsedInSpanAdditionalCheckForNetwork(AdditionalCheckForNetwork):
    def __init__(self):
        super().__init__()
        self._node_ids_used_in_spans: list = []

    def check_span_first_pass(self, span: dict, path: str):
        start = span.get("start")
        if start and start not in self._node_ids_used_in_spans:
            self._node_ids_used_in_spans.append(start)
        end = span.get("end")
        if end and end not in self._node_ids_used_in_spans:
            self._node_ids_used_in_spans.append(end)

    def check_node_second_pass(self, node: dict, path: str):
        id = node.get("id")
        if id and id not in self._node_ids_used_in_spans:
            self._additional_check_results.append(
                {
                    "type": "node_not_used_in_any_spans",
                    "node_id": node.get("id"),
                    "path": path,
                }
            )

    def skip_if_any_links_have_external_node_data(self) -> bool:
        return True

    def skip_if_any_links_have_external_span_data(self) -> bool:
        return True


class UniqueIDsAdditionalCheckForNetwork(AdditionalCheckForNetwork):
    def __init__(self):
        super().__init__()
        self._node_ids_seen: defaultdict = defaultdict(list)
        self._span_ids_seen: defaultdict = defaultdict(list)
        self._phase_ids_seen: defaultdict = defaultdict(list)
        self._organisation_ids_seen: defaultdict = defaultdict(list)
        self._contract_ids_seen: defaultdict = defaultdict(list)

    def check_node_first_pass(self, node: dict, path: str):
        id = node.get("id")
        if id and isinstance(id, str):
            self._node_ids_seen[id].append(path)

    def check_span_first_pass(self, span: dict, path: str):
        id = span.get("id")
        if id and isinstance(id, str):
            self._span_ids_seen[id].append(path)

    def check_phase_first_pass(self, phase: dict, path: str):
        id = phase.get("id")
        if id and isinstance(id, str):
            self._phase_ids_seen[id].append(path)

    def check_organisation_first_pass(self, organisation: dict, path: str):
        id = organisation.get("id")
        if id and isinstance(id, str):
            self._organisation_ids_seen[id].append(path)

    def check_contract_first_pass(self, contract: dict, path: str):
        id = contract.get("id")
        if id and isinstance(id, str):
            self._contract_ids_seen[id].append(path)

    def get_additional_check_results(self) -> list:
        out: list = []
        for id, paths in self._node_ids_seen.items():
            if len(paths) > 1:
                for path in paths:
                    out.append(
                        {
                            "type": "duplicate_node_id",
                            "node_id": id,
                            "path": path + "/id",
                        }
                    )
        for id, paths in self._span_ids_seen.items():
            if len(paths) > 1:
                for path in paths:
                    out.append(
                        {
                            "type": "duplicate_span_id",
                            "span_id": id,
                            "path": path + "/id",
                        }
                    )
        for id, paths in self._phase_ids_seen.items():
            if len(paths) > 1:
                for path in paths:
                    out.append(
                        {
                            "type": "duplicate_phase_id",
                            "phase_id": id,
                            "path": path + "/id",
                        }
                    )
        for id, paths in self._organisation_ids_seen.items():
            if len(paths) > 1:
                for path in paths:
                    out.append(
                        {
                            "type": "duplicate_organisation_id",
                            "organisation_id": id,
                            "path": path + "/id",
                        }
                    )
        for id, paths in self._contract_ids_seen.items():
            if len(paths) > 1:
                for path in paths:
                    out.append(
                        {
                            "type": "duplicate_contract_id",
                            "contract_id": id,
                            "path": path + "/id",
                        }
                    )
        return out

    def skip_if_any_links_have_external_node_data(self) -> bool:
        return False

    def skip_if_any_links_have_external_span_data(self) -> bool:
        return False


class GeometryTopologyAdditionalCheckForNetwork(AdditionalCheckForNetwork):
    """Validates that span geometry actually touches node geometry.
    
    This check ensures that the physical geometry of spans (LineStrings) 
    actually connects to the nodes they reference via start/end fields.
    This is critical for network topology integrity.
    """
    
    def __init__(self, tolerance=0.00001):
        """
        Args:
            tolerance: Distance tolerance in CRS units (degrees for WGS84).
                      0.00001 degrees ≈ 1.1 meters at equator.
                      This allows for minor GPS/digitizing inaccuracies.
        """
        super().__init__()
        self._tolerance = tolerance
        self._node_geometries = {}  # node_id -> (lon, lat)
    
    def check_node_first_pass(self, node: dict, path: str):
        """Collect node locations from geometry field."""
        node_id = node.get("id")
        geom = node.get("geometry")
        
        if node_id and geom:
            # GeoJSON Point geometry has coordinates as [lon, lat]
            coords = geom.get("coordinates", [])
            if isinstance(coords, list) and len(coords) >= 2:
                self._node_geometries[node_id] = (coords[0], coords[1])
    
    def check_span_second_pass(self, span: dict, path: str):
        """Verify span endpoints touch their corresponding nodes."""
        span_id = span.get("id")
        start_node_id = span.get("start")
        end_node_id = span.get("end")
        geom = span.get("geometry")
        
        # Skip if no geometry or not a LineString
        if not geom or geom.get("type") != "LineString":
            return
        
        coords = geom.get("coordinates", [])
        if not isinstance(coords, list) or len(coords) < 2:
            return
        
        # Check start point touches start node
        if start_node_id and start_node_id in self._node_geometries:
            node_coords = self._node_geometries[start_node_id]
            span_start = coords[0]
            
            if isinstance(span_start, list) and len(span_start) >= 2:
                distance = self._calculate_distance(
                    span_start[0], span_start[1],
                    node_coords[0], node_coords[1]
                )
                
                if distance > self._tolerance:
                    self._additional_check_results.append({
                        "type": "span_geometry_not_touching_start_node",
                        "span_id": span_id,
                        "node_id": start_node_id,
                        "distance": distance,
                        "tolerance": self._tolerance,
                        "path": path + "/geometry/coordinates/0"
                    })
        
        # Check end point touches end node
        if end_node_id and end_node_id in self._node_geometries:
            node_coords = self._node_geometries[end_node_id]
            span_end = coords[-1]
            
            if isinstance(span_end, list) and len(span_end) >= 2:
                distance = self._calculate_distance(
                    span_end[0], span_end[1],
                    node_coords[0], node_coords[1]
                )
                
                if distance > self._tolerance:
                    self._additional_check_results.append({
                        "type": "span_geometry_not_touching_end_node",
                        "span_id": span_id,
                        "node_id": end_node_id,
                        "distance": distance,
                        "tolerance": self._tolerance,
                        "path": path + "/geometry/coordinates/-1"
                    })
    
    def _calculate_distance(self, x1, y1, x2, y2):
        """Calculate Euclidean distance between two points.
        
        Note: For WGS84 coordinates, this is an approximation that works
        well for small distances. For more accuracy over large distances,
        consider using the Haversine formula.
        """
        import math
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def skip_if_any_links_have_external_node_data(self) -> bool:
        return True
    
    def skip_if_any_links_have_external_span_data(self) -> bool:
        return True


class DanglingSpansAdditionalCheckForNetwork(AdditionalCheckForNetwork):
    """Detects spans that don't connect to nodes on both ends.
    
    A 'dangling' span is one that is missing a start or end node reference.
    This is a topology error that indicates incomplete network data.
    
    Spans with status 'planned' or 'underConstruction' are exempt from this
    check, as it's common for planned infrastructure to have incomplete
    connectivity information.
    """
    
    # Statuses where dangling spans are acceptable
    ALLOWED_DANGLING_STATUSES = ['planned', 'underConstruction']
    
    def __init__(self):
        super().__init__()
        self._node_ids = set()
    
    def check_node_first_pass(self, node: dict, path: str):
        """Collect all valid node IDs."""
        node_id = node.get("id")
        if node_id:
            self._node_ids.add(node_id)
    
    def check_span_second_pass(self, span: dict, path: str):
        """Check if span has both start and end node references."""
        span_id = span.get("id")
        status = span.get("status", "")
        start_node = span.get("start")
        end_node = span.get("end")
        
        # Skip validation for planned/under construction spans
        if status in self.ALLOWED_DANGLING_STATUSES:
            return
        
        # Check for missing start node reference
        if not start_node:
            self._additional_check_results.append({
                "type": "dangling_span_missing_start",
                "span_id": span_id,
                "status": status if status else "(no status)",
                "path": path + "/start"
            })
        
        # Check for missing end node reference
        if not end_node:
            self._additional_check_results.append({
                "type": "dangling_span_missing_end",
                "span_id": span_id,
                "status": status if status else "(no status)",
                "path": path + "/end"
            })
    
    def skip_if_any_links_have_external_node_data(self) -> bool:
        return False
    
    def skip_if_any_links_have_external_span_data(self) -> bool:
        return False


class SelfIntersectionAdditionalCheckForNetwork(AdditionalCheckForNetwork):
    """Detects self-intersecting span geometries.
    
    A self-intersecting LineString is one where non-adjacent line segments
    cross each other. This is typically a digitizing error and can cause
    problems with network analysis and routing algorithms.
    
    Note: This check uses a computational geometry algorithm that compares
    all non-adjacent segment pairs. For very complex geometries with many
    vertices, this could be slow (O(n²) complexity).
    """
    
    def check_span_first_pass(self, span: dict, path: str):
        """Check if span geometry self-intersects."""
        span_id = span.get("id")
        geom = span.get("geometry")
        
        # Skip if no geometry or not a LineString
        if not geom or geom.get("type") != "LineString":
            return
        
        coords = geom.get("coordinates", [])
        
        # Need at least 4 points to have non-adjacent segments that could intersect
        # (segments 0-1 and 2-3 are the minimum for a self-intersection)
        if not isinstance(coords, list) or len(coords) < 4:
            return
        
        # Check for self-intersection using line segment intersection algorithm
        if self._has_self_intersection(coords):
            self._additional_check_results.append({
                "type": "span_self_intersection",
                "span_id": span_id,
                "vertex_count": len(coords),
                "path": path + "/geometry"
            })
    
    def _has_self_intersection(self, coords):
        """Check if a LineString self-intersects.
        
        Uses the CCW (counter-clockwise) algorithm to detect if any two
        non-adjacent line segments intersect.
        
        Args:
            coords: List of [lon, lat] coordinate pairs
            
        Returns:
            True if the LineString self-intersects, False otherwise
        """
        n = len(coords)
        
        # Check if this is a closed ring (first and last points are the same)
        is_closed_ring = (
            len(coords) >= 3 and
            coords[0][0] == coords[-1][0] and 
            coords[0][1] == coords[-1][1]
        )
        
        # Compare each segment with all non-adjacent segments
        for i in range(n - 1):
            # Start j at i+2 to skip adjacent segments (they share a vertex)
            for j in range(i + 2, n - 1):
                # For closed rings, skip comparing the first and last segments
                # because they share the closing vertex (not a real intersection)
                if is_closed_ring and i == 0 and j == n - 2:
                    continue
                
                # Check if segments (i, i+1) and (j, j+1) intersect
                if self._segments_intersect(
                    coords[i], coords[i + 1],
                    coords[j], coords[j + 1]
                ):
                    return True
        
        return False
    
    def _segments_intersect(self, p1, p2, p3, p4):
        """Check if line segment p1-p2 intersects with segment p3-p4.
        
        Uses the CCW (counter-clockwise) orientation test. Two segments
        intersect if and only if:
        - Points p1 and p2 are on opposite sides of the line through p3-p4, AND
        - Points p3 and p4 are on opposite sides of the line through p1-p2
        
        Args:
            p1, p2: Endpoints of first segment as [x, y] lists
            p3, p4: Endpoints of second segment as [x, y] lists
            
        Returns:
            True if segments intersect (cross each other), False otherwise
        """
        def ccw(A, B, C):
            """Check if three points are in counter-clockwise order.
            
            Returns True if the path A->B->C turns counter-clockwise,
            False if it turns clockwise or is collinear.
            """
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        # Segments intersect if p1,p2 are on opposite sides of p3-p4
        # AND p3,p4 are on opposite sides of p1-p2
        return (ccw(p1, p3, p4) != ccw(p2, p3, p4) and 
                ccw(p1, p2, p3) != ccw(p1, p2, p4))
    
    def skip_if_any_links_have_external_node_data(self) -> bool:
        return True
    
    def skip_if_any_links_have_external_span_data(self) -> bool:
        return True


ADDITIONAL_CHECK_CLASSES_FOR_NETWORK = [
    SpansMustHaveValidNodesAdditionalCheckForNetwork,
    PhaseReferenceAdditionalCheckForNetwork,
    OrganisationReferenceAdditionalCheckForNetwork,
    IsNodeUsedInSpanAdditionalCheckForNetwork,
    UniqueIDsAdditionalCheckForNetwork,
    GeometryTopologyAdditionalCheckForNetwork,
    DanglingSpansAdditionalCheckForNetwork,
    SelfIntersectionAdditionalCheckForNetwork,
]


class PythonValidate:
    """Validates data using additional checks custom written in Python"""

    def validate(self, json_data: dict) -> list:
        """Call with data. Results are returned."""

        additional_checks: list = []

        # For each Network
        networks = json_data.get("networks")
        if isinstance(networks, list):
            for network_idx, network in enumerate(networks):
                if isinstance(network, dict):
                    additional_check_instances = [
                        x() for x in ADDITIONAL_CHECK_CLASSES_FOR_NETWORK
                    ]
                    nodes = network.get("nodes", [])
                    nodes = nodes if isinstance(nodes, list) else []
                    spans = network.get("spans", [])
                    spans = spans if isinstance(spans, list) else []
                    phases = network.get("phases", [])
                    phases = phases if isinstance(phases, list) else []
                    organisations = network.get("organisations", [])
                    organisations = (
                        organisations if isinstance(organisations, list) else []
                    )
                    contracts = network.get("contracts", [])
                    contracts = contracts if isinstance(contracts, list) else []
                    # First pass
                    for additional_check_instance in additional_check_instances:
                        for node_idx, node in enumerate(nodes):
                            additional_check_instance.check_node_first_pass(
                                node,
                                "/networks/"
                                + str(network_idx)
                                + "/nodes/"
                                + str(node_idx),
                            )
                        for span_idx, span in enumerate(spans):
                            additional_check_instance.check_span_first_pass(
                                span,
                                "/networks/"
                                + str(network_idx)
                                + "/spans/"
                                + str(span_idx),
                            )
                        for phase_idx, phase in enumerate(phases):
                            additional_check_instance.check_phase_first_pass(
                                phase,
                                "/networks/"
                                + str(network_idx)
                                + "/phases/"
                                + str(phase_idx),
                            )
                        for organisation_idx, organisation in enumerate(organisations):
                            additional_check_instance.check_organisation_first_pass(
                                organisation,
                                "/networks/"
                                + str(network_idx)
                                + "/organisations/"
                                + str(organisation_idx),
                            )
                        for contract_idx, contract in enumerate(contracts):
                            additional_check_instance.check_contract_first_pass(
                                contract,
                                "/networks/"
                                + str(network_idx)
                                + "/contracts/"
                                + str(contract_idx),
                            )
                    # Second pass
                    for additional_check_instance in additional_check_instances:
                        for node_idx, node in enumerate(nodes):
                            additional_check_instance.check_node_second_pass(
                                node,
                                "/networks/"
                                + str(network_idx)
                                + "/nodes/"
                                + str(node_idx),
                            )
                        for span_idx, span in enumerate(spans):
                            additional_check_instance.check_span_second_pass(
                                span,
                                "/networks/"
                                + str(network_idx)
                                + "/spans/"
                                + str(span_idx),
                            )
                        for phase_idx, phase in enumerate(phases):
                            additional_check_instance.check_phase_second_pass(
                                phase,
                                "/networks/"
                                + str(network_idx)
                                + "/phases/"
                                + str(phase_idx),
                            )
                        for organisation_idx, organisation in enumerate(organisations):
                            additional_check_instance.check_organisation_second_pass(
                                organisation,
                                "/networks/"
                                + str(network_idx)
                                + "/organisations/"
                                + str(organisation_idx),
                            )
                        for contract_idx, contract in enumerate(contracts):
                            additional_check_instance.check_contract_second_pass(
                                contract,
                                "/networks/"
                                + str(network_idx)
                                + "/contracts/"
                                + str(contract_idx),
                            )
                    # Results
                    for additional_check_instance in additional_check_instances:
                        for (
                            additional_check
                        ) in additional_check_instance.get_additional_check_results():
                            additional_check["network_id"] = network.get("id")
                            additional_checks.append(additional_check)

        # Return
        return additional_checks

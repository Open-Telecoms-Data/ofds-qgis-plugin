# This file is very like
# https://github.com/Open-Telecoms-Data/lib-cove-ofds/blob/main/libcoveofds/python_validate.py
# and is heavily copied and pasted from there, with some changes to remove bits we don't need / can't use
#
# We can't just use the lib cove OFDS library directly sadly, using Python packages is very hard in QGIS :-(
#


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


ADDITIONAL_CHECK_CLASSES_FOR_NETWORK = [
    SpansMustHaveValidNodesAdditionalCheckForNetwork,
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

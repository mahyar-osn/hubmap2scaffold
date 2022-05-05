import random

from opencmiss.zinc.context import Context
from opencmiss.zinc.field import FieldGroup
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node

from opencmiss.utils.zinc.field import create_field_coordinates, find_or_create_field_group
from opencmiss.utils.zinc.general import create_node as create_zinc_node
from opencmiss.utils.zinc.general import ChangeManager
from opencmiss.zinc.status import OK as ZINC_OK


def write_ex(file_name, data):
    context = Context("SPARC Heart Scaffold")
    region = context.getDefaultRegion()
    load(region, data)
    region.writeFile(file_name)


def get_coordinates(ex_file):
    context = Context("HubMap Data")
    region = context.getDefaultRegion()
    region.readFile(ex_file)
    field_module = region.getFieldmodule()
    coordinate_field = field_module.findFieldByName("coordinates")

    with ChangeManager(field_module):
        field_cache = field_module.createFieldcache()
        node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        if node_set.getSize() == 0:
            del node_set
            node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        data_array = list()
        node_template = node_set.createNodetemplate()
        node_template.defineField(coordinate_field)
        node_iter = node_set.createNodeiterator()
        node = node_iter.next()
        fe_field = coordinate_field.castFiniteElement()
        node_counter = 0
        while node.isValid():
            node_template.defineFieldFromNode(fe_field, node)
            field_cache.setNode(node)
            result, values = fe_field.getNodeParameters(field_cache, -1, Node.VALUE_LABEL_VALUE, 1, 3)
            assert result == ZINC_OK, "Failed to get coordinates of the data."
            data_array.append(values)
            node_counter += 1
            node = node_iter.next()

    return data_array


def load(region, data):
    field_module = region.getFieldmodule()
    create_field_coordinates(field_module)

    for surface, points in data.items():
        points = random.sample(points, int(len(points)*0.1))
        node_identifiers = create_nodes(field_module, points)
        create_group_nodes(field_module, surface, node_identifiers, node_set_name='datapoints')


def create_nodes(field_module, embedded_lists, node_set_name='datapoints'):
    node_identifiers = []
    for pt in embedded_lists:
        if isinstance(pt, list):
            node_ids = create_nodes(field_module, pt, node_set_name=node_set_name)
            node_identifiers.extend(node_ids)
        else:
            local_node_id = create_zinc_node(field_module, pt, node_set_name=node_set_name)
            node_identifiers.append(local_node_id)

    return node_identifiers


def create_group_nodes(field_module, group_name, node_ids, node_set_name='nodes'):
    with ChangeManager(field_module):
        group = find_or_create_field_group(field_module, name=group_name)
        group.setSubelementHandlingMode(FieldGroup.SUBELEMENT_HANDLING_MODE_FULL)

        nodeset = field_module.findNodesetByName(node_set_name)
        node_group = group.getFieldNodeGroup(nodeset)
        if not node_group.isValid():
            node_group = group.createFieldNodeGroup(nodeset)

        nodeset_group = node_group.getNodesetGroup()
        for group_node_id in node_ids:
            node = nodeset.findNodeByIdentifier(group_node_id)
            nodeset_group.addNode(node)

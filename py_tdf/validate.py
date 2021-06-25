import xmlschema
from xmlschema.validators.exceptions import XMLSchemaValidationError


class TDFValidationError(Exception):
    pass

# TODO: determine absolute path to this file
# Current relative path probably wouldn't work in some usecases
PATH_TO_XSD_SCHEMA = 'schema.xsd'

def ensure_all_used_classes_are_defined(root):
    defined_rod_classes = set()
    defined_cable_classes = set()
    for el in root.findall('rod_class'):
        defined_rod_classes.add(el.attrib['id'])
    for el in root.findall('cable_class'):
        defined_cable_classes.add(el.attrib['id'])

    used_rod_classes = set()
    used_cable_classes = set()
    for el in root.findall('composition')[0].findall('rod'):
        if 'class' in el.attrib:
            used_rod_classes.add(el.attrib['class'])
    for el in root.findall('composition')[0].findall('cable'):
        if 'class' in el.attrib:
            used_cable_classes.add(el.attrib['class'])

    if not used_rod_classes.issubset(defined_rod_classes):
        raise TDFValidationError()
    if not used_cable_classes.issubset(defined_cable_classes):
        raise TDFValidationError()


# validation is done by additional walk over xml tree
# slightly slower, but easier to modify and understand
def validate(root):
    schema = xmlschema.XMLSchema(PATH_TO_XSD_SCHEMA)
    try:
        schema.validate(root)
    except XMLSchemaValidationError:
        raise TDFValidationError()
    except XMLSchemaChildrenValidationError:
        raise TDFValidationError()

    ensure_all_used_classes_are_defined(root)

    warnings = []
    return warnings

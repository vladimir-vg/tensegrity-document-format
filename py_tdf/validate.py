import xmlschema



# validation is done by additional walk over xml tree
# slightly slower, but easier to modify and understand
def validate(root):
    schema = xmlschema.XMLSchema('schema.xsd')
    schema.validate(root)
    # TODO
    # throw exception if anything is wrong with tdf xml tree
    warnings = []
    return warnings

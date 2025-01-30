import uuid
import xml.etree.ElementTree

"""
    Create QDC from EAF file path 

    eaf_filepath: file system path of source EAF file
    return QDC xml.etree.ElementTree representation
"""
def qdc_from_eaf_path(eaf_filepath):
    annotation_document = xml.etree.ElementTree.parse(eaf_filepath)
    return qdc_from_eaf(annotation_document)

"""
    Create QDC from EAF file contents

    eaf_filecontents: string contents of source EAF file
    return QDC xml.etree.ElementTree representation
"""
def qdc_from_eaf_string(eaf_filecontents):
    annotation_document = xml.etree.ElementTree.fromstring(eaf_filecontents)
    return qdc_from_eaf(annotation_document)

"""
    Create QDC from EAF xml.etree.ElementTree representation

    annotation_document: EAF xml.etree.ElementTree representation
    return QDC xml.etree.ElementTree representation
"""
def qdc_from_eaf(annotation_document):

    # Create QDC XML structure
    codebook = xml.etree.ElementTree.Element("CodeBook")
    codes = xml.etree.ElementTree.SubElement(codebook, "Codes")
    sets = xml.etree.ElementTree.SubElement(codebook, "Sets")

    tier_hierarchy = {}
    set_mapping = {}

    # Add tier_hierarchy mappings; (parent tier => [..., child tier, ...])
    for tier in annotation_document.findall("TIER"):
        parent_ref = tier.get("PARENT_REF", None)
        children = tier_hierarchy.setdefault(parent_ref, [])
        children.append(tier)

    # Populate XML codes node starting with root tiers
    for tier in tier_hierarchy.get(None, []):
        def code_from_tier(_tier):
            tier_id = _tier.get("TIER_ID")
            linguistic_type_ref = _tier.get("LINGUISTIC_TYPE_REF")
            code = xml.etree.ElementTree.Element("Code")
            code.set("guid", str(uuid.uuid4()))
            code.set("name", tier_id)
            code.set("isCodable", "true")

            # Codes can have child codes
            for _child_tier in tier_hierarchy.get(tier_id, []):
                code.append(code_from_tier(_child_tier))
            
            # Sets can have reference multiple codes
            if linguistic_type_ref not in set_mapping:
                _set = set_mapping.setdefault(linguistic_type_ref, xml.etree.ElementTree.SubElement(sets, "Set"))
                _set.set("guid", str(uuid.uuid4()))
                _set.set("name", linguistic_type_ref)
            _set = set_mapping.get(linguistic_type_ref)
            member_code = xml.etree.ElementTree.SubElement(_set, "MemberCode")
            member_code.set("guid", code.get("guid"))
            return code
        codes.append(code_from_tier(tier))

    return codebook

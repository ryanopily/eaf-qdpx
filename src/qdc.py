import uuid
import xml.etree.ElementTree

def qdc_from_eaf_path(path):
    element_tree = xml.etree.ElementTree.parse(path)
    return qdc_from_eaf(element_tree)

def qdc_from_eaf(element_tree):
    codebook = xml.etree.ElementTree.Element("CodeBook")
    codes = xml.etree.ElementTree.SubElement(codebook, "Codes")
    sets = xml.etree.ElementTree.SubElement(codebook, "Sets")

    tier_hierarchy = {}
    set_mapping = {}

    for tier in element_tree.findall("TIER"):
        parent_ref = tier.get("PARENT_REF")
        children = tier_hierarchy.setdefault(parent_ref, [])
        children.append(tier)

    for tier in tier_hierarchy.get(None):
        def code_from_tier(_tier):
            code = xml.etree.ElementTree.Element("Code")
            code.set("guid", str(uuid.uuid4()))
            code.set("name", _tier.get("TIER_ID"))
            code.set("isCodable", "true")

            for _child_tier in tier_hierarchy.get(_tier.get("TIER_ID"), []):
                code.append(code_from_tier(_child_tier))
            
            linguistic_type_ref = _tier.get("LINGUISTIC_TYPE_REF")
            if linguistic_type_ref not in set_mapping:
                _set = set_mapping.setdefault(linguistic_type_ref, xml.etree.ElementTree.SubElement(sets, "Set"))
                _set.set("guid", str(uuid.uuid4()))
                _set.set("name", linguistic_type_ref)
            
            _set = set_mapping.get(linguistic_type_ref)
            _member_code = xml.etree.ElementTree.SubElement(_set, "MemberCode")
            _member_code.set("guid", code.get("guid"))
            return code
        codes.append(code_from_tier(tier))

    return codebook

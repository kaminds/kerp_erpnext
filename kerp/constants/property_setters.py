PROPERTY_SETTERS = [
    {
        "doctype": "Item",
        "fieldname": "section_break_11",
        "property": "collapsible",
        "value": "0",
    },
    {
        "doctype": "Item",
        "fieldname": "brand",
        "property": "depends_on",
        "value": "eval:!doc.has_variants",
    },
    {
        "doctype": "Item",
        "fieldname": "brand",
        "property": "mandatory_depends_on",
        "value": "eval:!doc.has_variants && !doc.is_fixed_asset",
    },
    {
        "doctype": "Item",
        "fieldname": "gst_hsn_code",
        "property": "fetch_from",
        "value": None,
    },
    {
        "doctype": "Batch",
        "doctype_or_field": "DocType",
        "property": "title_field",
        "value": "batch_no_kerp",
    },
    {
        "doctype": "Batch",
        "doctype_or_field": "DocType",
        "property": "show_title_field_in_link",
        "value": "1",
    },
    {
        "doctype": "Address",
        "doctype_or_field": "DocType",
        "property": "title_field",
        "value": "address_title",
    },
    {
        "doctype": "Address",
        "doctype_or_field": "DocType",
        "property": "search_fields",
        "value": "address_line1, city, state, country",
    },
    {
        "doctype": "Address",
        "doctype_or_field": "DocType",
        "property": "track_changes",
        "value": "1",
    },
]

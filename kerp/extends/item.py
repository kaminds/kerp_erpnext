from erpnext.stock.doctype.item.item import Item


class CustomItem(Item):
    def validate_variant_attributes(self):
        if self.variant_of == "Micronutrient Premix":
            return
        else:
            super().validate_variant_attributes()

from dataclasses import dataclass

RECORD_LENGTH = 80

@dataclass(frozen=True)
class FieldSpec:
    name: str
    start: int
    end: int
    strip: bool = True
    description: str = ""

    def extract(self, line: str) -> str:
        value = line[self.start - 1:self.end]
        return value.strip() if self.strip else value

REQUEST_SPECS: dict[str, list[FieldSpec]] = {
    "10": [FieldSpec("entry_no", 9, 16), FieldSpec("district_port_of_entry", 18, 21), FieldSpec("entry_type", 34, 35), FieldSpec("mot", 36, 37)],
    "11": [FieldSpec("importer_of_record_number", 3, 14), FieldSpec("consignee_number", 15, 26), FieldSpec("estimated_entry_date", 42, 47), FieldSpec("date_of_importation", 48, 53)],
    "20": [FieldSpec("carrier_code", 3, 6), FieldSpec("district_port_of_unlading", 7, 10), FieldSpec("estimated_date_of_arrival", 11, 16), FieldSpec("location_of_goods_code", 17, 20)],
    "21": [FieldSpec("trip_identifier", 3, 7)],
    "22": [FieldSpec("manifested_quantity", 3, 10), FieldSpec("manifested_quantity_uom", 11, 15)],
    "23": [FieldSpec("manifest_component_type_code", 3, 3), FieldSpec("manifest_component_identifier", 8, 19)],
    "31": [FieldSpec("bond_type_code", 3, 3), FieldSpec("surety_company_code", 6, 8)],
    "40": [FieldSpec("line_item_identifier", 5, 7), FieldSpec("country_of_origin", 9, 10), FieldSpec("country_of_export", 11, 12), FieldSpec("gross_shipping_weight", 42, 51)],
    "44": [FieldSpec("commercial_description", 3, 72)],
    "47": [FieldSpec("party_type", 3, 3), FieldSpec("party_id", 4, 18)],
    "50": [FieldSpec("hts_number", 3, 12), FieldSpec("duty_amount", 14, 23), FieldSpec("value", 25, 34), FieldSpec("quantity_1", 36, 47), FieldSpec("uom_1", 48, 50)],
    "54": [FieldSpec("declaration_type_code", 3, 4), FieldSpec("declaration_information", 5, 80)],
    "90": [FieldSpec("grand_total_duty", 3, 13), FieldSpec("grand_total_user_fee", 15, 25), FieldSpec("grand_total_ir_tax", 27, 37), FieldSpec("grand_total_ad_duty", 39, 49), FieldSpec("grand_total_cv_duty", 51, 61)],
}

RESPONSE_SPECS: dict[str, list[FieldSpec]] = {
    "A": [FieldSpec("port_code", 2, 5), FieldSpec("filer_code", 6, 8), FieldSpec("batch_date", 15, 20), FieldSpec("application_identifier", 26, 27)],
    "B": [FieldSpec("port_code", 4, 7), FieldSpec("filer_code", 8, 10), FieldSpec("application_identifier", 11, 12)],
    "E0": [FieldSpec("reference_data_type_code", 4, 9), FieldSpec("occurrence_position", 11, 16), FieldSpec("reference_id_constant", 18, 24), FieldSpec("reference_data_text", 26, 80)],
    "E1": [FieldSpec("disposition_type_code", 3, 3), FieldSpec("severity_code", 4, 4), FieldSpec("condition_code", 5, 7), FieldSpec("reason_code", 8, 10), FieldSpec("narrative_text", 11, 50), FieldSpec("entry_filer_code", 51, 53), FieldSpec("entry_number", 56, 63), FieldSpec("version_number", 64, 68), FieldSpec("broker_reference_number", 69, 77)],
    "Y": [FieldSpec("port_code", 4, 7), FieldSpec("filer_code", 8, 10), FieldSpec("application_identifier", 11, 12), FieldSpec("record_count", 13, 17)],
    "Z": [FieldSpec("port_code", 2, 5), FieldSpec("filer_code", 6, 8), FieldSpec("batch_date", 15, 20)],
}

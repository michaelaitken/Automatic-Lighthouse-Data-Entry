import specifications

class Analyze:
    def __init__(self) -> None:
        pass

    def decode_lpm_product_codes(self, product_code) -> dict:
        '''Decodes a list of LPM product codes and returns a dictionary of individual selectors for identification'''
        string_code = str(product_code)
        if string_code == "MDF/MDF MR/PWB/HMR COVERSHEET":
            return None
        else:
            code_dict = {
                "original_code": string_code,
                "product_type": string_code[:2],
                "side_type": string_code[2],
                "thickness": float(string_code[4:6]),
                "plate_seperator": string_code[8:10],
                "board_length": int(string_code[10:14]),
                "board_width": int(string_code[14:18]),
                "color_code": string_code[18:23],
            }

            logic_product_code = self.get_lpm_logic_code(code_dict)
            return logic_product_code
    
    def get_lpm_logic_code(self, product_dict: dict,) -> dict:
            # Check if single-sided
        if product_dict["side_type"] == "1":

            if product_dict["board_width"] >= 1800:

                if product_dict["thickness"] >= 25:
                    product_dict["data_sheet"] = "1.1"

                elif 18 >= product_dict["thickness"]:
                    product_dict["data_sheet"] = "1.2"


            elif product_dict["board_width"] < 1800:
                if product_dict["thickness"] <= 25:
                    product_dict["data_sheet"] = "2.1"

                elif product_dict["thickness"] >= 33:
                    product_dict["data_sheet"] = "3.1"

            # Check if single-sided
        elif product_dict["side_type"] == "D":

            if product_dict["board_width"] < 1800:
                product_dict["data_sheet"] = "6.1"

            elif product_dict["board_width"] >= 1800:
                if 12 >= product_dict["thickness"]:
                    product_dict["data_sheet"] = "5.1"

                elif product_dict["thickness"] > 12:
                    product_dict["data_sheet"] = 4
                        
                    if product_dict["color_code"] == "WHITE":
                        if product_dict["plate_seperator"] == "VE" or product_dict["plate_seperator"] == "DE":
                            if product_dict["board_length"] < 3600:
                                product_dict["data_sheet"] = "4.1"

                            elif product_dict["board_length"] >= 3600:
                                product_dict["data_sheet"] = "4.2"

                        if product_dict["plate_seperator"] == "PE" or product_dict["plate_seperator"] == "FL":
                            product_dict["data_sheet"] = "4.3"

                    elif product_dict["color_code"] == "BLACK" or product_dict["color_code"] == "CHARC":
                        product_dict["data_sheet"] = "4.4"
                        
                    else:
                        product_dict["data_sheet"] = "4.3"

        return product_dict

    def get_lpm_specification_values(self, product_decoded):
        specs = specifications.specifications[product_decoded['data_sheet']]

        product_dict = {
            "original_code": product_decoded["original_code"],
            "board_thickness": {
                "lsl": product_decoded["thickness"] - 0.1,
                "norm": product_decoded["thickness"],
                "usl": product_decoded["thickness"] + 0.1
            }
        }
        product_dict["bow_reading"] = specs["bow_reading"]
        product_dict["temp_bottom"] = specs["temp_bottom"]
        product_dict["temp_top"] = specs["temp_top"]
        product_dict["press_time"] = specs["press_time"]

        return product_dict
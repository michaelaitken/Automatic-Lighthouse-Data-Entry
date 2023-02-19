import lighthouse as lh
import json


    # ---------- Global Variables ---------- #
URL = "https://lmxlighthouse.fbu.com/sfolv7/#2/grid/ProductType"
USERNAME = "michael.aitken"
PASSWORD = "Laminex1"


    # ---------- Main Program ---------- #
    # Gather the product codes to be analyzed and data entered
lighthouse = lh.Lighthouse()
lighthouse.login(URL, USERNAME, PASSWORD)
product_codes = lighthouse.get_lpm_product_codes()

    # Dump dictionary to a JSON for easy troubleshooting.
# with open(file="./data.json", mode="w") as data:
#     json.dump(product_specs, data)

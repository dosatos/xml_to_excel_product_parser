import xml.etree.ElementTree as ET
import json
import pandas as pd
import logging


def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def setup_loggers():
    logger_names = ['not_founds', 'overrides']
    loggers = dict(zip(logger_names, [None for _ in range(len(logger_names))]))
    for name in logger_names:
        loggers[name] = setup_logger(name, f"messages/{name}.log")
    return loggers


def get_products(xml_tree, namespaces):
    root = xml_tree.getroot()
    products = root.find('urn:products', namespaces)
    return products


def get_xls_table(config):
    path, fields = config['excel_path'], config['excel_fields']
    table = pd.read_excel(path, sheet_name="Data - CFT", skipinitialspace=True)[fields]
    filtered_table = table[fields].drop_duplicates()
    filtered_table.columns = ['concept_code', 'ingredients']
    filtered_table.concept_code = filtered_table.astype('str')
    filtered_table = filtered_table.fillna("")
    return filtered_table


def get_ingredients(table, concept_code, loggers):
    try:
        return table[table['concept_code'] == concept_code].values[0][1]
    except IndexError:
        loggers['not_founds'].info(f"Not found for {concept_code} not found")


def append_or_set_ingredients(product, ingredients, tag_name, namespaces, counter, logger):
    # validate if ingredients found in the excel table
    if not ingredients:
        counter['not_found'] += 1
        return

    # verify if it already contained ingredients tag
    # overwrite (set new) if the proposed ingredients are different from the original ones
    ing_tag = product.find(f'urn:{tag_name}', namespaces)
    if ing_tag is not None:
        if ing_tag.text != ingredients:
            logger['overrides'].warning(f"Changed ORIGINAL: {ing_tag.text} TO: {ingredients}")
            ing_tag.text = ingredients
            counter["updated"] += 1
        return

    # if found ingredients in the excel update xml
    ing_tag = ET.Element(tag_name)
    ing_tag.text = ingredients
    product.append(ing_tag)
    counter["appended"] += 1
    return


def read_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)


def main():
    config = read_config(path='config.json')
    source = get_xls_table(config)
    namespaces = config['namespace']

    loggers = setup_loggers()

    counter = {
        "not_found": 0,
        "updated": 0,
        "appended": 0,
    }

    tree = ET.parse('xml/DCEProductText_180815_KZ.xml')
    products = get_products(tree, namespaces)

    for product in products:
        concept_code = product.find('urn:ProfileNumber', namespaces).text
        ingredients = get_ingredients(source, concept_code, loggers)
        append_or_set_ingredients(product, ingredients, config['ingredient_tag_name'],
                                                            namespaces, counter, loggers)

    tree.write("xml/output.xml", encoding="utf8")
    nl = '\n'
    print(f"{counter['not_found']} - not found{nl}{counter['updated']} - updated{nl}{counter['appended']} - appended{nl}{len(products)} - Total")


if __name__ == "__main__":
    main()
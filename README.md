#### XML, XLS Parser
This script updates/appends products (from an XML file)
with ProductIngredients retrieved from the given Excel file.

##### setup the config.json file

ingredient_tag_name - tag name in the XML
excel_path - path to the excel file
excel_fields -  two columns to be considered as [ProfileNumber/ConceptCode, Ingredients]
namespace - default namespace used in the XML


appends the XML product objects with Ingredients Info.
#### Python 3.6

##### To activate the virtual envirionment:
>>> source venv/bin/activate

##### To install dependencies:
>>> pip install -r requirements.txt



##### To run the file:
>>> python xls_to_xml.py
from xml.etree.ElementTree import Element, SubElement, tostring, parse, fromstring
from multiprocessing import Process
from typing import List
import csv

from io import FileIO
import tempfile
from zipfile import ZipFile
import os, fnmatch
import random
import string
import uuid



def _name_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def _generate_random_xml_body() -> FileIO:
    objects_count = random.randint(1, 10)
    level = random.randint(1, 100)
    id = uuid.uuid4()
    root = Element('root')
    element_var_id = SubElement(root, "var")
    element_var_id.set('name', "id")
    element_var_id.set('value', f"{id}")
    element_var_level = SubElement(root, "var")
    element_var_level.set('name', 'level')
    element_var_level.set('value', str(level))
    element_objects = SubElement(root, "objects")
    for i_1 in range(objects_count):
        name = _name_generator()
        element_object = SubElement(element_objects, "object")
        element_object.set('name', name)
    return tostring(root)

def generate_files():
    for zip_index in range(50):
        with ZipFile(f'{zip_index}.zip', 'w') as zipObj:
            for file_index in range(100):
                file_body = _generate_random_xml_body()
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp_name = temp.name
                try:
                    temp.write(file_body)
                finally:
                    temp.close()
                zipObj.write(temp_name, f'{temp.name}.xml')
                os.remove(temp_name)

def _get_id_and_level(root_element: Element) -> tuple[int, str]:
    id = None
    level = None
    attributes = []
    for child in root_element:
        if child.tag == 'var':
            attributes.append(tuple(child.attrib.values()))
    attributes = dict(attributes)
    return attributes.get('id'), attributes.get('level')

def _get_objects_names(root_element: Element) -> List[str]:
    names = []
    for child in root_element:
        if child.tag == 'objects':
            for ob in child:
                names.append(ob.attrib.get('name'))
    return names

def parse_files():
    zips_list = fnmatch.filter(os.listdir('.'), '*.zip')

    first_csv_header = ['id', 'level']
    first_csv_data = []

    second_csv_header = ['id', 'object_name']
    second_csv_data = []
    
    for zip_file_path in zips_list:
        zip_file = ZipFile(zip_file_path)
        names = zip_file.namelist()
        for name in names:
            xml_file = zip_file.open(name)
            content = xml_file.read()
            root_element = fromstring(content)
            id, level = _get_id_and_level(root_element)
            first_csv_data.append([id, level])

            object_names = _get_objects_names(root_element)
            for object_name in object_names:
                second_csv_data.append([id, object_name])

    with open('first_result.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(first_csv_header)
        writer.writerows(first_csv_data)

    with open('second_result.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(second_csv_header)
        writer.writerows(second_csv_data)

if __name__ == '__main__':
    generate_files()
    p = Process(target=parse_files)
    p.start()
    p.join()

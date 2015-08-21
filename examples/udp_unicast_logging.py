#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import json
import yaml
from xml.etree import ElementTree
import os.path

def save_as_json(results, log_name):
    """
    Saves a dictionary type as a json formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name
    """
    with open(log_name+'.json', 'w') as logfile:
        json.dump(results, logfile)

def save_as_yaml(results, log_name):
    """ 
    Saves a dictionary type as a yaml formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name
    """
    with open(log_name+'.yaml', 'w') as logfile:
        yaml.dump(results, logfile)

def save_as_csv(results, log_name):
    """
    Saves a dictionary type as a csv formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name.
    Writes keys in first column, values in second. One key-value pair each line
    """
    with open(log_name+'.csv', 'w') as logfile:
        writer = csv.writer(logfile)
        writer.writerows(results.items())

def save_as_xml(results, log_name):
    """
    Save a dictionary in an xml file with name 'log_name'.xml.
    if logfile already exists, results will be appended to the file.
    """
    logfile = log_name+".xml"
    tree = None
    root = None
    
    if os.path.isfile(logfile):
        tree = ElementTree.ElementTree(file=logfile)
        root = tree.getroot()
    else:
        # Create root element with tag log
        root = ElementTree.Element('log')
        tree = ElementTree.ElementTree(element=root)

    id_string = str(results.pop('test_id'))
    child = dict_to_xml(id_string, results)
    root.append(child)

    tree.write(logfile)

def dict_to_xml(tag, d):
    """ 
    Turn a simple dictionary d of key, value pairs into xml.
    'tag' is the "root" xml entry
    returns an ElementTree.Element
    """
    element = ElementTree.Element(str(tag))
    for key, val in d.items():
        child = Element(str(key))
        child.text = str(val)
        elememt.append(child)
    return element


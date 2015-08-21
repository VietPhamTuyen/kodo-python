#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import json
import yaml
import csv
from xml.etree import ElementTree
import os
import uuid

def save_as_json(results, log_name):
    """
    Saves a dictionary type as a json formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name
    """
    with open(log_name+'.json', 'a') as logfile:
        json.dump(results, logfile)

def save_as_yaml(results, log_name):
    """ 
    Saves a dictionary type as a yaml formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name
    """
    with open(log_name+'.yaml', 'a') as logfile:
        yaml.dump(results, logfile)

def save_as_csv(results, log_name):
    """
    Saves a dictionary type as a csv formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name.
    Writes keys in first column, values in second. One key-value pair each line
    """
    with open(log_name+'.csv', 'a') as logfile:
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
    parser = ElementTree.XMLParser(encoding='utf-8')
    
    if os.path.isfile(logfile):
        tree = ElementTree.ElementTree()
        tree.parse(logfile, parser=parser)
        root = tree.getroot()
    else:
        # Create root element with tag log
        root = ElementTree.Element('log')
        tree = ElementTree.ElementTree(element=root)

    id_string = str(results.pop('test_id'))
    child = dict_to_xml('test_id', results)
    child.text = id_string
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
        child = ElementTree.Element(str(key))
        child.text = str(val)
        element.append(child)
    return element

def test():
    # Create test dictionary
    testresults = dict(
        test_id     = uuid.uuid4().int,
        client_ip   = "192.168.1.80",
        status      = "success",
        packets_total = 100,
        packets_decode = 98,
        time_start  = 14.231235, 
        time_decode = 28.123215,
        time_stop   = 30.456456)

    logname = "testlog"
    save_as_json(testresults, logname)
    save_as_yaml(testresults, logname)
    save_as_csv(testresults, logname)
    save_as_xml(testresults, logname)

def test_cleanup():
    for extension in ['json', 'yaml', 'csv', 'xml']:
        filename = 'testlog.' + extension
        if os.path.isfile(filename):
            os.remove(filename)

if __name__ == '__main__':
    test()
    test() # run twice to check if files are appended properly
    test_cleanup()

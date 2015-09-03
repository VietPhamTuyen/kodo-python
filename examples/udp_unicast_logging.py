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

"""
    Saves a list of dictionaries in logfile with 
    name 'log_name'. Uses function load_func to load existing data, 
    and dump_func to save data with correct formatting. 
    """
def save_helper(results, log_name, load_func, dump_func):
    results_list = []

    # read in old results, if any
    if os.path.isfile(log_name):
        with open(log_name, 'r') as logfile:
            old_results = load_func(logfile)
            if type(old_results) is list:
                results_list += old_results
            elif type(old_results) is dict:
                results_list.append(old_results)

    # add results to list of results
    results_list.append(results)

    with open(log_name, 'w') as logfile:
        dump_func(results_list, logfile, indent=4)

def save_as_json(results, log_name):
    """
    Saves a list of dictionaries as a json formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name
    """
    def dump(res, file, indent=4):
        json.dump(res, file, indent=indent, sort_keys=True)

    save_helper(results, log_name+'.json', json.load, dump)
    
def save_as_yaml(results, log_name):
    """ 
    Saves a list of dictionaries as a yaml formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name
    """
    save_helper(results, log_name+'.yaml', yaml.load, yaml.dump)

def save_as_csv(results, log_name):
    """
    Saves a dictionary type as a csv formatted logfile with 
    name 'log_name'. Function adds correct extension to logfile name.
    Writes keys in first column, values in second. One key-value pair each line
    """
    with open(log_name+'.csv', 'a') as logfile:
        writer = csv.writer(logfile)
        writer.writerows(results.items())
        logfile.write(os.linesep)

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
        test_id     = uuid.uuid4().hex,
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

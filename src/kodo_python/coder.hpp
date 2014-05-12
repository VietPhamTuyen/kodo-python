// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <kodo/trace.hpp>
#include <kodo/has_trace.hpp>

#include <Python.h>

namespace kodo_python {

    template<class Coder>
    bool has_trace(Coder& coder)
    {
        (void) coder;
        return kodo::has_trace<Coder>::value;
    }

    template<class Coder>
    void trace(Coder& coder)
    {
        return kodo::trace(coder, std::cout);
    }

    template<class Coder>
    void filtered_trace(Coder& coder, PyObject* function)
    {
        auto filter = [&function](const std::string& zone)
        {
            return boost::python::call<bool>(function, zone);
        };
        return kodo::trace(coder, std::cout, filter);
    }

    template<class TraceTag, class Type>
    struct trace_methods
    {
        template<class CoderClass>
        void operator()(CoderClass& coder_class)
        {
            (void) coder_class;
        }
    };

    template<class Type>
    struct trace_methods<kodo::enable_trace, Type>
    {
        template<class CoderClass>
        void operator()(CoderClass& coder_class)
        {
            coder_class.def("trace", &trace<Type>);
            coder_class.def("filtered_trace", &filtered_trace<Type>);
            coder_class.def("has_trace", &has_trace<Type>);
        }
    };

    template<template<class, class> class Coder, class Field, class TraceTag>
    auto coder(const std::string& name) ->
        boost::python::class_<Coder<Field, TraceTag>, boost::noncopyable>
    {
        typedef Coder<Field, TraceTag> coder_type;
        auto coder_class = boost::python::class_<coder_type,
                                                   boost::noncopyable>(
            name.c_str(), boost::python::no_init)
            .def("payload_size", &coder_type::payload_size)
            .def("block_size", &coder_type::block_size)
            .def("symbol_size", &coder_type::symbol_size)
            .def("symbols", &coder_type::symbols)
            .def("rank", &coder_type::rank)
            .def("is_symbol_pivot", &coder_type::is_symbol_pivot);


        trace_methods<TraceTag, coder_type> trace;
        trace(coder_class);

        return coder_class;
    }
}

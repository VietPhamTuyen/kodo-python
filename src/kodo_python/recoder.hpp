// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <string>
#include <vector>

#include <Python.h>
#include <boost/python.hpp>
#include <boost/python/args.hpp>

#include "coder.hpp"
#include "resolve_field_name.hpp"

namespace kodo_python
{
    template<class Recoder>
    PyObject* recoder_write_payload(Recoder& recoder)
    {
        std::vector<uint8_t> payload(recoder.payload_size());
        auto length = recoder.write_payload(payload.data());
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), length);
        #else
        return PyString_FromStringAndSize((char*)payload.data(), length);
        #endif
    }

    template<class Recoder>
    void recoder_read_payload(Recoder& recoder, const std::string& data)
    {
        std::vector<uint8_t> payload(data.length());
        std::copy(data.c_str(), data.c_str() + data.length(), payload.data());
        recoder.read_payload(payload.data());
    }

    template<template<class, class> class Coder>
    struct extra_recoder_methods
    {
        template<class RecoderClass>
        extra_recoder_methods(RecoderClass& recoder_class)
        {
            (void) recoder_class;
        }
    };

    template<
        template<class, class> class Coder,
        class Field, class TraceTag
    >
    void recoder(const std::string& stack)
    {
        using boost::python::arg;
        using boost::python::args;
        using recoder_type = Coder<Field, TraceTag>;

        std::string field = resolve_field_name<Field>();
        std::string kind = "Recoder";
        std::string name = stack + kind + field;

        auto recoder_class = coder<Coder, Field, TraceTag>(name)
        .def("read_payload", &recoder_read_payload<recoder_type>, arg("symbol_data"),
            "Read the provided encoded symbol.\n\n"
            "\t:param symbol_data: The encoded symbol.\n"
        )
        .def("write_payload", &recoder_write_payload<recoder_type>,
            "Recode a symbol.\n\n"
            "\t:returns: The recoded symbol.\n"
        );

        (extra_recoder_methods<Coder>(recoder_class));
    }
}

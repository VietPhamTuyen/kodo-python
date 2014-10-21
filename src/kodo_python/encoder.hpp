// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <Python.h>
#include <bytesobject.h>

#include <boost/python/args.hpp>

#include <kodo/disable_trace.hpp>
#include <kodo/enable_trace.hpp>
#include <kodo/has_systematic_encoder.hpp>
#include <kodo/is_systematic_on.hpp>
#include <kodo/set_systematic_off.hpp>
#include <kodo/set_systematic_on.hpp>
#include <kodo/write_feedback.hpp>

#include <string>
#include <vector>

#include "coder.hpp"
#include "resolve_field_name.hpp"

namespace kodo_python
{
    template<class Encoder>
    bool is_systematic_on(const Encoder& encoder)
    {
        return kodo::is_systematic_on(encoder);
    }

    template<class Encoder>
    void set_systematic_on(Encoder& encoder)
    {
        kodo::set_systematic_on(encoder);
    }

    template<class Encoder>
    void set_systematic_off(Encoder& encoder)
    {
        kodo::set_systematic_off(encoder);
    }

    template<class Encoder>
    void set_symbols(Encoder& encoder, const std::string& data)
    {
        auto storage = sak::const_storage(
            (uint8_t*)data.c_str(), data.length());
        encoder.set_symbols(storage);
    }

    template<class Encoder>
    void set_symbol(Encoder& encoder, uint32_t index, const std::string& data)
    {
        auto storage = sak::const_storage(
            (uint8_t*)data.c_str(), data.length());
        encoder.set_symbol(index, storage);
    }

    template<class Encoder>
    PyObject* encode(Encoder& encoder)
    {
        std::vector<uint8_t> payload(encoder.payload_size());
        uint32_t length = encoder.encode(payload.data());
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), length);
        #else
        return PyString_FromStringAndSize((char*)payload.data(), length);
        #endif
    }

    template<class Encoder>
    void read_feedback(Encoder& encoder, const std::string& feedback)
    {
        std::vector<uint8_t> _feedback(feedback.length());
        std::copy(
            feedback.c_str(),
            feedback.c_str() + feedback.length(),
            _feedback.data());
        encoder.read_feedback(_feedback.data());
    }

    template<bool IS_SYSTEMATIC_ENCODER, class Type>
    struct systematic_encoder_methods
    {
        template<class EncoderClass>
        systematic_encoder_methods(EncoderClass& encoder_class)
        {
            (void) encoder_class;
        }
    };

    template<class Type>
    struct systematic_encoder_methods<true, Type>
    {
        template<class EncoderClass>
        systematic_encoder_methods(EncoderClass& encoder_class)
        {
            encoder_class
            .def("is_systematic_on", &is_systematic_on<Type>,
                "Returns true if the encoder is in systematic mode.\n\n"
                "\t:returns: True if the encoder is in systematic mode.\n"
            )
            .def("set_systematic_on", &set_systematic_on<Type>,
                "Set the encoder in systematic mode.\n"
            )
            .def("set_systematic_off", &set_systematic_off<Type>,
                "Turns off systematic mode.\n");
        }
    };

    template<template<class, class> class Coder, class Type>
    struct extra_encoder_methods
    {
        template<class EncoderClass>
        extra_encoder_methods(EncoderClass& encoder_class)
        {
            (void) encoder_class;
        }
    };

    template<class Type>
    struct extra_encoder_methods<kodo::sliding_window_encoder, Type>
    {
        template<class EncoderClass>
        extra_encoder_methods(EncoderClass& encoder_class)
        {
            encoder_class
            .def("feedback_size", &Type::feedback_size,
                "Returns the required feedback buffer size in bytes.\n\n"
                "\t:returns: The required feedback buffer size in bytes.\n"
            )
            .def("read_feedback", &read_feedback<Type>,
                "Returns the feedback information.\n\n"
                "\t:returns: The feedback information.\n");
        }
    };

    template<class Type>
    struct extra_encoder_methods<kodo::shallow_sparse_full_rlnc_encoder, Type>
    {
        template<class EncoderClass>
        extra_encoder_methods(EncoderClass& encoder_class)
        {
            using boost::python::arg;
            encoder_class
            .def("set_density", &Type::set_density, arg("density"),
                "Set the density of the coefficients generated.\n\n"
                "\t:param density: The coefficients density.\n"
            )
            .def("density", &Type::density,
                "Get the density of the coefficients generated.\n\n"
                "\t:returns: The density of the generator.\n"
            )
            .def("set_average_nonzero_symbols",
                &Type::set_average_nonzero_symbols, arg("symbols"),
                "Set the average number of nonzero symbols.\n\n"
                "\t:param symbols: The average number of nonzero symbols.\n"
            );
        }
    };

    template<template<class, class> class Coder, class Field, class TraceTag>
    void encoder(const std::string& stack, bool trace)
    {
        using boost::python::arg;
        using boost::python::args;

        std::string field = resolve_field_name<Field>();

        std::string s = "_";
        std::string kind = "encoder";
        std::string trace_string = trace ? "_trace" : "";
        std::string name = stack + s + kind + s + field + trace_string;

        typedef Coder<Field, TraceTag> encoder_type;
        auto encoder_class = coder<Coder, Field, TraceTag>(name)
        .def("encode", &encode<encoder_type>,
            "Encodes a symbol.\n\n"
            "\t:returns: The encoded symbol.\n"
        )
        .def("set_symbols", &set_symbols<encoder_type>, arg("symbols"),
            "Sets the symbols to be encoded.\n\n"
            "\t:param symbols: The symbols to be encoded.\n"
        )
        .def("set_symbol", &set_symbol<encoder_type>, args("index", "symbol"),
            "Sets a symbol to be encoded.\n\n"
            "\t:param index: The index of the symbol in the coding block.\n"
            "\t:param symbol: The actual data of that symbol.\n");

        extra_encoder_methods<Coder, encoder_type> extra_encoder_methods(
            encoder_class);

        systematic_encoder_methods<
            kodo::has_systematic_encoder<encoder_type>::value,
            encoder_type>
            systematic_encoder_methods(encoder_class);
    }
}

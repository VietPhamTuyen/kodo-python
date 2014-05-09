// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <Python.h>
#include <bytesobject.h>
#include <kodo/has_systematic_encoder.hpp>
#include <kodo/set_systematic_on.hpp>
#include <kodo/set_systematic_off.hpp>
#include <kodo/is_systematic_on.hpp>
#include <kodo/write_feedback.hpp>
#include <kodo/disable_trace.hpp>
#include <kodo/enable_trace.hpp>

#include "coder.hpp"

namespace kodo_python
{
    template<class Encoder>
    bool has_systematic_encoder(const Encoder& encoder)
    {
        (void) encoder;
        return kodo::has_systematic_encoder<Encoder>::value;
    }

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
        auto storage = sak::const_storage((uint8_t*)data.c_str(), data.length());
        encoder.set_symbols(storage);
    }

    template<class Encoder>
    void set_symbol(Encoder& encoder, uint32_t index, const std::string& data)
    {
        auto storage = sak::const_storage((uint8_t*)data.c_str(), data.length());
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

    template<template<class, class> class Coder, class Type>
    struct extra_encoder_methods
    {
        template<class EncoderClass>
        void operator()(EncoderClass& encoder_class)
        {
            (void) encoder_class;
        }
    };

    template<class Type>
    struct extra_encoder_methods<kodo::sliding_window_encoder, Type>
    {
        template<class EncoderClass>
        void operator()(EncoderClass& encoder_class)
        {
            encoder_class.def("feedback_size", &Type::feedback_size)
                         .def("read_feedback", &read_feedback<Type>);
        }
    };

    template<template<class, class> class Coder, class Field, class TraceTag>
    void encoder(const std::string& name)
    {
        typedef Coder<Field, TraceTag> encoder_type;
        typedef Coder<Field, TraceTag> decoder_type;
        auto encoder_class = coder<Coder,Field,TraceTag>(name)
            .def("encode", &encode<encoder_type>)
            .def("set_symbols", &set_symbols<encoder_type>)
            .def("set_symbol", &set_symbol<encoder_type>)
            .def("has_systematic_encoder", &has_systematic_encoder<encoder_type>)
            .def("is_systematic_on", &is_systematic_on<encoder_type>)
            .def("set_systematic_on", &set_systematic_on<encoder_type>)
            .def("set_systematic_off", &set_systematic_off<encoder_type>)
        ;

        extra_encoder_methods<Coder, encoder_type> extra;
        extra(encoder_class);

        boost::python::register_ptr_to_python<boost::shared_ptr<encoder_type>>();
    }
}

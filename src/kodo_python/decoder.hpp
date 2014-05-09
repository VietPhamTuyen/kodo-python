// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <sak/storage.hpp>
#include <kodo/is_partial_complete.hpp>
#include <kodo/has_partial_decoding_tracker.hpp>

#include <Python.h>
#include <bytesobject.h>

#include <kodo/write_feedback.hpp>

#include "coder.hpp"

namespace kodo_python
{

    template<class Decoder>
    PyObject* copy_symbols(Decoder& decoder)
    {
        std::vector<uint8_t> payload(decoder.block_size());
        auto storage = sak::mutable_storage(payload.data(), decoder.block_size());
        decoder.copy_symbols(storage);
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), decoder.block_size());
        #else
        return PyString_FromStringAndSize((char*)payload.data(), decoder.block_size());
        #endif
    }

    /// @todo: consider removing this method from the python api.
    template<class Decoder>
    PyObject* copy_symbol(Decoder& decoder, uint32_t index)
    {
        std::vector<uint8_t> payload(decoder.block_size());
        auto storage = sak::mutable_storage(payload.data(), decoder.block_size());
        decoder.copy_symbol(index, storage);
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), decoder.block_size());
        #else
        return PyString_FromStringAndSize((char*)payload.data(), decoder.block_size());
        #endif
    }

    template<class Decoder>
    PyObject* recode(Decoder& decoder)
    {
        std::vector<uint8_t> payload(decoder.payload_size());
        auto length = decoder.recode(payload.data());

        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), length);
        #else
        return PyString_FromStringAndSize((char*)payload.data(), length);
        #endif
    }

    template<class Decoder>
    void decode(Decoder& decoder, const std::string& data)
    {
        std::vector<uint8_t> payload(data.length());
        std::copy(data.c_str(), data.c_str() + data.length(), payload.data());
        decoder.decode(payload.data());
    }

    template<class Decoder>
    void decode_symbol(Decoder& decoder, const std::string& symbol_data,
        const std::string& symbol_coefficients)
    {
        std::vector<uint8_t> _symbol_data(decoder.symbol_size());
        std::vector<uint8_t> _symbol_coefficients(decoder.symbol_size());

        std::copy(
            symbol_data.c_str(),
            symbol_data.c_str() + symbol_data.length(),
            _symbol_data.data());

        std::copy(
            symbol_coefficients.c_str(),
            symbol_coefficients.c_str() + symbol_coefficients.length(),
            _symbol_coefficients.data());

        decoder.decode_symbol(_symbol_data.data(), _symbol_coefficients.data());
    }

    template<class Decoder>
    bool has_partial_decoding_tracker(Decoder& decoder)
    {
        (void) decoder;
        return kodo::has_partial_decoding_tracker<Decoder>::value;
    }

    template<class Decoder>
    bool is_partial_complete(Decoder& decoder)
    {
        return kodo::is_partial_complete(decoder);
    }

    template<class Decoder>
    PyObject* write_feedback(Decoder& decoder)
    {
        std::vector<uint8_t> payload(decoder.feedback_size());
        uint32_t length = kodo::write_feedback(decoder, payload.data());
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), length);
        #else
        return PyString_FromStringAndSize((char*)payload.data(), length);
        #endif
    }

    template<template<class, class> class Coder, class Type>
    struct extra_decoder_methods
    {
        template<class DecoderClass>
        void operator()(DecoderClass& decoder_class)
        {
            (void) decoder_class;
        }
    };

    template<class Type>
    struct extra_decoder_methods<kodo::sliding_window_decoder, Type>
    {
        template<class EncoderClass>
        void operator()(EncoderClass& decoder_class)
        {
            decoder_class.def("feedback_size", &Type::feedback_size)
                         .def("write_feedback", &write_feedback<Type>);
        }
    };

    template<template<class, class> class Coder, class Field, class TraceTag>
    void decoder(const std::string& name)
    {
        typedef Coder<Field, TraceTag> decoder_type;
        auto decoder_class = coder<Coder,Field,TraceTag>(name)
            .def("recode", &recode<decoder_type>)
            .def("decode", &decode<decoder_type>)
            .def("decode_symbol", &decode_symbol<decoder_type>)
            .def("is_complete", &decoder_type::is_complete)
            .def("symbols_uncoded", &decoder_type::symbols_uncoded)
            .def("copy_symbols", &copy_symbols<decoder_type>)
            .def("copy_symbol", &decoder_type::copy_symbol)
            .def("is_symbol_uncoded", &decoder_type::is_symbol_uncoded)
            .def("has_partial_decoding_tracker", &has_partial_decoding_tracker<decoder_type>)
            .def("is_partial_complete", &is_partial_complete<decoder_type>)
        ;

        void (decoder_type::*decode_symbol2)(uint8_t*, uint32_t) =
            &decoder_type::decode_symbol;
        decoder_class.def("decode_symbol_at_index", decode_symbol2);

        extra_decoder_methods<Coder, decoder_type> extra;
        extra(decoder_class);

        boost::python::register_ptr_to_python<boost::shared_ptr<decoder_type>>();
    }
}



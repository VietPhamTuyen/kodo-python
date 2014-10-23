// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <Python.h>
#include <bytesobject.h>

#include <boost/python/args.hpp>

#include <kodo/has_partial_decoding_tracker.hpp>
#include <kodo/is_partial_complete.hpp>
#include <kodo/write_feedback.hpp>

#include <sak/storage.hpp>

#include <algorithm>
#include <string>
#include <vector>

#include "coder.hpp"
#include "resolve_field_name.hpp"

namespace kodo_python
{

    template<class Decoder>
    PyObject* copy_symbols(Decoder& decoder)
    {
        std::vector<uint8_t> payload(decoder.block_size());
        auto storage = sak::mutable_storage(
            payload.data(), decoder.block_size());
        decoder.copy_symbols(storage);
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize(
            (char*)payload.data(), decoder.block_size());
        #else
        return PyString_FromStringAndSize(
            (char*)payload.data(), decoder.block_size());
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

    template<bool HAS_PARTIAL_DECODING_TRACKER, class Type>
    struct is_partial_complete_method
    {
        template<class DecoderClass>
        is_partial_complete_method(DecoderClass& decoder_class)
        {
            (void) decoder_class;
        }
    };

    template<class Type>
    struct is_partial_complete_method<true, Type>
    {
        template<class DecoderClass>
        is_partial_complete_method(DecoderClass& decoder_class)
        {
            decoder_class
            .def("is_partial_complete", &is_partial_complete<Type>,
                "Check whether the decoding matrix is partially decoded.\n\n"
                "\t:returns: True if the decoding matrix is partially "
                "decoded.\n");
        }
    };

    template<template<class, class> class Coder, class Type>
    struct extra_decoder_methods
    {
        template<class DecoderClass>
        extra_decoder_methods(DecoderClass& decoder_class)
        {
            (void) decoder_class;
        }
    };

    template<class Type>
    struct extra_decoder_methods<kodo::sliding_window_decoder, Type>
    {
        template<class DecoderClass>
        extra_decoder_methods(DecoderClass& decoder_class)
        {
            decoder_class
            .def("feedback_size", &Type::feedback_size,
                "Return the required feedback buffer size in bytes.\n\n"
                "\t:returns: The required feedback buffer size in bytes.\n"
            )
            .def("write_feedback", &write_feedback<Type>,
                "Return a buffer containing the feedback.\n\n"
                "\t:returns: A buffer containing the feedback.\n");
        }
    };

    template<template<class, class> class Coder, class Field, class TraceTag>
    void decoder(const std::string& stack, bool trace)
    {
        using boost::python::arg;

        std::string field = resolve_field_name<Field>();

        std::string s = "_";
        std::string kind = "decoder";
        std::string trace_string = trace ? "_trace" : "";
        std::string name = stack + s + kind + s + field + trace_string;

        typedef Coder<Field, TraceTag> decoder_type;
        auto decoder_class = coder<Coder, Field, TraceTag>(name)
        .def("recode", &recode<decoder_type>,
            "Recode symbol.\n\n"
            "\t:returns: The recoded symbol.\n"
        )
        .def("decode", &decode<decoder_type>, arg("symbol_data"),
            "Decode the provided encoded symbol.\n\n"
            "\t:param symbol_data: The encoded symbol.\n"
        )
        .def("decode_symbol", &decode_symbol<decoder_type>,
            arg("symbol_data"), arg("symbol_coefficients"),
            "Decode encoded symbol according to the coding coefficients.\n\n"
            "\t:param symbol_data: The encoded symbol.\n"
            "\t:param symbol_coefficients: The coding coefficients used to "
            "create the encoded symbol.\n"
        )
        .def("is_complete", &decoder_type::is_complete,
            "Check whether decoding is complete.\n\n"
            "\t:returns: True if the decoding is complete.\n"
        )
        .def("symbols_uncoded", &decoder_type::symbols_uncoded,
            "Return the number of uncoded symbols.\n\n"
            "\t:returns: The number of symbols which have been uncoded.\n"
        )
        .def("copy_symbols", &copy_symbols<decoder_type>,
            "Return the decoded symbols.\n\n"
            "\t:returns: The decoded symbols.\n"
        )
        .def("is_symbol_uncoded", &decoder_type::is_symbol_uncoded,
            arg("index"),
            "Return whether the symbol is uncoded or not.\n\n"
            "\t:param index: Index of the symbol to check.\n"
            "\t:returns: True if the symbol is uncoded, and otherwise false.\n"
        );

        void (decoder_type::*decode_symbol2)(uint8_t*, uint32_t) =
            &decoder_type::decode_symbol;
        decoder_class.def("decode_symbol_at_index", decode_symbol2);

        is_partial_complete_method<
            kodo::has_partial_decoding_tracker<decoder_type>::value,
            decoder_type>
            is_partial_complete_method(decoder_class);

        extra_decoder_methods<Coder, decoder_type> extra_decoder_methods(
            decoder_class);
    }
}



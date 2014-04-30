// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

namespace kodo_python
{
    template<class Encoder>
    bool is_systematic(const Encoder& encoder)
    {
        return kodo::is_systematic_encoder(encoder);
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
    void set_symbols(Encoder& encoder, std::string data)
    {
        auto storage = sak::const_storage((uint8_t*)data.c_str(), data.length());
        encoder.set_symbols(storage);
    }

    template<class Encoder>
    std::string encode(Encoder& encoder)
    {
        std::vector<uint8_t> payload(encoder.payload_size());
        uint32_t length = encoder.encode(payload.data());
        std::string str(payload.begin(), payload.begin() + length);
        return str;
    }

    template<class Coder>
    void encoder(const std::string& name)
    {
        typedef Coder encoder_type;
        boost::python::class_<encoder_type, boost::noncopyable>(name.c_str(),
            boost::python::no_init)
            .def("payload_size", &encoder_type::payload_size)
            .def("block_size", &encoder_type::block_size)
            .def("symbol_size", &encoder_type::symbol_size)
            .def("symbols", &encoder_type::symbols)
            .def("rank", &encoder_type::rank)
            .def("is_symbol_pivot", &encoder_type::is_symbol_pivot)
            .def("encode", &encode<encoder_type>)
            .def("set_symbols", &set_symbols<encoder_type>)
            .def("set_symbol", &encoder_type::set_symbol)
            .def("is_systematic", &is_systematic<encoder_type>)
            .def("is_systematic_on", &is_systematic_on<encoder_type>)
            .def("set_systematic_on", &set_systematic_on<encoder_type>)
            .def("set_systematic_off", &set_systematic_off<encoder_type>)
        ;

        boost::python::register_ptr_to_python<boost::shared_ptr<encoder_type>>();
    }
}

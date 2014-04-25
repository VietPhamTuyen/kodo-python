#include <boost/python.hpp>
#include <boost/python/register_ptr_to_python.hpp>
#include <fifi/default_field.hpp>
#include <kodo/rlnc/full_vector_codes.hpp>

#include "encoder.hpp"


namespace kodo_python
{
    BOOST_PYTHON_MODULE(kodo)
    {
        typedef kodo::full_rlnc_encoder<fifi::binary>::factory factory_type;
        boost::python::class_<factory_type, boost::noncopyable>("encoder_factory",
            boost::python::init<uint32_t, uint32_t>())
            .def("build", &factory_type::build)
            .def("set_symbols", &factory_type::set_symbols)
            .def("set_symbol_size", &factory_type::set_symbol_size)
            .def("max_symbols", &factory_type::max_symbols)
            .def("max_symbol_size", &factory_type::max_symbol_size)
            .def("max_block_size", &factory_type::max_block_size)
            .def("max_payload_size", &factory_type::max_payload_size)
        ;

        typedef encoder<kodo::full_rlnc_encoder<fifi::binary>> encoder_type;
        boost::python::class_<encoder_type, boost::noncopyable>("encoder",
            boost::python::no_init)
            .def("payload_size", &encoder_type::payload_size)
            .def("block_size", &encoder_type::block_size)
            .def("symbol_size", &encoder_type::symbol_size)
            .def("symbols", &encoder_type::symbols)
            .def("rank", &encoder_type::rank)
            .def("is_symbol_pivot", &encoder_type::is_symbol_pivot)
            .def("encode", &encoder_type::encode)
            .def("set_symbols", &encoder_type::set_symbols)
            .def("set_symbol", &encoder_type::set_symbol)
            .def("is_systematic", &encoder_type::is_systematic)
            .def("is_systematic_on", &encoder_type::is_systematic_on)
            .def("set_systematic_on", &encoder_type::set_systematic_on)
            .def("set_systematic_off", &encoder_type::set_systematic_off)
        ;

        boost::python::register_ptr_to_python<boost::shared_ptr<encoder_type>>();
    }
}

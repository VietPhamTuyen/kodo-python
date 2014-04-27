#include <boost/python.hpp>
#include <boost/python/register_ptr_to_python.hpp>
#include <fifi/default_field.hpp>
#include <kodo/rlnc/full_vector_codes.hpp>

#include <sak/storage.hpp>
#include <kodo/systematic_operations.hpp>
namespace kodo_python
{
    template<class T>
    boost::python::list std_vector_to_py_list(const std::vector<T>& v)
    {
        boost::python::object get_iter = boost::python::iterator<std::vector<T> >();
        boost::python::object iter = get_iter(v);
        boost::python::list l(iter);
        return l;
    }


    bool is_systematic(const kodo::full_rlnc_encoder<fifi::binary>& encoder)
    {
        return kodo::is_systematic_encoder(encoder);
    }

    bool is_systematic_on(const kodo::full_rlnc_encoder<fifi::binary>& encoder)
    {
        return kodo::is_systematic_on(encoder);
    }

    void set_systematic_on(kodo::full_rlnc_encoder<fifi::binary>& encoder)
    {
        kodo::set_systematic_on(encoder);
    }

    void set_systematic_off(kodo::full_rlnc_encoder<fifi::binary>& encoder)
    {
        kodo::set_systematic_off(encoder);
    }

    void set_symbols(kodo::full_rlnc_encoder<fifi::binary>& encoder, std::string data)
    {
        auto storage = sak::const_storage((uint8_t*)data.c_str(), data.length());
        encoder.set_symbols(storage);
    }

    boost::python::list encode(kodo::full_rlnc_encoder<fifi::binary>& encoder)
    {
        std::vector<int> payload(encoder.payload_size());
        encoder.encode((uint8_t*)payload.data());
        return std_vector_to_py_list(payload);
    }

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

        typedef kodo::full_rlnc_encoder<fifi::binary> encoder_type;
        boost::python::class_<encoder_type, boost::noncopyable>("encoder",
            boost::python::no_init)
            .def("payload_size", &encoder_type::payload_size)
            .def("block_size", &encoder_type::block_size)
            .def("symbol_size", &encoder_type::symbol_size)
            .def("symbols", &encoder_type::symbols)
            .def("rank", &encoder_type::rank)
            .def("is_symbol_pivot", &encoder_type::is_symbol_pivot)
            .def("encode", encode)
            .def("set_symbols", set_symbols)
            .def("set_symbol", &encoder_type::set_symbol)
            .def("is_systematic", is_systematic)
            .def("is_systematic_on", is_systematic_on)
            .def("set_systematic_on", set_systematic_on)
            .def("set_systematic_off", set_systematic_off)
        ;

        boost::python::register_ptr_to_python<boost::shared_ptr<encoder_type>>();
    }
}

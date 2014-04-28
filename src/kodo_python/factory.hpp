#pragma once

namespace kodo_python
{
    template<class Coder>
    void factory(const std::string& name)
    {
        typedef typename Coder::factory factory_type;
        boost::python::class_<factory_type, boost::noncopyable>(name.c_str(),
            boost::python::init<uint32_t, uint32_t>())
            .def("build", &factory_type::build)
            .def("set_symbols", &factory_type::set_symbols)
            .def("set_symbol_size", &factory_type::set_symbol_size)
            .def("max_symbols", &factory_type::max_symbols)
            .def("max_symbol_size", &factory_type::max_symbol_size)
            .def("max_block_size", &factory_type::max_block_size)
            .def("max_payload_size", &factory_type::max_payload_size)
        ;
    }
}

// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#if !defined(KODO_PYTHON_DISABLE_RLNC) && \
    !defined(KODO_PYTHON_DISABLE_FULL_VECTOR)

#include <kodo_rlnc/full_vector_codes.hpp>

#include "create_helpers.hpp"

namespace kodo_python
{
    template<>
    struct extra_encoder_methods<kodo_rlnc::sparse_full_vector_encoder>
    {
        template<class EncoderClass>
        extra_encoder_methods(EncoderClass& encoder_class)
        {
            using boost::python::arg;
            encoder_class
            .def("set_density",
                &EncoderClass::wrapped_type::set_density, arg("density"),
                "Set the density of the coefficients generated.\n\n"
                "\t:param density: The coefficients density.\n"
            )
            .def("density",
                &EncoderClass::wrapped_type::density,
                "Get the density of the coefficients generated.\n\n"
                "\t:returns: The density of the generator.\n"
            )
            .def("set_average_nonzero_symbols",
                &EncoderClass::wrapped_type::set_average_nonzero_symbols,
                arg("symbols"),
                "Set the average number of nonzero symbols.\n\n"
                "\t:param symbols: The average number of nonzero symbols.\n"
            );
        }
    };

    void create_full_vector_stacks()
    {
        using namespace kodo_rlnc;

        create_encoder<full_vector_encoder>("FullVector");
        create_decoder<full_vector_decoder>("FullVector");

        create_encoder<sparse_full_vector_encoder>("SparseFullVector");
    }
}

#endif

// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#if !defined(KODO_PYTHON_DISABLE_RLNC) && \
    !defined(KODO_PYTHON_DISABLE_ON_THE_FLY)

#include <kodo_rlnc/on_the_fly_codes.hpp>

#include "create_helpers.hpp"

namespace kodo_python
{
    void create_on_the_fly_stacks()
    {
        using namespace kodo_rlnc;

        create_encoder<on_the_fly_encoder>("OnTheFly");
        create_decoder<on_the_fly_decoder>("OnTheFly");
    }
}

#endif

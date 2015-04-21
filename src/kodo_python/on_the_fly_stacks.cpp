// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#include <kodo/rlnc/on_the_fly_codes.hpp>

#include "create_helpers.hpp"

namespace kodo_python
{
    void create_on_the_fly_stacks()
    {
        using namespace kodo::rlnc;

        create_field<on_the_fly_encoder>("OnTheFly");
        create_field<on_the_fly_decoder>("OnTheFly");
    }
}

// Copyright Steinwurf ApS 2011-2012.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <sak/storage.hpp>
#include <kodo/systematic_operations.hpp>
#include <cstdint>

namespace kodo_python
{
    template<class Coder, class Stack>
    class factory : public Stack::factory
    {

    public:

        Coder build()
        {
            return encoder(Stack::factory.build());
        }
    };
}

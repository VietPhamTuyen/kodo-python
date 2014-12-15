// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <type_traits>

namespace kodo_python
{
    /// Helper that allows compile time detection of whether a
    /// stack is an encoder or decoder stack.
    ///
    /// Example:
    ///
    /// typedef kodo::full_rlnc8_encoder encoder_t;
    ///
    /// if(kodo_python::has_encode<encoder_t>::value)
    /// {
    ///     // Do something here
    /// }

    template<typename T>
    struct has_encode
    {
    private:
        typedef std::true_type yes;
        typedef std::false_type no;

        template<typename U>
        static auto test(int) ->
            decltype(std::declval<U>().encode(0), yes());

        template<typename> static no test(...);

    public:

        enum { value = std::is_same<decltype(test<T>(0)),yes>::value };
    };

}

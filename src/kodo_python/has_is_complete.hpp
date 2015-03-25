// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <type_traits>

namespace kodo_python
{
    /// Helper that allows compile time detection of whether a
    /// stack has the is_complete member function, i.e., whether it's a decoder
    /// or an encoder stack.
    ///
    /// Example:
    ///
    /// typedef kodo::full_rlnc_encoder<fifi::binary8> encoder_t;
    ///
    /// if(kodo_python::has_is_complete<encoder_t>::value)
    /// {
    ///     // Do something here
    /// }

    template<typename T>
    struct has_is_complete
    {
    private:
        typedef std::true_type yes;
        typedef std::false_type no;

        template<typename U>
        static auto test(int) ->
            decltype(std::declval<U>().is_complete(), yes());

        template<typename> static no test(...);

    public:

        enum { value = std::is_same<decltype(test<T>(0)), yes>::value };
    };
}

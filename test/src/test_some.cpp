#include <gtest/gtest.h>
#include <kodo_python/some.hpp>

TEST(TestSome, return_value_of_some_method)
{
    ::some s;
    EXPECT_TRUE(s.some_method());
}

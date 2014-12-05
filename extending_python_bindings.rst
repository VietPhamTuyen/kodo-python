Extending the Kodo Python Bindings
==================================

The scope of the kodo-python bindings is not to contain all the functions and
stacks of the Kodo library. This is not practical nor useful.

If you find that something is missing, you can either make an issue and
argue why the feature you want should be present in the Kodo python API, or even
better you can try to add this yourself and create a pull request.

This document serves as a guide on how to add new functions and stacks.

The entry point for the bindings are the ``src/kodo_python/kodo.cpp`` file.
This contains a set of of helper function and classes. These are used make it
easier to handle the different variations of each stack.

* **create_stacks**: This function specifies the stacks which are to be
  included.
* **create_trace**: This function ensure that all stacks has two versions, one
  with trace, and one without.
* **create_field**: This function is in charge of which fields the stacks
  defined in ``create_stacks`` should support.
* **create/create_coder**: The function and associated helper structs are used
  for creating a decoder if the stack is a decoder, or an encoder if the stack
  is an encoder. It's very unlikely that you will have to make changes here.

Please note that when a new stack or a new field is added the kodo python
library grows in size.

If you add a new function, a new function will be added to all stack
combinations. As an example if we add a new function to all the encoders, the
actual number of new functions added will be::

  number_of_stacks * number_of_fields * with_and_without_trace = 3 * 4 * 2 = 24

Adding a New Stack
------------------

If you want to add a stack you should do so in the ``create_stacks`` function.
If your stack has both an encoder and decoder part, you need to add both.

You can use the current stacks as inspiration when adding a new one.

If the stack you've added has special functions you want to expose please see
`Adding a Stack Specific Function`_.

Adding a New Field
------------------

If you want to add a new field, and you want this field to be available in all
stacks, you need to add it in the ``create_field`` function.

Adding a New Function
---------------------

If the function can be added without any additional mapping functionality,
exposing a function can be done very quickly.
The following shows how the ``set_symbols`` function looks::

  .def("set_symbols", &factory_type::set_symbols, arg("symbols"),
       "Set the number of symbols.\n\n"
       "\t:param symbols: The number of symbols.\n"
  )

The first parameter defines what the function should be called in python,
the second parameter is a function pointer to the factory's ``set_symbol``
function.
The third is the parameter name(s), this is used to call the function from
python with named arguments. If the function takes multiple arguments you need
to use ``args`` instead of ``arg``.
The fourth and final parameter is the docstring of the function. All functions
should have a docstring which follows the `pep257 style guide
<http://legacy.python.org/dev/peps/pep-0257/>`_. Furthermore the parameters
of the function should be documented using the sphinx style with::

  :param parameter_name: Explanation of parameter_name.

Where ``parameter_name`` should be exchanged with the appropriate parameter
name.

If the function you want to expose can't be exposed directly you must create a
helper function which can handle the communication between python and c++.

And example of this is the trace method::

    template<class Coder>
    void trace(Coder& coder)
    {
        kodo::trace(coder, std::cout);
    }

    ...

    .def("trace", &trace<Type>,
        "Write the trace information to stdout.\n"
    )

The Kodo trace function takes the coder and a stream where the trace output
should be outputted. This is not possible in python, furthermore, we would like
this to be a method on the coder object in python.
To do so we create a function in c++ called trace, this takes the coder as a
reference, and to make it usable for all coders, we template it.
We default to always use ``std::cout``. Alternatively the function could have
returned at string with the data and we could ourselves print the results in
python.

Hopefully this will give you an idea about how to approach the task of adding
new functions. If you are in doubt you can try to look at how the current
functions have been implemented.

Adding a General Function
^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to add a new function which is available to all stacks, it must
obviously be available on all stacks.
Depending on where the function is defined, it should be added in the
constructor of either one of the following classes.

* **coder**: If the function is available on both the encoder and decoder.
* **encoder**: If the function is available on the encoder.
* **decoder**: If the function is available on the decoder.
* **factory**: If the function is available on the factory - for both the
  encoder and decoder factory.

Adding a Stack Specific Function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some times a stack exposes a special API which no other stack exposes. To
accommodate this we have use a template specialized struct called
``extra_decoder_methods`` and ``extra_encoder_methods`` for the decoder and
encoder respectively.

To add a function only to a certain stack you need to partially template
specialize the struct and add the special functions in the structs constructor.

An example of this is the ``sliding_window_encoder``. This stack exposes the
feedback API which includes the ``feedback_size`` and ``read_feedback``
functions. The following shows how this is implemented.

  template<class Type>
  struct extra_encoder_methods<kodo::sliding_window_encoder, Type>
  {
      template<class EncoderClass>
      extra_encoder_methods(EncoderClass& encoder_class)
      {
          encoder_class
          .def("feedback_size", &Type::feedback_size,
              "Return the required feedback buffer size in bytes.\n\n"
              "\t:returns: The required feedback buffer size in bytes.\n"
          )
          .def("read_feedback", &read_feedback<Type>,
              "Return the feedback information.\n\n"
              "\t:returns: The feedback information.\n");
      }
  };
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "game_instance.h"
#include "bitboards.h"
#include "move_gen.h"

/*
 * Implements an example function.
 */

PyDoc_STRVAR(Stratego_example_doc, "example(obj, number)\
\
Example function");


PyObject *Stratego_example(PyObject *self, PyObject *args, PyObject *kwargs) {
    /* Shared references that do not need Py_DECREF before returning. */
    PyObject *obj = NULL;
    int number = 0;

    /* Parse positional and keyword arguments */
    static char* keywords[] = { "obj", "number", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Oi", keywords, &obj, &number)) {
        return NULL;
    }

    /* Function implementation starts here */

    if (number < 0) {
        PyErr_SetObject(PyExc_ValueError, obj);
        return NULL;    /* return NULL indicates error */
    }

    Py_RETURN_NONE;
}

/*
 * List of functions to add to Stratego in exec_Stratego().
 */
static PyMethodDef Stratego_functions[] = {
    { "example", (PyCFunction)Stratego_example, METH_VARARGS | METH_KEYWORDS, Stratego_example_doc },
    { NULL, NULL, 0, NULL } /* marks end of array */
};

/*
 * Initialize Stratego. May be called multiple times, so avoid
 * using static state.
 */
int exec_Stratego(PyObject *module) {
    PyModule_AddFunctions(module, Stratego_functions);

    PyModule_AddStringConstant(module, "__author__", "Pawwz");
    PyModule_AddStringConstant(module, "__version__", "1.0.0");
    PyModule_AddIntConstant(module, "year", 2024);

    return 0; /* success */
}

/*
 * Documentation for Stratego.
 */
// PyDoc_STRVAR(Stratego_doc, "The Stratego module");


static PyModuleDef_Slot Stratego_slots[] = {
    { Py_mod_exec, exec_Stratego },
    { 0, NULL }
};

static PyModuleDef Stratego_def = {
    PyModuleDef_HEAD_INIT,
    "Stratego",
    NULL, //Stratego_doc,
    0,              /* m_size */
    NULL,           /* m_methods */
    Stratego_slots,
    NULL,           /* m_traverse */
    NULL,           /* m_clear */
    NULL,           /* m_free */
};

PyMODINIT_FUNC PyInit_Stratego() {
    return PyModuleDef_Init(&Stratego_def);
}

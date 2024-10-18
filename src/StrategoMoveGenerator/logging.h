#pragma once
#include <fstream>

//#define _DEBUG_LOGS 1

#ifdef _DEBUG_LOGS
// Define Logging  functions here
extern std::ofstream __debug_log_stream;
extern int __open_debug_stream();
static const int __debug_initializer = __open_debug_stream();

#define DEBUG_PRINTLN(X) __debug_log_stream << X << "\n";
#define DEBUG_PRINT(X) __debug_log_stream << X;

#else
#define DEBUG_PRINTLN(X) 
#define DEBUG_PRINT(X) 
#endif // _DEBUG_LOGS

#include "pch.h"
#include "logging.h"
#include <iostream>

#ifdef _DEBUG_LOGS
std::ofstream __debug_log_stream("StrategoMoveGenerator_DebugLogs.txt");
int __open_debug_stream()
{
    std::cout << & __debug_log_stream;

    if (__debug_log_stream.is_open())
        return 0;

    return 1;
}


#endif

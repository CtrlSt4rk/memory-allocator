# memory-allocator
A simple memory allocation simulator, that can dynamically fill memory with mapped and unmapped addresses according to the defined available memory size and mapped region. It also includes a swap mechanism (coldest page first) that will start if the number of requested accesses surpasses the number of pages that can be stored in memory.

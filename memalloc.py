import sys
import random
import numpy as np

memory_heap_size = 262144 #total memory size
memory_heap_mmap = 131027 #196563 #65536 #mapped mem size
page_size = 4096
percent_page_fault = int(sys.argv[1])

#depending on memory alloc, set max pages that can be mapped or not mapped
mem_mapped = memory_heap_mmap
mem_unmapped = memory_heap_size - memory_heap_mmap

qtt_accesses = 100000 #Will trigger swap mechanism if larger then fits on memory
qtt_mem_pages = int(memory_heap_size / page_size)
max_pages_mapped = mem_mapped / page_size
max_pages_unmapped = qtt_mem_pages - max_pages_mapped

if max_pages_unmapped != 0:
	if max_pages_unmapped % (int (max_pages_unmapped)) >= 0.5:
		max_pages_unmapped = int (max_pages_unmapped) + 1
	else:
		max_pages_unmapped = int (max_pages_unmapped)

if max_pages_mapped != 0:
	if max_pages_mapped % (int (max_pages_mapped)) >= 0.5:
		max_pages_mapped = int (max_pages_mapped) + 1
	else:
		max_pages_mapped = int (max_pages_mapped)

#check if percent_page_fault is in range
if percent_page_fault > 100:
	print ("Input Error")
	exit()

#check qtt pages that cause fault or not, according to percentage_page_fault
if percent_page_fault < 50:
	if percent_page_fault == 0:
		qtt_mem_pages_mapped = max_pages_mapped
		qtt_mem_pages_unmapped = 0
	else:
		if (max_pages_unmapped * percent_page_fault / 100) < (max_pages_mapped * (100-percent_page_fault) / 100):
			#print ("\n1") #TODO error mmap > mem/2
			qtt_mem_pages_mapped = max_pages_mapped
			qtt_mem_pages_unmapped = int(qtt_mem_pages_mapped * percent_page_fault/100 /((100-percent_page_fault)/100))
			
		if (max_pages_unmapped * percent_page_fault / 100) >= (max_pages_mapped * (100-percent_page_fault) / 100):
			qtt_mem_pages_mapped = max_pages_mapped
			qtt_mem_pages_unmapped = int(qtt_mem_pages_mapped * percent_page_fault/100 /((100-percent_page_fault)/100))

else:
	if percent_page_fault == 100:
		qtt_mem_pages_mapped = 0
		qtt_mem_pages_unmapped = max_pages_unmapped
	else:
		if (max_pages_mapped * (100-percent_page_fault) / 100) < (max_pages_unmapped * percent_page_fault / 100):
			#print ("\n3") #TODO error mmap < mem/2
			qtt_mem_pages_unmapped = max_pages_unmapped
			qtt_mem_pages_mapped = int(qtt_mem_pages_unmapped * (100-percent_page_fault)/100 /(percent_page_fault/100))

		if (max_pages_mapped * (100-percent_page_fault) / 100) >= (max_pages_unmapped * percent_page_fault / 100):
			qtt_mem_pages_unmapped = max_pages_unmapped
			qtt_mem_pages_mapped = int(qtt_mem_pages_unmapped * (100-percent_page_fault)/100 /(percent_page_fault/100))

#aprox values so it always fit on mem --> >=.5 (+1) <.5 (-1)
if qtt_mem_pages_unmapped != 0:
	if qtt_mem_pages_unmapped % (int (qtt_mem_pages_unmapped)) >= 0.5:
		qtt_mem_pages_unmapped = int (qtt_mem_pages_unmapped) + 1
	else:
		qtt_mem_pages_unmapped = int (qtt_mem_pages_unmapped)

if qtt_mem_pages_mapped != 0:
	if qtt_mem_pages_mapped % (int (qtt_mem_pages_mapped)) >= 0.5:
		qtt_mem_pages_mapped = int (qtt_mem_pages_mapped) + 1
	else:
		qtt_mem_pages_mapped = int (qtt_mem_pages_mapped)

#array that contains the status of every page address (mapped or unmapped)
mem_array_flag = [-1] * qtt_mem_pages

#load flag array
for i in range (0, qtt_mem_pages): #qtt_mem_pages=64
	if i >= max_pages_mapped and i < max_pages_mapped + qtt_mem_pages_unmapped: 
		mem_array_flag[i] = 0 #page fault
	if i < qtt_mem_pages_mapped:
		mem_array_flag[i] = 1 #pagehit

timestamp_array = [-1] * qtt_mem_pages
timestamp_array_pos = 0

#load initial page addr on array
mem_array = [-1] * qtt_mem_pages
for i in range (0, qtt_mem_pages):
	if (mem_array_flag[i] == 1 or mem_array_flag[i] == 0):
		mem_array[i] = i*page_size
		timestamp_array [i] = timestamp_array_pos
		timestamp_array_pos = timestamp_array_pos+1

print ("Timestamp before swap mechanism")
print (timestamp_array)

print ("Initial mem array flag, 0=pagefault, 1=pagehit, -1=empty")
print (mem_array_flag)

print ("Initial mem array")
print (mem_array)

#does the page swap mechanism
#counter for page_fault or not_page_fault pages after initial array is defined
extra_page_fault_counter = 0
extra_not_page_fault_counter = 0
extra_qtt_accesses = qtt_accesses-qtt_mem_pages
current_percent_pf_weight = 50
weight_page_fault = 1
weight_not_page_fault = 1

for i in range (0, extra_qtt_accesses):
	oldest_page_pos = np.argmin(timestamp_array)
	newest_page_value = np.max(timestamp_array)
	oldest_page_value = timestamp_array[oldest_page_pos]

	page_status = -1 # 0 for page_fault, 1 for page_hit (not_page_fault)
	
	#check if it will be page_fault or not_page_fault
	if ((current_percent_pf_weight <= percent_page_fault) or (extra_page_fault_counter == 0 and extra_not_page_fault_counter == 0)):
		page_status = 0
		weight_page_fault = weight_page_fault + 1
		current_percent_pf_weight = (weight_page_fault/(weight_page_fault+weight_not_page_fault)*100)
		extra_page_fault_counter = extra_page_fault_counter+1
	else: 
		page_status = 1
		weight_not_page_fault = weight_not_page_fault+1
		current_percent_pf_weight = (weight_page_fault / (weight_page_fault+weight_not_page_fault)*100)
		extra_not_page_fault_counter = extra_not_page_fault_counter+1

	#find selected page and overwrite with new values
	timestamp_array[oldest_page_pos] = newest_page_value+1
	mem_array_flag[oldest_page_pos] = page_status
	if mem_array_flag[oldest_page_pos] == 0:
		mem_array[oldest_page_pos] = memory_heap_mmap + oldest_page_pos * page_size
	if mem_array_flag[oldest_page_pos] == 1:
		mem_array[oldest_page_pos] = oldest_page_pos * page_size

#save the final array to file
with open('mem_array.c', 'w') as f:
	#(c file can be incorporated into the main code --> faster than reading from file)
	for i in range (0, qtt_mem_pages):
		if i == 0:
			f.write("long mem_addr_array[] = {"+str(mem_array[i])+", ")
		if i > 0 and i < qtt_mem_pages-1:
			f.write(str(mem_array[i])+", ")
		if i == qtt_mem_pages-1:
			f.write(str(mem_array[i])+"};")

print ("\nTimestamp after swap mechanism")
print (timestamp_array)

print ("Mem array flag, 0=pagefault, 1=pagehit, -1=empty")
print (mem_array_flag)

print ("Final mem array")
print (mem_array)

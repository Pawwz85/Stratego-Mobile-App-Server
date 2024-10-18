/*
	LUT - Look up table
	Garbage - Any LUT entry that is not a valid data
	density = 1 - (Garbage count)/(LUT's size)

	This file implements an algorithm that tries to compress multiple low density LUTs into LUT with more density.
*/
#pragma once
#include "pch.h"
#include "fixed_arr.hpp"
#include <algorithm>

template <typename T>
struct LUT_opt_result{
	fixed_arr<T> LUT;
	fixed_arr<size_t> offsets;
};

template <typename T>
struct __LUT {
	fixed_arr<T> data;
	bool (*isGarbage)(const T &);
};

template <typename T>
LUT_opt_result<T> LUT_opt(const fixed_arr<__LUT<T>> LUTs) {
	LUT_opt_result<T> result;
	result.offsets = fixed_arr<size_t>(LUTs.get_size());
	size_t current_offset, current_lut, some_lut, absolute_index;
	bool found_valid_offset;

	// Step 1. Sort LUTs by their length
	fixed_arr<size_t> order(LUTs.get_size());
	for (size_t i = 0; i < order.get_size(); ++i)
		order[i] = i;

	class comp {
		const fixed_arr<__LUT<T>>* LUTs;
	public:
		comp(const fixed_arr<__LUT<T>> & LUTs) {
			this->LUTs = &LUTs;
		}
		int operator()(const size_t& index1, const size_t& index2) {
			return std::greater<size_t>()((*LUTs)[index1].data.get_size(), (*LUTs)[index2].data.get_size());
		}
	};

	size_t* raw_order = order.c_array();
	std::sort(raw_order, raw_order + order.get_size(), comp(LUTs));
	order = fixed_arr<size_t>(raw_order, order.get_size());
	delete[] raw_order;

	// step 2. Greedy search for best offsets
	result.offsets[order[0]] = 0; 
	for (size_t order_i = 1; order_i < order.get_size(); ++order_i) {
		current_lut = order[order_i];
		current_offset = 0; 
		found_valid_offset = false;

		while (!found_valid_offset) {
			for (size_t i = 0; i < LUTs[current_lut].data.get_size(); ++i) {
				
				if(LUTs[current_lut].isGarbage(LUTs[current_lut].data[i]))
					continue;

				absolute_index = current_offset + i;

				// iterate previous LUTS to find if  collision eliminates offset
				for (size_t order_j = 0; order_j < order_i; ++order_j) {
					some_lut = order[order_j];

					if (absolute_index < result.offsets[some_lut] ||
						absolute_index >= result.offsets[some_lut] + LUTs[some_lut].data.get_size())
						continue; // we are not overlapping this lut



						if (!LUTs[some_lut].isGarbage(LUTs[some_lut].data[absolute_index - result.offsets[some_lut]]))
							goto OFFSET_FAILED; // Offset failed, cause we are colliding with no garbage value

				}
			}
			found_valid_offset = true;
			OFFSET_FAILED:
			if (!found_valid_offset)
			++current_offset;
		}
		result.offsets[current_lut] = current_offset;
	}

	// step 3. Calculate last useful index, for extra space, and final result size
	
	// TODO: this function leaves Garbage values at the end, fix that
	size_t last_useful_index = result.offsets[0] + LUTs[0].data.get_size();
	for (size_t i = 1; i < LUTs.get_size(); ++i)
		if (last_useful_index < result.offsets[i] + LUTs[i].data.get_size())
			last_useful_index = result.offsets[i] + LUTs[i].data.get_size();

	// step 4: compose a result array
	T* final_LUT = new T[last_useful_index + 1];

	for (size_t i = 0; i < last_useful_index + 1; ++i)
		final_LUT[i] = T();

	for (size_t i = 0; i < LUTs.get_size(); ++i) {
		for (size_t j = 0; result.offsets[i] + j <= last_useful_index && j < LUTs[i].data.get_size(); ++j)
			if (!LUTs[i].isGarbage(LUTs[i].data[j]))
				final_LUT[result.offsets[i] + j] = LUTs[i].data[j];
	}

	result.LUT = fixed_arr<T>(final_LUT, last_useful_index + 1);

	delete[] final_LUT;
	return result;
}
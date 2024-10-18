#pragma once
#include "pch.h"
#include <stdexcept>

; // For some retarded reason this semicolon is mandatory, wild huh?
template <typename T> class fixed_arr {
private:
	T* arr;
	size_t size;
	inline void lval_copy(const fixed_arr<T>& other);
public:
	fixed_arr(T* src, size_t size); // shallow copies an 'size' amount of elements from 'src' internally, no ownership over src pointer is taken
	fixed_arr(size_t size);
	fixed_arr();
	fixed_arr(const fixed_arr<T>& other);

	~fixed_arr();

	size_t get_size() const;
	T* c_array(); // returns an unboundend array, user has ownership, also returns nullptr if array is empty
	
	fixed_arr<T>& operator=(const fixed_arr<T>& other);
	
	inline T& operator[](size_t index) {
		if (index >= this->size) {
			throw std::out_of_range("Array index out of bounds.");
		}
		return arr[index];
	};
	inline const T& operator[](size_t index) const {
		if (index >= this->size) {
			throw std::out_of_range("Array index out of bounds.");
		}
		return arr[index];
	};
};

template<typename T>
inline void fixed_arr<T>::lval_copy(const fixed_arr<T>& other)
{
	this->size = other.size;
	this->arr = new T[this->size];
	for (size_t i = 0; i < this->size; ++i)
		this->arr[i] = other[i];
}

template<typename T>
inline fixed_arr<T>::fixed_arr(T* src, size_t size)
{
	this->arr = new T[size];
	this->size = size;
	for (size_t i = 0; i < size; ++i)
		this->arr[i] = src[i];
}

template<typename T>
inline fixed_arr<T>::fixed_arr(size_t size)
{
	this->arr = new T[size];
	this->size = size;
}

template<typename T>
inline fixed_arr<T>::fixed_arr()
{
	this->arr = nullptr;
	this->size = 0;
}

template<typename T>
inline fixed_arr<T>::~fixed_arr()
{
	if(this->arr) delete[] this->arr;
}

template<typename T>
inline size_t fixed_arr<T>::get_size() const
{
	return this->size;
}

template<typename T>
inline T* fixed_arr<T>::c_array()
{
	if (!this->arr)
		return nullptr;

	T* result = new T[this->size];
	for (size_t i = 0; i < size; ++i)
		result[i] = this->arr[i];
	return result;
}

template<typename T>
inline fixed_arr<T>::fixed_arr(const fixed_arr<T>& other)
{
	lval_copy(other);
}

template<typename T>
inline fixed_arr<T>& fixed_arr<T>::operator=(const fixed_arr<T>& other)
{
	if (arr)
		delete[] arr;

	lval_copy(other);
	return *this;
}

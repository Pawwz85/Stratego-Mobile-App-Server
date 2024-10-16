#include "pch.h"
#include "fast_magic_boot.h"

Bitboard fastMagicNumbers[100] = {
{ 0x7f7f7fffbf7f7fb8ull, 0xf7fefffffffffff9ull },
{ 0xefffbfffeffffd63ull, 0xfff7ffffbffdfdfbull },
{ 0xdf7ff7f7ffbfffd6ull, 0xff7fffff7ffff19bull },
{ 0xf77ffdfcf37fefb0ull, 0xbbfa77ffdfff7f95ull },
{ 0xffbffffbfdf5fdfcull, 0xfffbefffffffaff6ull },
{ 0xf7f7ffeffdfffff5ull, 0xff7ff7fffffb9fbeull },
{ 0xd7dff7ffeffffff3ull, 0xffdbdfffffff3ff9ull },
{ 0xfeffbff7e7fff558ull, 0xbfffffffbffbf7f2ull },
{ 0xdffefffbbbffef7full, 0x777ff7fffffffffeull },
{ 0xf7feffffefffdfedull, 0xffffbffffffff6fcull },
{ 0xffdff7ffef7ffff4ull, 0xffeff3fbfffff762ull },
{ 0xffbfefffdef7f5f4ull, 0xfffd7fff7feffe96ull },
{ 0xfbf7f7fddf7ffd56ull, 0xfffffff7f77fffdfull },
{ 0xfff7dff7f3ffff3dull, 0xfffdfffaf4ffff56ull },
{ 0xff7ff7fffbff7efaull, 0xfedfffffffffdc6bull },
{ 0x7ffffbfffdfcfefeull, 0xfff6fffff3fff6f1ull },
{ 0xffffdfdff7f7fbd6ull, 0x7fffffff7f7fdf7bull },
{ 0xf7ffefeffff77fdaull, 0xf7ffffffffffffbeull },
{ 0xffffff3dfdff3ff2ull, 0xffffbffffeffbfdfull },
{ 0xf7f7ffbfff5fbe87ull, 0xfffff7ffffffffbdull },
{ 0x7ffbffffdfff6eb2ull, 0xefeffffffbefffd4ull },
{ 0xffffdf5fff7eff7cull, 0xfdf7ffffbfffffe1ull },
{ 0xbffff7f7f777bf7cull, 0xf7fff77ffdbff7bdull },
{ 0x7fdff5fe3f7fffebull, 0xdf7ffbfbffffff26ull },
{ 0xffff6fff7efff7fcull, 0xbfff7ffffffff7f5ull },
{ 0xffff77fff7d5ff73ull, 0x7bfdf7fffffbfbe1ull },
{ 0xbfff7ff7f7ffff70ull, 0xbfff7ffff7fbfed4ull },
{ 0xefffffbfbbaff7ddull, 0xffffffffffffffa1ull },
{ 0xffffdfeffdfdfbf9ull, 0xfffdfffffff7fdd5ull },
{ 0xefff7ffdffffbff8ull, 0xfff7df7dfbfffea9ull },
{ 0xf5ffff7efabffef2ull, 0xf7fbfffffbd1fee0ull },
{ 0x7ffb7fbf7fff7ff2ull, 0xde77f77fffdffef8ull },
{ 0x7ff7f7f7fdffffffull, 0xf77f7ffffbffb7fdull },
{ 0x7ff7d787ee7fffdcull, 0xf6bffffff7fefff9ull },
{ 0xeffbf7fffdefff7dull, 0x7ffdffffffffbfb5ull },
{ 0xfffffff7ff6ffff7ull, 0xdfffff3ffefff7efull },
{ 0xdbff7f4fff7ffe3bull, 0xe7fffffffffffba0ull },
{ 0xeffffbffbb7ffbf9ull, 0xffd3fffdfffbfdf1ull },
{ 0xdfffdfffffdffff3ull, 0xffff5fffffff6de4ull },
{ 0xf3fffeff7faffd86ull, 0xfffefffffffbe655ull },
{ 0x7fff7f7efbff77f6ull, 0x7fefffffdff7ff72ull },
{ 0xffff7f7feffffab4ull, 0xbe7ffffffffbffa0ull },
{ 0xffffafdf7bfffefeull, 0xfdeefffffff77ff6ull },
{ 0xfffffff77ffffda5ull, 0xfffffffefffeff75ull },
{ 0x77fb7f7ffeffef38ull, 0xf77f6ffffeffffecull },
{ 0xffdfbff737fff7f2ull, 0xf7ff7fffffff7df4ull },
{ 0xfffffffdfff7ff7dull, 0xfdffde7fffffbf57ull },
{ 0xefff55fff75bdfeeull, 0xfffffffeffffffecull },
{ 0xffeffbffee7ff9e3ull, 0xb7f2ffffff77ffbdull },
{ 0xeffff7bff7bff7f0ull, 0xffbf77fffefffb55ull },
{ 0x6ffffebefff7fbe3ull, 0xf7f777ffbf3fffa0ull },
{ 0xfeff7f6f7ffd7debull, 0xfffbffffe7fefbe6ull },
{ 0xffffffffbfffed96ull, 0xefeeffffef7ffff8ull },
{ 0xfff7fbfef3f37ff6ull, 0xfffefffdffffffdcull },
{ 0xff7df77feefdf7b8ull, 0xf7fbf7b7ffffffdeull },
{ 0xf5fbfb7bf7eff7f7ull, 0x5defbffffffaffb3ull },
{ 0xbf7ffffb5feffff1ull, 0xdffffefffdf3fffeull },
{ 0xffffdfffff7f7fb1ull, 0xf7fffffff7ffeffaull },
{ 0xffffb7bbff7feedeull, 0xffdfeffff7ffff5bull },
{ 0xfbfffeff7ff77f43ull, 0xfdffbefffffffff8ull },
{ 0xfffffffbbdffeee5ull, 0xffdffff7fffffff6ull },
{ 0xffbfffff77fbf6cbull, 0xffdffd7ffdedfd7eull },
{ 0xbffffffbffffdd73ull, 0xff3fffdffffff739ull },
{ 0x77ffffffdf6bffffull, 0x7fd7beffffbff5f9ull },
{ 0xffd7fffff7eefff3ull, 0xb7efff7ffffeff72ull },
{ 0x3effffff6ffe7f67ull, 0xfffbffbffeedfdc2ull },
{ 0xffff7ff7ffefdbf5ull, 0xf67ffbbffffffa59ull },
{ 0x7f7bffffffebff79ull, 0xffbf7feffdffd77full },
{ 0xfff77ffb7ff77f35ull, 0xdfefffefffd73fdaull },
{ 0xfffffffff7f777d9ull, 0xfff7fff7fdffbfdeull },
{ 0xffffffff7ed7fe99ull, 0xffffbffffefebf3full },
{ 0xfdffffff3ffffdccull, 0xffffefffff5bff70ull },
{ 0xfbefffdfffffbfafull, 0x7ffef7ffff7fff97ull },
{ 0xfffffffd7bfedfa2ull, 0x7f7fdbfffffbebe8ull },
{ 0xff3ffffff77fffcfull, 0xfb7ff7fdffffffc8ull },
{ 0xffffffffdfefbfb9ull, 0xffb5ffffdfffffe7ull },
{ 0xff7ff7fffefdbfbbull, 0xff7f7dfbff7fffe3ull },
{ 0xff7cfefffffff370ull, 0xf7fd7ffefff7fff8ull },
{ 0x7fdfffffecf67ef6ull, 0xffff7ffffbffffd2ull },
{ 0xdfffdffff97fbfe3ull, 0xf3ff7feffffffefaull },
{ 0xef7ffffbdef7f8fcull, 0xf5fefffdffffffe9ull },
{ 0xdf7fffffbefffdb3ull, 0xffeffffbff7efffeull },
{ 0xf77fffffefff6ff2ull, 0xffff7f7efd7fdfe0ull },
{ 0xffff7fffeff7f5c6ull, 0xbdf7d7f7fffffff9ull },
{ 0xfffffffdf7fb77edull, 0xffdbfbfbffffffe6ull },
{ 0xff7fffff7fe7ef4dull, 0xfff7f7fff77ffbffull },
{ 0xfffffffdfffffff3ull, 0xff7f77fbffffff47ull },
{ 0x77fff7bffffdff38ull, 0xf7fdff7ffffff3c4ull },
{ 0xfffffffffef75f92ull, 0x77ffffefffffefb9ull },
{ 0xf9ffffffff7ff97bull, 0xfdffffefffffffdbull },
{ 0xbfbfffffdfdffffcull, 0x777b7fdff7ff9730ull },
{ 0xffffffffdfeffef7ull, 0xfefff7fffefffeeeull },
{ 0xffffdffffffeffe7ull, 0xf7fd5efff7ffff7dull },
{ 0x3ffbbff7fff6fff8ull, 0xf73ffff7efffdffaull },
{ 0xffffffffdcfffdfdull, 0xffeffef7dffffee9ull },
{ 0xff77ffff7ffdff30ull, 0xfbffffeffddffff6ull },
{ 0xd7febffffffffeb4ull, 0xbbf7ffbf6fdfffefull },
{ 0xffffffffffffdfdcull, 0xdfff7f7ff7fcff75ull },
{ 0x7fffffffffbf7fe8ull, 0xff7eb7fffefff7a3ull },
{ 0xffeffffffff7ff57ull, 0xfefffffbff7ffdebull }
};
unsigned int fastMagicNumbers_bit_count[100] = {
18, 16, 10, 10, 16, 16, 10, 10, 16, 17,
16, 15, 9,  9,  15, 15, 9,  9,  15, 16,
16, 15, 9,  9,  15, 16, 9,  9,  15, 16,
16, 16, 10, 10, 15, 16, 10, 10, 15, 16,
9,  8,  6,  6,  8,  9,  6,  6,  9,  9,
8,  9,  6,  6,  8,  9,  6,  6,  9,  8,
16, 15, 10, 10, 15, 15, 10, 10, 15, 17,
16, 15, 9,  9,  15, 15, 9,  9,  15, 16,
16, 15, 9,  9,  15, 15, 9,  9,  15, 16,
18, 16, 10, 10, 16, 17, 10, 10, 16, 17
};
const bool fastMagicNumbers_are_after_LUT = true;
unsigned int fastMagicNumbers_offsets[100] = {
0,			1039114,	663354,		526254,		1235685,	1301117,	664374,		665396,		1497698,	524104,
1563232,	2541173,	679755,		663363,		2638872,	2671540,	696578,		701086,		2769580,	1954416,
2019196,	2802347,	697087,		697583,		2573933,	2281124,	700130,		700639,		2996864,	1366649,
1432174,	1627738,	667442,		684820,		2411783,	1758783,	666420,		680535,		2444550,	2084724,
669461,		127514,		0,			0,			670716,		263058,		0,			0,			264846,		265230,
265882,		271350,		0,			0,			670460,		671062,		0,          0,			263555,		50,
1888882,	2510063,	668430,		542643,		2606688,	2704307,	534460,		538508,		2736820,	778568,
1693269,	2835111,	712328,		669945,		2867871,	2477316,	527272,		701564,		2898601,	1170150,
1104644,	2931353,	712838,		713348,		2964104,	3029631,	531335,		667443,		3062397,	2346659,
262003,		2215589,	679515,		530312,		2150131,	908044,		683798,		695619,		824310,		655172
};


std::string ull_to_hex(unsigned long long x) {
	char buffer[65];
	#pragma warning(suppress : 4996)
	sprintf(buffer, "%.16llx", x);
	return std::string(buffer);
}

std::string bitboard_to_string(Bitboard& b) {
	std::stringstream ss;
	ss << "{ 0x" << ull_to_hex(b.low) << "ull, 0x" << ull_to_hex(b.high) << "ull }";
	return ss.str();
}

void printMagicNumbersLiteral(std::ostream& out) {
	out << "Bitboard fastMagicNumbers[100] = {\n";

	for (int i = 0; i < 100; ++i) {
		out << bitboard_to_string(magic_bitboards[i].magic_number) << ((i != 99) ? "," : " ") << "\n";
	}

	out << "};\n";

	out << "unsigned int fastMagicNumbers_bit_count[100] = {\n";
	for (int i = 0; i < 100; ++i) {
		out << magic_bitboards[i].bits;
		out << ((i == 99) ? "\n" : ",\n");
	}
	out << "};\n";

	out << "const bool fastMagicNumbers_are_after_LUT = " << ((__after_LUT_optimization), "true", "false") << "\n";

	out << "unsigned int fastMagicNumbers_offsets[100] = {\n";
	for (int i = 0; i < 100; ++i) {
		if (__after_LUT_optimization)
			out << magic_bitboards[i].lookup_table - magic_lookup_tables;
		else
			out << 0;

		out << ((i == 99) ? "\n" : ",\n");
	}
	out << "}\n";
	// TODO: if LUT optimisation was ready, print offsets and 
}


int fast_magic_bitboard_init(){
	__dealoc_magic_lookup_tables();
	__init_scout_attack_masks();
	__init_relevant_sqaures_for_magic_scout_gen();

	int result = 1;

	for (int i = 0; i < 100; ++i) {
		__assign(&magic_bitboards[i].magic_number, fastMagicNumbers + i);
		magic_bitboards[i].bits = fastMagicNumbers_bit_count[i];
	}
		

	if (!fastMagicNumbers_are_after_LUT) {
		for (unsigned int i = 0; i < 100; ++i) {
			magic_bitboards[i].lookup_table = (Bitboard*)malloc((1ull << fastMagicNumbers_bit_count[i]) * sizeof(Bitboard));
			result &= __verify_magic_numbers(magic_bitboards + i, i);
		}
	}
	else {
		
		unsigned int furthest_LUT = 0;
		for (unsigned int i = 1; i < 100; ++i) {
			if (fastMagicNumbers_offsets[i] > fastMagicNumbers_offsets[furthest_LUT])
				furthest_LUT = i;
		}
		unsigned int magic_lookup_table_sizes = fastMagicNumbers_offsets[furthest_LUT] + (1ull << fastMagicNumbers_bit_count[furthest_LUT]);
		magic_lookup_tables = new Bitboard[magic_lookup_table_sizes]; 

		for (unsigned int i = 0; i < 100; ++i) {
			magic_bitboards[i].lookup_table = magic_lookup_tables + fastMagicNumbers_offsets[i];
			result &= __verify_magic_numbers(magic_bitboards + i, i);
		}
		__after_LUT_optimization = true;
	}

	if (result) {
		__post_magic_init = true;
		__clear_magic_not_garbage_flag();
	}
	

	return result;
}

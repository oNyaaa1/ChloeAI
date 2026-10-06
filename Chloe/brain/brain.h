#pragma once
#include <iostream>
int brain = 0;

namespace chloe {
	void setBrain(bool brains) {
		brain = brains;
	};

	bool brainFunction() {
		if (brain == 1) {
			return true;
		}
		return false; // Default return value for other cases
	};

	bool brainCompute() {
		if (brain == 1) {
			printf("Brain is computing...\n");	
			std::cout << "Enter two numbers: ";

			int x{};
			std::cin >> x;

			int y{};
			std::cin >> y;

			int awnser = x + y;

			std::cout << "Awnser: " << awnser << '\n';
			return true;
		}
		return false; // Default return value for other cases
	};

}


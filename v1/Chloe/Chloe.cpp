#define CURL_STATICLIB

#include <iostream>
#include <string>
#include "brain/brain.h" // Include the brain header file#
#include <iostream>
#include <thread>
#include <chrono>

using namespace std;
using namespace chloe;

// Define the LLMService class
class LLMService {
public:
    virtual std::string generate(const std::string& prompt) = 0;
    virtual ~LLMService() = default;
};

LLMService* createLLMService() {
	// Return an instance of a concrete implementation of LLMService
	// For demonstration purposes, we can return a dummy implementation
	class DummyLLMService : public LLMService {
	public:
		std::string generate(const std::string& prompt) override {
			return "Chloe says: " + prompt;
		}
	};
	return new DummyLLMService();
}

int main() {
	LLMService* llmservers = createLLMService();
    std::string response = llmservers->generate("Loaded?");
	cout << "LLM Response: " << response << std::endl;
    delete llmservers;
	chloe::setBrain(1); // Set the brain variable to 1
    bool result = chloe::brainFunction(); // Call the brain function from the chloe namespace
    if (result == true) {
        std::cout << "Brain function returned true." << std::endl;
	}
	else {
		std::cout << "Brain function returned false." << std::endl;
    }
    std::cout << "Brain function executed." << std::endl;

	while (true) {
		chloe::brainCompute();
		std::this_thread::sleep_for(std::chrono::seconds(3));
	}
    return 0;
}
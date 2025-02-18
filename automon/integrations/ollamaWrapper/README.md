# ollamaWrapper

![](https://www.librechat.ai/images/blog/2024-03-02_ollama.png)

For official documentation: https://github.com/ollama/ollama-python

### Requirements

- Must have ollama installed
- Must have ollama running

### How to use this library

Refer to the [tests folder](automon/integrations/ollamaWrapper/tests/) for
examples.

### Run test from shell

```bash
RUN=1 python3 test_rag.py
```

### Example

```bash
% RUN=1 python3 test_rag.py

DEBUG   [client.py:109] is_ready        [OllamaClient] :: is_ready :: >>>>
DEBUG   [client.py:122] list    [OllamaClient] :: list :: >>>>
DEBUG   [client.py:129] list    [OllamaClient] :: list :: model=Model(model='deepseek-r1:14b', modified_at=datetime.datetime(2025, 2, 18, 3, 45, 7, 831500, tzinfo=TzInfo(-06:00)), digest='ea35dfe18182f635ee2b214ea30b7520fe1ada68da018f8b395b444b662d4f1a', size=8988112040, details=ModelDetails(parent_model='', format='gguf', family='qwen2', families=['qwen2'], parameter_size='14.8B', quantization_level='Q4_K_M'))
DEBUG   [client.py:133] list    [OllamaClient] :: list :: 1 model(s)
INFO    [client.py:134] list    [OllamaClient] :: list :: done
INFO    [client.py:113] is_ready        [OllamaClient] :: is_ready :: done

Enter your question: how do you make a python selenium code move the mouse in a human and natural way?

DEBUG   [client.py:52]  add_message     [OllamaClient] :: add_message :: role='user' :: 31 tokens >>>>
DEBUG   [client.py:64]  add_message     [OllamaClient] :: add_message :: 31 total tokens
INFO    [client.py:69]  add_message     [OllamaClient] :: add_message :: done
DEBUG   [client.py:51]  add_message     [OllamaClient] :: add_message :: role='user' :: 67 tokens >>>>
DEBUG   [client.py:64]  add_message     [OllamaClient] :: add_message :: 98 total tokens
INFO    [client.py:69]  add_message     [OllamaClient] :: add_message :: done
DEBUG   [client.py:51]  add_message     [OllamaClient] :: add_message :: role='user' :: 112 tokens >>>>
DEBUG   [client.py:64]  add_message     [OllamaClient] :: add_message :: 210 total tokens
INFO    [client.py:69]  add_message     [OllamaClient] :: add_message :: done
DEBUG   [client.py:51]  add_message     [OllamaClient] :: add_message :: role='user' :: 47 tokens >>>>
DEBUG   [client.py:64]  add_message     [OllamaClient] :: add_message :: 257 total tokens
INFO    [client.py:69]  add_message     [OllamaClient] :: add_message :: done
DEBUG   [client.py:51]  add_message     [OllamaClient] :: add_message :: role='user' :: 69 tokens >>>>
DEBUG   [client.py:64]  add_message     [OllamaClient] :: add_message :: 326 total tokens
INFO    [client.py:69]  add_message     [OllamaClient] :: add_message :: done
DEBUG   [client.py:51]  add_message     [OllamaClient] :: add_message :: role='user' :: 46 tokens >>>>
DEBUG   [client.py:64]  add_message     [OllamaClient] :: add_message :: 372 total tokens
INFO    [client.py:69]  add_message     [OllamaClient] :: add_message :: done
DEBUG   [client.py:74]  chat    [OllamaClient] :: chat :: 372 tokens >>>>
DEBUG   [client.py:90]  chat    [OllamaClient] :: chat :: response=[OllamaResponse]
INFO    [client.py:91]  chat    [OllamaClient] :: chat :: done
DEBUG   [client.py:147] print_response  [OllamaClient] :: print_response :: >>>>

<think>
Okay, I want to figure out how to make my Python Selenium code move the mouse in a more natural way. Right now, when I automate actions on a website, the cursor moves too quickly or in straight lines, which might look suspicious or get blocked by some anti-bot systems.

Hmm, I remember that Selenium has some methods for moving the mouse, like `move_to_element` and `move_by_offset`. Maybe those can be used to create smoother movements. But how do I make it feel more human?

One idea is to introduce delays between mouse movements. If I make the code wait a bit after each move, it would mimic a real person's reaction time. Also, maybe moving the mouse in small steps instead of one big jump could help. Like, instead of jumping directly from point A to B, simulate several tiny moves.

Another thought: sometimes humans don't always click exactly on the target; they might hover near it or move around a bit before clicking. So adding some randomness to the movement range could make the actions look more natural.

I've heard about using `ActionChains` in Selenium for complex interactions. Maybe chaining several mouse movements and introducing pauses between them would help create that realistic feel. For example, moving the mouse a little, waiting, then moving again towards the target.

Wait, I should check how to implement these ideas. Let me think of steps:

1. Use `ActionChains` for more granular control over each movement.
2. Break down the target location into smaller segments so that each move is just a small step.
3. Add random pauses between each movement to simulate human reaction times and hesitations.
4. Introduce some randomness in the exact position to mimic how people might not always hit the exact center of a button.

Maybe I can write a function that takes a target element or coordinates, splits the journey into steps, adds waits, and varies the path slightly. That way, each execution would look different, reducing any repetitive patterns that could be flagged by anti-bot measures.

I should also test these changes to ensure they don't slow down the script too much or cause errors. Balancing realism with efficiency is key here.
</think>

To make your Python Selenium code move the mouse in a more natural and human-like way, you can simulate mouse movements with delays and small steps using `ActionChains`. Here's an example:
```

```python
from selenium import webdriver
from selenium.webdriver import ActionChains
import random
import time

# Initialize the WebDriver (e.g., Chrome)
driver = webdriver.Chrome()


# Move the mouse in a natural way to an element
def move_mouse_naturally(driver, target_element):
    # Get the coordinates of the target element
    location = target_element.location
    x = location['x']
    y = location['y']

    # Create ActionChains object
    action = ActionChains(driver)

    # Split the movement into small steps
    steps = 10  # Number of steps to simulate natural movement
    for i in range(steps):
        # Calculate intermediate positions
        current_x = x * (i + 1) / steps
        current_y = y * (i + 1) / steps

        # Move the mouse by small increments and add a slight delay
        action.move_to_location(current_x, current_y)
        time.sleep(random.uniform(0.1, 0.3))  # Random delay between each step

    # Execute all actions
    action.perform()
```

```bash
# Use this function when you need to move the mouse naturally
move_mouse_naturally(driver, your_target_element)

### Key Points:
- **ActionChains**: Allows for more precise and controlled movements.
- **Random Delays**: Introduce slight delays between movements to mimic human hesitation.
- **Small Steps**: Break down the movement into multiple small steps for a smoother transition.

### Ratings:
1. **Realism**: 9/10 - The mouse moves in smaller increments with random delays, making it look more natural.
2. **Efficiency**: 8/10 - May slow down execution due to the added steps and delays, but necessary for realism.
3. **Customization**: 9/10 - Easily adjustable parameters (steps, delay range) for different scenarios.

This approach should make your Selenium scripts appear more like a real user interacting with the page.

INFO    [client.py:154] print_response  [OllamaClient] :: print_response :: done
.
----------------------------------------------------------------------
Ran 1 test in 2356.314s

OK
```

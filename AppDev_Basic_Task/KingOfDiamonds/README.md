# King of Diamonds

## Objective

The objective of this task was to create a simple browser-based implementation of the **King of Diamonds** game using basic web technologies.

I did not have any previous experience working with the web stack before this task. The project was completed by learning the minimum concepts required to build an interactive webpage using HTML, CSS and JavaScript.

---

## Game Rules

1. The user enters a whole number between **0 and 100**.
2. The computer generates its own random number between **0 and 100**.
3. The average of both numbers is calculated.

```
Average = (User Number + Bot Number) / 2
```

4. A target value is then computed as:

```
Target = Average × 0.8
```

5. The distance of both the user and the bot from the target is calculated.

6. Whoever is closer to the target wins the round.

7. If both distances are equal, the result is declared a tie.

---

## Technologies Used

### HTML

HTML was used to create the structure of the webpage.

The page contains:

* A heading displaying the game title.
* A numeric input field for the user.
* A button to start a round.
* A section to display the results.

---

### CSS

CSS was used to improve the appearance of the page.

Some styling choices include:

* Center-aligned content.
* A light background colour.
* Styled buttons.
* Rounded result containers.
* Basic spacing and readability improvements.

The styling was kept simple since the primary focus of the task was implementing the game logic.

---

### JavaScript

JavaScript was used to implement the behaviour of the game.

The program performs the following steps:

* Reads the user's input.
* Validates the entered value.
* Generates a random number for the bot.
* Calculates the average and target values.
* Computes each participant's distance from the target.
* Determines the winner.
* Displays all results dynamically on the webpage.

---

## Input Validation

Basic validation checks were implemented to improve usability.

The program checks whether:

* The input field is empty.
* The entered number lies between 0 and 100.
* The input is a whole number.

Appropriate messages are displayed when invalid input is provided.

---

## Example Flow

Suppose the user enters:

```
User Number = 50
```

The bot generates:

```
Bot Number = 70
```

Then:

```
Average = (50 + 70) / 2 = 60
Target = 60 × 0.8 = 48
```

Distances:

```
User Distance = |50 − 48| = 2
Bot Distance  = |70 − 48| = 22
```

Result:

```
Winner: User
```

---

## Challenges Faced

Since I had very little exposure to web development before this task, understanding how HTML, CSS and JavaScript interact with each other was initially confusing.

Some of the concepts I had to learn while building this project included:

* Accessing HTML elements from JavaScript.
* Responding to button clicks using event listeners.
* Updating webpage content dynamically.
* Validating user input before processing it.

Although the implementation itself is relatively simple, this project served as an introduction to client-side web development.

---

## Limitations

* The game supports only a single round at a time.
* No score tracking is implemented.
* The bot uses purely random choices and has no strategy.
* The application stores no game history.
* The interface focuses on functionality rather than advanced design.

---

## Conclusion

This task helped me gain an initial understanding of how basic web applications are structured and how interactivity can be added using JavaScript. While I do not have extensive experience with the web stack, completing this project allowed me to become familiar with the fundamentals required to build a small browser-based application.

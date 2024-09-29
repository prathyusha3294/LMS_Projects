document.addEventListener('DOMContentLoaded', function () {
    const quizContainer = document.getElementById('quiz-container');
    const quizTitle = document.getElementById('quiz-title');
    const quizForm = document.getElementById('quiz-form');
    const submitQuizButton = document.getElementById('submit-quiz');

    // Get all the 'Take Quiz' buttons
    const takeQuizButtons = document.querySelectorAll('.take-quiz-btn');

    takeQuizButtons.forEach(button => {
        button.addEventListener('click', function () {
            const courseId = button.getAttribute('data-course-id');  // Get course ID
            const courseTitle = button.getAttribute('data-course-title');  // Get course title

            // Set the quiz title
            quizTitle.innerText = `Take Quiz: ${courseTitle}`;
            quizContainer.style.display = 'block';  // Show the quiz container

            // Clear any previous quiz questions
            quizForm.innerHTML = '';

            // Use fetch API to retrieve quiz questions based on the course
            fetch(`/api/getquiz/${courseId}/`)
                .then(response => {
                    // Check if the response is OK (status code 200)
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const questions = data.questions; // Get the questions object
                    if (questions && questions.length > 0) {
                        // Loop through each question and create form elements
                        questions.forEach((question, index) => {
                            const questionElement = document.createElement('p');
                            questionElement.innerText = `${index + 1}. ${question.text}`;
                            quizForm.appendChild(questionElement);

                            // Create radio buttons for each option
                            question.options.forEach(option => {
                                const optionLabel = document.createElement('label');
                                const optionInput = document.createElement('input');
                                optionInput.type = 'radio';
                                optionInput.name = `question_${question.id}`;
                                optionInput.value = option;
                                
                                optionLabel.appendChild(optionInput);
                                optionLabel.appendChild(document.createTextNode(option));
                                quizForm.appendChild(optionLabel);
                                quizForm.appendChild(document.createElement('br'));
                            });
                        });

                        submitQuizButton.style.display = 'block';  // Show the submit button
                    } else {
                        quizForm.innerHTML = `<p>No quiz questions available for ${courseTitle}.</p>`;
                        submitQuizButton.style.display = 'none';  // Hide the submit button if no questions
                    }
                })
                .catch(error => {
                    console.error('Error fetching quiz:', error);
                    quizForm.innerHTML = `<p>There was an error loading the quiz: ${error.message}. Please try again later.</p>`;
                });
        });
    });
});

// // Sample static quiz data
// const quizData = {
//     id: 1,
//     title: "Sample Quiz",
//     questions: [
//         {
//             id: 1,
//             text: "What is the capital of France?",
//             options: ["Berlin", "Madrid", "Paris", "Rome"]
//         },
//         {
//             id: 2,
//             text: "What is the largest ocean on Earth?",
//             options: ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"]
//         },
//         {
//             id: 3,
//             text: "Which planet is known as the Red Planet?",
//             options: ["Earth", "Mars", "Jupiter", "Saturn"]
//         }
//     ]
// };

// // Function to display the quiz questions on the page
// function displayQuiz(quizData) {
//     const quizContainer = document.getElementById('quiz-container'); // Assume you have a container in your HTML

//     quizContainer.innerHTML = ''; // Clear previous content

//     // Create HTML for the quiz title
//     const titleElement = document.createElement('h2');
//     titleElement.innerText = quizData.title;
//     quizContainer.appendChild(titleElement);

//     // Create HTML for each question
//     quizData.questions.forEach(question => {
//         const questionElement = document.createElement('div');
//         questionElement.innerHTML = `
//             <h3>${question.text}</h3>
//             ${question.options.map(option => `
//                 <label>
//                     <input type="radio" name="question_${question.id}" value="${option}"> ${option}
//                 </label>
//             `).join('')}
//         `;
//         quizContainer.appendChild(questionElement);
//     });

//     // Add submit button
//     const submitButton = document.createElement('button');
//     submitButton.innerText = 'Submit Quiz';
//     submitButton.onclick = () => submitQuiz(quizData.id);
//     quizContainer.appendChild(submitButton);
// }

// // Function to collect answers and submit the quiz
// function submitQuiz(quizId) {
//     const answers = {};
//     const quizContainer = document.getElementById('quiz-container');

//     // Collect answers from the quiz container
//     quizContainer.querySelectorAll('input[type="radio"]:checked').forEach(input => {
//         const questionId = input.name.split('_')[1]; // Extract question ID from name
//         answers[questionId] = input.value; // Store the answer
//     });

//     const answersJson = JSON.stringify({
//         quiz_id: quizId,
//         answers: answers
//     });

//     // Send the POST request using fetch
//     fetch(`/api/quizsubmit/`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCSRFToken()  // Ensure you have the CSRF token
//         },
//         body: answersJson
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log('Success:', data);
//         alert(`Quiz submitted successfully! Your score: ${data.score}/${data.total_marks}`);
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// }

// // Helper function to get the CSRF token if you're using Django's CSRF protection
// function getCSRFToken() {
//     const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
//     return csrfToken ? csrfToken.value : '';
// }

// // Example usage
// displayQuiz(quizData);  // Display the quiz with static data

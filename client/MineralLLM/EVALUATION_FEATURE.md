# Answer Evaluation Feature

## Overview
The Answer Evaluation feature allows users to evaluate the quality of LLM responses to questions. Users can rate answers on multiple criteria and provide qualitative feedback.

## Features Implemented

### 1. **Conversation Selection**
- View all conversations in a searchable dropdown
- Conversations displayed with ID and creation timestamp
- Select a conversation to load its questions
- Can switch between conversations easily

### 2. **View Questions**
- Displays all questions for the selected conversation
- Expandable accordion format for easy navigation
- Shows question details, answers, and timestamps
- Indicates which questions already have evaluations with color-coded badges

### 3. **Create Evaluation**
Users can evaluate answers based on:
- **If Answer Provided**: Yes/No (binary 0 or 1)
- **Technical Accuracy**: Rating 1-5 (Likert scale)
- **Practical Utility**: Rating 1-5 (Likert scale)
- **Trustworthiness**: Rating 1-5 (Likert scale)
- **Comprehension Depth**: Rating 1-5 (Likert scale)
- **Issues Found**: Text field for describing problems
- **Suggestions for Improvement**: Text field for recommendations

### 4. **Edit Evaluation**
- Click the edit icon (pencil) to modify existing evaluations
- All fields can be updated
- Uses PATCH endpoint to update data

### 5. **Delete Evaluation**
- Click the trash icon to remove an evaluation
- Confirmation through the API

### 6. **Visual Indicators**
- Star ratings displayed for all metrics (1-5 scale)
- Color-coded badges for evaluation status
- Responsive accordion interface for easy navigation

## Navigation

The Answer Evaluation page can be accessed by clicking the **Clipboard icon** in the left navigation bar.

## API Endpoints Used

- `POST /v1/evaluation/answer_evaluation` - Create new evaluation
- `GET /v1/evaluation/answer_evaluations` - Get all evaluations
- `GET /v1/evaluation/answer_evaluation/question/{question_id}` - Get evaluation by question
- `PATCH /v1/evaluation/answer_evaluation/{evaluation_id}` - Update evaluation
- `DELETE /v1/evaluation/answer_evaluation/{evaluation_id}` - Delete evaluation

## Components Created

1. **AnswerEvaluation.jsx** - Main component with all functionality
2. **AnswerEvaluation.module.css** - Styling for the component
3. **api.js** - Added evaluation API methods

## Database Constraints

- Each question can only have ONE evaluation (enforced by UNIQUE constraint on `evaluate_queryquestion_id`)
- Attempting to create duplicate evaluations will show a helpful error message
- Foreign key constraint ensures evaluations are linked to valid questions

## Usage Flow

1. Navigate to Answer Evaluation page
2. Select a conversation from the dropdown menu (conversations are listed by ID and creation date)
3. View all questions from that conversation
4. Expand a question to see its answer and evaluation status
5. For unevaluated questions, click "Create Evaluation"
6. Fill in the evaluation form with ratings and comments
7. Click "Save" to submit
8. Edit or delete evaluations as needed using the action icons
9. Switch to a different conversation to evaluate other questions

## Technical Details

- Uses Mantine UI components for consistent design
- Implements proper error handling and user notifications
- **Efficient loading**: Only loads questions for the selected conversation (not all at once)
- Searchable conversation dropdown for easy navigation
- Real-time updates after create/edit/delete operations
- Responsive design for all screen sizes
- Separate loading states for conversations and questions
- Clear button to deselect conversation


# Draftly Demo Video Script

**Goal**: Create a 5-10 minute video demonstrating the core features of Draftly.

## Preparation
1.  Ensure Backend is running (`uvicorn app.main:app --reload`).
2.  Ensure Frontend is running (`npm run dev`).
3.  Open your browser to `http://localhost:5173`.
4.  Have a screen recording tool ready (e.g., OBS, Loom, QuickTime).

## Scene 1: Introduction & Registration (1 minute)
*   **Action**: Start on the Login page.
*   **Narrate**: "Hi, this is a demo of Draftly, an AI-assisted document authoring platform. I'll start by registering a new user."
*   **Action**: Click "Register", fill in details, and submit.
*   **Action**: Log in with the new credentials.
*   **Narrate**: "Now I'm logged into the main dashboard."

## Scene 2: Creating a Word Document Project (2 minutes)
*   **Action**: Click "Create Project".
*   **Action**: Enter Title: "Q3 Marketing Strategy".
*   **Action**: Select Type: "Word Document (.docx)".
*   **Action**: Enter Prompt: "Create a marketing strategy for a new eco-friendly coffee brand targeting millennials."
*   **Action**: Click "Create".
*   **Narrate**: "I'm creating a new project for a marketing strategy. The AI will use this prompt to generate content."

## Scene 3: Content Generation (2 minutes)
*   **Action**: On the Project Details page, locate the "Generate outline & sections" panel.
*   **Action**: Click "Generate".
*   **Narrate**: "I'm now triggering the AI to generate the initial outline and section content. This uses the integrated LLM (Ollama/Gemini)."
*   **Wait**: Wait for generation to complete.
*   **Action**: Show the generated sections in the list.
*   **Narrate**: "The AI has generated several sections based on my prompt."

## Scene 4: Refinement & Editing (2 minutes)
*   **Action**: Click on a section (e.g., "Target Audience").
*   **Action**: Show the content in the editor.
*   **Action**: In the "Refinement instruction" box, type: "Expand on the demographics and include psychographics."
*   **Action**: Click "Refine".
*   **Narrate**: "I can refine specific sections. Here, I'm asking the AI to expand on the target audience details."
*   **Action**: Show the updated content.
*   **Action**: Manually edit a sentence to show manual control. Click "Save".

## Scene 5: Exporting (1 minute)
*   **Action**: Click "Export DOCX".
*   **Action**: Open the downloaded file in Word.
*   **Narrate**: "Finally, I can export the project to a formatted Word document."
*   **Action**: Scroll through the Word doc to show the result.

## Scene 6: PowerPoint Workflow (Optional/Quick)
*   **Action**: Go back to Dashboard. Create a new project.
*   **Action**: Select Type: "PowerPoint (.pptx)".
*   **Action**: Generate content.
*   **Action**: Click "Export PPTX".
*   **Action**: Open the PowerPoint file.
*   **Narrate**: "The platform also supports generating and exporting PowerPoint presentations."

## Conclusion
*   **Narrate**: "That concludes the demo of Draftly. Thank you."

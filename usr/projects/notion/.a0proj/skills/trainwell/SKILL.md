---
name: trainwell
description: "Retrieve exercise details, metadata fields (Name, Area, Place, Tool, Difficulty, Contraction Type, Target Muscles), direct video URLs (from S3/copilot-exercise-media or page video tags), and instructions from Trainwell for any given workout movement, with best-effort web search fallback for basic demos/images."
---
# Trainwell Exercise Retriever

## Objective

Retrieve exercise information, structured metadata attributes, video URLs, and instructions from Trainwell (or fallback web search) based on a user's exercise query.

## Instructions & Workflow

1.  **Construct the Target URL:**
    
      - Take the user's exercise query (e.g., "Pull Up", "Med Ball Halo", "Spiderman Push Up") and format it into a URL slug by converting it to lowercase, using singular phrasing where applicable (e.g., "Pull Ups" -> `pull-up`, "Med Ball Halos" -> `med-ball-halo`), and replacing spaces with hyphens.
      - The standard exercise page URL structure on Trainwell is: `https://www.trainwell.net/exercises/{exercise-slug}`
      - *Example:* For "Med Ball Halo", the target URL is `https://www.trainwell.net/exercises/med-ball-halo`.

2.  **Browse the Webpage & Fallback:**
    
      - Fetch the content of the constructed URL.
      - Extract direct video source files (`.mp4`) typically embedded via `<source src="https://copilot-exercise-media.s3.us-east-2.amazonaws.com/.../...mp4">` or `<video>` tags.
      - If the exact exercise URL returns a 404, redirects, or cannot be found, search Trainwell exercises (e.g., via web search `site:trainwell.net/exercises <exercise name>` or browsing `https://www.trainwell.net/exercises`) to locate the correct page.
      - **Fallback Rule**: If the exercise is not present on Trainwell, perform a best-effort web search across reliable fitness sources.

3.  **Extract & Map Required Fields:** Extract and map the exercise overview, category, instructions, equipment, muscles used, and cues to the standard schema:
    
      - **Name:** The official name of the exercise (e.g., Med Ball Halo, Pull Up).
      - **Area:** The body area or anatomical region (e.g., Upper Body, Lower Body, Core, Feet).
      - **Place:** The venue or environment (e.g., Gym, Home, Outdoors).
      - **Tool:** The equipment or tool used (e.g., Medicine Ball, Pull-Up Bar, Bodyweight, Dumbbell).
      - **Difficulty:** Experience level (e.g., Beginner, Intermediate, Advanced).
      - **Contraction Type:** Muscular contraction (e.g., Dynamic, Isometric, Eccentric).
      - **Target Muscles:** Specific muscles targeted (e.g., Deltoids, Rotator Cuff, Trapezius, Obliques, Core, Glutes, Hamstrings).
      - **Video URLs:** Direct video URLs (such as `https://copilot-exercise-media.s3.us-east-2.amazonaws.com/.../*.mp4` or embedded video links).
      - **URL:** The direct link to the Trainwell exercise source page (`https://www.trainwell.net/exercises/{exercise-slug}`).
      - **Instructions / Steps:** Step-by-step execution details, cues, overview, and form tips.

4.  **Format the Output:** Present the exercise details in a clean, structured format matching the standard schema:
    
      - **Name:** [Exercise Name]
      - **Area:** [Area]
      - **Place:** [Place]
      - **Tool:** [Tool/Equipment]
      - **Difficulty:** [Difficulty Level]
      - **Contraction Type:** [Contraction Type]
      - **Target Muscles:** [Target Muscles]
      - **URL:** [Exercise Page URL]
      - **Video URLs:** [List of extracted video links]
      - **Instructions:** [Step-by-step instructions and notes]
---
name: musclewiki
description: "Retrieve exercise details, metadata fields (Name, Area, Place, Tool, Difficulty, Contraction Type, Target Muscles), direct CDN video URLs (.mp4 looping clips), and instructions from MuscleWiki for any given workout movement, with best-effort web search fallback for basic demos/images."
---
# MuscleWiki Exercise Retriever

## Objective

Retrieve exercise information, structured metadata attributes, direct looping `.mp4` video URLs from MuscleWiki CDN, and instructions from MuscleWiki (or fallback web search) based on a user's exercise query.

-----

## Instructions & Workflow

1.  **Construct the Target URL:**
    
      - Take the user's exercise query (e.g., "Pull Ups", "Single Legged Romanian Deadlifts") and format it into a URL slug by converting it to lowercase and replacing spaces with hyphens (e.g., `pull-ups`, `single-legged-romanian-deadlifts`).
      - The standard exercise page URL structure is: `https://musclewiki.com/exercise/{exercise-slug}`
      - *Example:* For "Pull Ups", the URL is `https://musclewiki.com/exercise/pull-ups`.

2.  **Direct CDN Video Resolution**:
    
      - **Do not rely on web scrapers to detect video tags**, as dynamic scrapers often encounter placeholder text (`Your browser can't play this video`).
      - Always construct the direct `.mp4` video URLs hosted on MuscleWiki's CDN:
        `https://media.musclewiki.com/media/uploads/videos/branded/{gender}-{Tool}-{slug}-{angle}.mp4`
      - **Tool Casing & Conventions**:
          - `Bodyweight` (e.g., `male-Bodyweight-single-legged-romanian-deadlifts-front.mp4`)
          - `Dumbbells` (e.g., `male-Dumbbells-single-leg-stiff-leg-deadlift-side.mp4`)
          - `Barbell` (e.g., `male-Barbell-single-leg-deadlift-front.mp4`)
          - `Kettlebells` (e.g., `male-Kettlebells-single-leg-deadlift-side.mp4`)
          - `Cables`
          - `Bands`
          - `Medicine-Ball`
      - **Angles**: `front`, `side`
      - **Genders**: `male`, `female`

3.  **Browse the Webpage & Fallback:**
    
      - Fetch the content of the constructed URL.
      - If the exact exercise URL returns a 404 or cannot be found, search MuscleWiki to locate the exercise.
      - **Fallback Rule**: If the exercise is not present on MuscleWiki, perform a best-effort web search across reliable fitness sources to retrieve standard metadata fields. For demonstration media, search for **basic demonstration videos only** (short-form looping clips / silent demos), strictly avoiding extensive coaching or talking-head videos.

4.  **Extract Required Fields:** Extract and populate all of the following required fields:
    
      - **Name:** The official name of the exercise.
      - **Area:** The body area / anatomical region (e.g., Upper Body, Lower Body, Core, Feet).
      - **Place:** The environment / venue where the exercise is typically performed (e.g., Gym, Home, Outdoors, Climbing Gym).
      - **Tool:** The equipment or tool used (e.g., Barbell, Dumbbells, Bodyweight, Cable, Kettlebells, Machine, Resistance Bands, Pull-up Bar).
      - **Difficulty:** The experience or skill level (e.g., Beginner, Intermediate, Advanced).
      - **Contraction Type:** The type of muscular contraction (e.g., Isotonic, Isometric, Concentric, Eccentric, Dynamic).
      - **Target Muscles:** The specific muscles or muscle groups targeted (e.g., Latissimus Dorsi, Biceps Brachii, Pectoralis Major, Quadriceps, Glutes, Hamstrings).
      - **Video URLs:** Direct `.mp4` video CDN source URLs (Male/Female Front & Side angles).
      - **URL:** The direct link to the exercise source page.
      - **Instructions / Steps:** Step-by-step execution details and exercise cues.

5.  **Format the Output:** Present the exercise details in a clean, structured format adhering to the required fields:
    
      - **Name:** [Exercise Name]
      - **Area:** [Area]
      - **Place:** [Place]
      - **Tool:** [Tool/Equipment]
      - **Difficulty:** [Difficulty Level]
      - **Contraction Type:** [Contraction Type]
      - **Target Muscles:** [Target Muscles]
      - **URL:** [Exercise Page URL]
      - **Video URLs:** [List of extracted direct .mp4 CDN video links]
      - **Instructions:** [Step-by-step instructions and notes]

-----

## Edge Cases & Guidelines

  - **Short Demos Only**: Prioritize short looping demonstrations (front/side angles) and exclude long coaching tutorials.
  - Include both male and female, front and side angle direct `.mp4` URLs whenever available.
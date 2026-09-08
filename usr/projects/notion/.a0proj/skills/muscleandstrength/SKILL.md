---
name: muscleandstrength
description: "Retrieve exercise details, metadata fields (Name, Area, Place, Tool, Difficulty, Contraction Type, Target Muscles), video URLs, and instructions from Muscle & Strength for any given workout movement, with best-effort web search fallback for basic demos/images."
---
# Muscle & Strength Exercise Retriever

## Objective

Retrieve exercise information, structured metadata attributes, video URLs, and instructions from Muscle & Strength (or fallback web search) based on a user's exercise query.

## Instructions & Workflow

1.  **Construct the Target URL:**
    
      - Take the user's exercise query (e.g., \"Pull Ups\", \"Barbell Bench Press\") and format it into a URL slug by converting it to lowercase, using singular phrasing where applicable (e.g., \"Pull Ups\" -> `pull-up`), and replacing spaces with hyphens (e.g., `pull-up`, `bench-press`, `dumbbell-deadlift`).
      - The standard exercise page URL structure on Muscle & Strength is: `https://www.muscleandstrength.com/exercises/{exercise-slug}`
      - *Example:* For \"Pull Ups\", the target URL is `https://www.muscleandstrength.com/exercises/pull-up`.

2.  **Browse the Webpage & Fallback:**
    
      - Fetch the content of the constructed URL.
      - If the exact exercise URL returns a 404, redirects, or cannot be found, search Muscle & Strength exercises (e.g., via web search `site:muscleandstrength.com/exercises <exercise name>`) to locate the correct page.
      - **Fallback Rule**: If the exercise is not present on Muscle & Strength, perform a best-effort web search across reliable fitness sources to retrieve the standard metadata fields. For demonstration media, search for **basic demonstration videos only** (short-form looping clips or silent demos) or images, strictly avoiding long coaching or talking-head tutorials.

3.  **Extract & Map Required Fields:** Extract and map the exercise profile, overview, instructions, and tips to the standard schema:
    
      - **Name:** The official name of the exercise (e.g., Pull Up, Barbell Bench Press).
      - **Area:** The body area or anatomical region (e.g., Upper Body, Lower Body, Core, Feet), derived from Target Muscle Group and Secondary Muscles.
      - **Place:** The venue or environment where the exercise is performed (e.g., Gym, Home, Outdoors), inferred from equipment requirements and exercise setup.
      - **Tool:** The equipment or tool used (e.g., Bodyweight, Barbell, Dumbbells, Cable, Machine, Kettlebells, Pull-up Bar), extracted from \"Equipment Required\".
      - **Difficulty:** The experience or skill level (e.g., Beginner, Intermediate, Advanced), extracted from \"Experience Level\".
      - **Contraction Type:** The type of muscular contraction or mechanical classification (e.g., Isotonic, Isometric, Dynamic, Compound, Isolation), derived from \"Mechanics\" and exercise style.
      - **Target Muscles:** The specific muscles targeted (e.g., Primary: Latissimus Dorsi; Secondary: Abs, Biceps, Shoulders, Upper Back, Glutes, Hamstrings), extracted from \"Target Muscle Group\" and \"Secondary Muscles\".
      - **Video URLs:** Direct video source URLs or embedded demonstration links (e.g., YouTube embeds or video guide links) on the page.
      - **URL:** The direct link to the Muscle & Strength exercise source page.
      - **Instructions / Steps:** Step-by-step execution details, cues, overview, and tips.

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
      - **Instructions:** [Step-by-step instructions, cues, and tips]

## Edge Cases & Guidelines

  - **Plural vs. Singular Slugs**: Muscle & Strength typically uses singular slugs for exercises (e.g., `pull-up`, `push-up`, `chin-up`, `lat-pulldown`). If a plural URL 404s, test the singular form before searching.
  - **Short Demos Only**: When retrieving video links, prioritize direct demonstration videos or short video guides over lengthy tutorials.
  - Maintain schema consistency with the existing exercise retriever format to allow seamless downstream integration.
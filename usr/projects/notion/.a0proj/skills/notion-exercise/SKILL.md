---
name: notion-exercise
description: "Create a new exercise page in the Notion Exercise Library database for any specified movement matching the Face Pull Ups reference structure. Enforces a strict source hierarchy for exercise metadata & synthesis: (1) MuscleWiki (highest precedence for metadata), (2) Muscle & Strength, (3) Trainwell, (4) other/web search fallback, or user-provided overrides. Uses reliable YouTube video embeds for demonstrations and coaching (strictly avoiding raw CDN .mp4 URLs which fail to play in Notion), synthesizes a ~400-character summary in the top reference callout box, sets Notion database properties, and creates the page via Notion CLI (notion-cli)."
---
# Create Exercise Page

A skill to automatically create and populate a new exercise entry in the Notion Exercise Library database, modeled directly after the **Face Pull Ups** reference page standard.

## When to Use

  - When the user asks to create, add, or generate a new exercise page in Notion.
  - When expanding the workout library with new movements (e.g., calisthenics, weightlifting, gymnastics, climbing conditioning).
  - When the user provides a custom exercise guide, workout notes, or specific URLs to turn into a Notion exercise page.
  - When the user asks to add an exercise to their physical activity planner or Exercise Library database.

## Notion CLI Integration Directives

  - **CLI Tool Execution**: Execute the `notion-cli` tool directly (provided by the `cli-anything` skill and installed system-wide on `PATH`):
    ```bash
    notion-cli [command] [options]
    ```
  - **Database Target**:
      - Exercise Library Database ID: `ba872d615db54338b586006e708e3fc7`
      - Exercise Library Database URL: `https://app.notion.com/p/ba872d615db54338b586006e708e3fc7`
  - **Authentication**: Ensure `NOTION_TOKEN` is set in `usr/.env` or passed via `--token`.
  - **No Automatic Icons/Emojis**: **DO NOT** add icons, emojis, or covers automatically to pages. Leave `icon` omitted or set to `"none"`.

## Strict Source Precedence Hierarchy (Metadata & Cues)

When retrieving exercise details, metadata fields, cues, and exercise overviews, strictly enforce the following hierarchy:

1.  **User-Provided Source of Truth (Absolute Priority)**:
      - Any custom URL, notes, form cues, video links, or property overrides explicitly provided by the user override all external databases.

2.  **MuscleWiki (`@user:musclewiki`) (1st Priority — Highest Precedence for Metadata)**:
      - **Always query MuscleWiki first** for exercise metadata, muscle classifications, and anatomical breakdowns.
      - Map MuscleWiki primary and secondary muscles, body area, contraction type, and equipment/tools.

3.  **Muscle & Strength (`@user:muscleandstrength`) (2nd Priority)**:
      - Consult if the exercise or required details are not fully covered on MuscleWiki.
      - Extract target muscles, mechanics, difficulty, equipment, step-by-step instructions, and form tips from `https://www.muscleandstrength.com/exercises/{exercise-slug}`.

4.  **Trainwell (`@user:trainwell`) (3rd Priority)**:
      - Consult to extract exercise overview, muscles used, equipment, form cues, and coaching points from `https://www.trainwell.net/exercises/{exercise-slug}`.

5.  **Web Search Fallback (4th Priority)**:
      - Best-effort web search across reputable fitness libraries if the movement is not found in the primary databases.

## Video Media Format & Embedding Directives

  - **`# Video Demonstrations`**:
      - Include concise, high-quality YouTube movement demonstrations showing clean execution across key equipment/angle variations (e.g., Bodyweight, Dumbbells, Barbell, setup/technique demos, or YouTube Shorts).
      - Ensure demonstration titles clearly describe the variation and angle/tool.

  - **`# Coaching Videos`**:
      - Strictly reserved for comprehensive form analysis, technique tutorials, and biomechanics coaching videos.
      - Enforce Coaching Video Hierarchy:
        1.  **Squat University YouTube Channel** (Top priority).
        2.  **Reputable Biomechanics / PT Channels**: Conor Harris (`https://www.youtube.com/@conorharris`), ATHLEAN-X, Renaissance Periodization (Dr. Mike Israetel), Movement Physio, Dr. Carl Baird.
        3.  **General Fitness Guides**: Other high-quality form tutorials when top-tier coaching channels do not cover the movement.

## Reference Page Standard & Template

All created exercise pages must conform to the structure of the reference page ([Face Pull Ups](https://app.notion.com/p/3c562a72b770819ca31fc1f039259b4d)):

``` markdown
<callout icon="📖" color="blue_bg">
	**{Source_Name} Reference**: Sourced from [{Guide_Title}]({Source_URL}).
	{400-Character Comprehensive Summary}
</callout>

# Video Demonstrations
<video src="{YouTube_Demonstration_URL}">{Exercise_Name} Demonstration ({Tool} / {Focus})</video>

---

# Coaching Videos
<video src="{YouTube_Coaching_URL}">{Exercise_Name} Coaching ({Channel_Name} — {Focus})</video>
```

### Top Callout Box Guidelines (~400 Characters Summary)

The top callout box must contain a high-density, ~400-character summary structured as follows:

1.  **Header & Attribution**: `**{Source_Name} Reference**: Sourced from [{Guide_Title}]({Source_URL}).` (Attributed according to the source hierarchy: user source, MuscleWiki, Muscle & Strength, Trainwell, or external reference).
2.  **~400 Character Body Text**: A concise paragraph (~380–420 characters) detailing:
      - **Movement Definition & Mechanics**: Equipment/body positioning and movement plane.
      - **Key Execution Cues**: Biomechanical focus (torso angle, hip alignment, lockout, core bracing).
      - **Target Muscle Engagement**: Primary and stabilizer muscles.
      - **Functional & Postural Benefits**: Physical application (joint health, mobility, posture, injury resilience).

## Steps & Workflow

1.  **Extract Exercise Target & User Input**:
      - Identify the exercise name.
      - Check if the user supplied custom URLs, notes, video links, or property overrides.

2.  **Retrieve Exercise Metadata & Cues**:
      - Query MuscleWiki first, then Muscle & Strength, then Trainwell.
      - Extract and map all database properties:
          - **Area**: JSON array (`Upper Body`, `Lower Body`, `Core`, `Feet`)
          - **Contraction Type**: JSON array (`Dynamic`, `Isometric`, `Eccentric`)
          - **Multiplicity**: JSON array (`Single`, `Routine`)
          - **Tool**: JSON array (`Bar`, `Hanging Board`, `Gymnastic Rings`, `Bodyweight`, `Dumbbell`, `Resistance Band`, `TRX`, `Kettlebell`, `Med Ball`, etc.)
          - **Place**: JSON array (`Gym`, `Home`, `Climbing Gym`, `Outdoor Park`)
          - **Target Muscles**: JSON array (`Glutes`, `Hamstrings`, `Adductors`, `Hip Flexors`, `Core`, `Lower Leg`, `Calfs`, `Feet`, `Erector Spinae`, `Lats`, `Biceps`, `Rhomboids`, `Rear Deltoids`, `Rotator Cuff`, `Forearms`, `Obliques`, `Groin`)

3.  **Retrieve & Curate YouTube Video Media**:
      - Find high-quality YouTube demonstration videos/shorts for `# Video Demonstrations`.
      - Find in-depth YouTube coaching tutorials prioritizing Squat University and Conor Harris/PT channels for `# Coaching Videos`.
      - **Never use raw .mp4 CDN links.**

4.  **Construct & Create/Update Page via Notion CLI**:
      - Compose Notion Markdown adhering to the Face Pull Ups structure.
      - Encode database properties as a JSON dictionary:
        ```json
        {
          "Area": ["Upper Body"],
          "Contraction Type": ["Dynamic"],
          "Multiplicity": ["Single"],
          "Tool": ["Bar"],
          "Place": ["Gym"],
          "Target Muscles": ["Lats", "Biceps"]
        }
        ```
      - Execute `notion-cli page create`:
        ```bash
        notion-cli page create \
          --database \
          --parent ba872d615db54338b586006e708e3fc7 \
          --title "{Exercise_Name}" \
          --properties '{...properties json...}' \
          --body "{Page_Markdown_Content}" \
          --open
        ```
      - Provide a confirmation response with a clickable link to the page.
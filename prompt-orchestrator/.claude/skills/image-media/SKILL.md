---
name: image-media
description: Generate, edit, and process visual artifacts, diagrams, and multimedia
  assets. Use when creating UI mockups, visual explainers, image transformations,
  or media layouts (carousel, bento grid).
argument-hint: <image prompt or media task>
---

<!-- Generated from skills/image-media.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: Image & Media Handling

## Purpose
Generate, edit, and process images and other media assets.

## Tools Required
- Image generation tools (text2im, image_gen)
- Image editing tools (image_edit)
- Video generation tools (video_gen)
- Vision/analysis tools

## General Principles
- Only generate images when they add significant value to the response
- If text alone is clear and sufficient, don't add images
- Prefer built-in vision capabilities over OCR: OCR is high-cost, high-risk, last-resort
- OCR libraries support English only

## Image Generation

### When to Generate Images
**High value use cases:**
- Explaining processes visually
- Browsing and inspiration
- Exploratory context
- Highlighting differences (before/after)
- Quick visual grounding
- Visual comprehension
- Introducing people/places

**Low value / avoid:**
- UI walkthroughs without exact current screenshots
- Precise comparisons requiring accuracy
- Speculation / spoilers / guesswork
- Mathematical accuracy
- Casual chit-chat / emotional support
- Pure text-based tasks (definitions, grammar)
- Writing / coding / data analysis

### Layout Options
- **carousel** (default): swipeable images in a row
- **bento**: grid layout at top of response as cover; use for single entity deep-dives (person, place, sport team)

### Image Parameters
- Aspect ratio: `1:1` (default) or `16:9`
- Query: search terms to find relevant images
- num_per_query: 1-5 images per query term
- size: image dimensions
- transparent_background: for PNG output

## Image Editing
- Modify existing images based on instructions
- Add/remove elements
- Alter colors, style transfer
- Improve quality/resolution
- Transform style (cartoon, oil painting, etc.)

## Video Generation
- Available when the tool supports it
- Text-to-video with audio cues
- Extending existing videos
- Generating videos between specified first and last frames
- Using reference images to guide content

## Visual Analysis
- Use vision capabilities to describe image content
- Extract text from images when necessary
- Analyze charts, diagrams, screenshots
- Identify objects, people, scenes
- Read UI layouts for automation

## When to Use Multiple Image Groups
- Long, multi-section answers: one image group per major section
- Compare-and-contrast across categories
- Timeline or era segmentation
- Geographic or regional breakdowns
- Ingredient → steps → finished result

## Image Citations
- When using web-sourced images, cite the source
- For generated images, no citation needed
- Don't fabricate image URLs

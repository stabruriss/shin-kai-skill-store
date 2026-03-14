---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality and on-demand SVG asset generation via Quiver AI. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code with integrated SVG logos, icons, and illustrations.
license: Complete terms in LICENSE.txt
allowed-tools: Bash(curl:*)
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

## SVG Asset Generation (Quiver AI)

When a frontend design needs custom vector assets — logos, icons, illustrations, decorative elements, hero graphics, dividers, or background patterns — use the Quiver AI API to generate production-ready SVGs on demand.

### Setup

The API requires the environment variable `QUIVER_AI_API_KEY`. Before making any API calls:

1. Check if `QUIVER_AI_API_KEY` is set in the environment
2. If not set, **ask the user for their Quiver AI API key** before proceeding
3. Keys can be obtained at https://app.quiver.ai/settings/api-keys

### Text-to-SVG Generation

Generate SVGs from descriptive text prompts:

```bash
curl --request POST \
  --url https://api.quiver.ai/v1/svgs/generations \
  --header "Authorization: Bearer $QUIVER_AI_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "model": "arrow-preview",
    "prompt": "A geometric logo for a fintech startup, minimal lines, sharp angles",
    "n": 1,
    "stream": false
  }'
```

### Image-to-SVG Vectorization

Convert existing raster images (PNG, JPG) into clean SVG vectors:

```bash
curl --request POST \
  --url https://api.quiver.ai/v1/svgs/vectorizations \
  --header "Authorization: Bearer $QUIVER_AI_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "model": "arrow-preview",
    "image": "<base64-encoded-image-or-url>",
    "n": 1,
    "stream": false
  }'
```

### Best Practices

- **Prompt with aesthetic context**: Write prompts that match the design's tone and direction. Instead of "a logo", write "a brutalist monochrome logo with raw geometric shapes and sharp edges" — align the SVG style with the overall frontend aesthetic.
- **Color coherence**: Reference the design's color palette in the prompt so generated SVGs harmonize with the interface.
- **Inline embedding**: Embed SVGs directly in HTML/JSX for maximum flexibility — this enables CSS styling, hover animations, theme-aware color switching, and dynamic manipulation.
- **Generate variations**: Use `"n": 2` or `"n": 3` to get multiple options, then pick the best fit.
- **Rate limit**: 20 requests per 60 seconds per organization. Plan batch generation accordingly.

# Claude Web Clipper

Claude acts as a substitute for the Obsidian Web Clipper browser extension.
When asked to "clip" a URL, Claude performs the following steps:

## Steps Claude Performs

1. Fetch the page using WebFetch
2. Extract metadata:
   - title
   - author (if found)
   - published date (if found)
   - source URL
   - tags (inferred from content)
3. Convert page content to clean Markdown
4. Compose a YAML frontmatter block with the extracted metadata,
   plus an `images:` list of all image URLs found on the page
5. Write the result to `raw/articles/<slug>.md`
   where slug is a lowercase-hyphenated version of the title

## Image Limitation

Claude cannot download binary image files. All image URLs are captured in
the frontmatter under `images:` for manual download to `raw/assets/`.

## Usage

Say: "clip this URL: <url>"
Claude will produce and save the clipped Markdown file.

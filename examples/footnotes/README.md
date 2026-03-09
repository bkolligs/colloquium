# Footnotes

This example deck shows the two supported footnote patterns:

- inline numbered footnotes with `^[...]`
- floating slide notes with `<!-- footnote: ... -->` or `<!-- footnote-right: ... -->`

Patterns in [`footnotes.md`](./footnotes.md):

- one inline numbered footnote on the right
- two inline numbered footnotes on the same slide
- inline numbered footnotes positioned on the left with `<!-- footnotes: left -->`
- inline numbered footnotes stacked with a floating citation
- a plain unnumbered floating slide note

Basic usage:

```md
This sentence has a footnote marker.^[This renders as a numbered note above the footer.]
```

Move inline numbered footnotes to the left:

```md
<!-- footnotes: left -->
```

Plain floating slide note without an inline marker:

```md
<!-- footnote-right: This note lives in the footer area without adding a marker in the body. -->
```

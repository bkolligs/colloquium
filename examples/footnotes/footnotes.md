---
title: "Footnotes"
author: "Colloquium"
footer:
  left: "examples/footnotes"
  right: "auto"
bibliography: ../hello/refs.bib
---

## Inline numbered footnote

This sentence ends with a numbered footnote marker.^[This note is collected into the bottom-right stack.]

---

## Two inline footnotes

The first point gets one note.^[Footnotes are numbered in order of appearance on the slide.] The second point gets another.^[Each marker links down to the corresponding note.]

---

<!-- footnotes: left -->
## Left-side inline footnotes

When the right side is busy, move the notes left.^[This is helpful when the right footer already holds a logo or a dense citation.] You can still keep the marker inline where the sentence needs it.^[The bottom note block stays left-aligned.]

---

<!-- cite-right: christiano2017 -->
## Footnote and citation together

This slide has a regular citation and an inline numbered footnote.^[Citations stay above the footnote stack when they share a side.]

---

<!-- footnote-right: This is a plain floating slide note with no inline marker in the body. -->
## Unnumbered floating footnote

Use this when you want a quiet caveat or speaker-side context, but you do not want a numbered marker in the main text.

---

<!-- footnote: This is the same unnumbered floating note pattern, but pinned to the left side. -->
## Unnumbered floating footnote on the left

This version behaves like `cite` vs `cite-right`: no inline marker, just a footer note on the chosen side.

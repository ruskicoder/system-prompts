# Citations: verification and formats

## Verify before citing

A reference enters the list only after all of these hold:

1. You or the agent opened the source itself (the paper, the standard, the page), not a summary
   of it, and found the passage that supports the sentence citing it.
2. Its DOI resolves to the same title, first author and year. Run
   `scripts/check_refs.py references.md` yourself and read every line of its output. It checks
   every DOI and URL on each reference line. `fail` means a DOI is not registered or a URL does
   not answer, even after a retry with a browser User-Agent. `mismatch` means the DOI belongs to
   a different work. `unchecked` means the line has no DOI or URL, or the network failed. All
   three block submission until resolved.
3. A source without a DOI (a standard, a web page, documentation, a book) has a URL that opens,
   or an ISBN you checked in a library catalogue. The checker reports a line with neither as
   `unchecked, no identifier`; check it by hand and say how. Record the access date for web pages.
4. The claim in your sentence matches the source's claim in scope and strength. "Detectors
   misclassified non-native writers' TOEFL essays" is what Liang et al. found; "detectors cannot
   detect AI" is not.

If a reference fails, remove it and the claim it supported, or replace both with a source that
passes. Tell the writer which references were removed. Never fill a gap with a plausible author,
title, year or DOI: an invented reference that a lecturer checks is an academic-integrity case.

Wikipedia's AI Cleanup editors list invalid DOIs, DOIs that lead to unrelated articles, book
citations without pages and links to search results as signs of generated text
("Wikipedia:Signs of AI writing", retrieved 2026-11-07).

## What to cite

| Claim | Cite |
|---|---|
| A fact about your own system (latency, range, number of use cases) | Your test, log or design section, by number: "Table 5", "test T4" |
| A fact about the world (how often hikers lose signal) | A survey, paper or official statistic |
| A technique or algorithm you use | The paper or standard that defines it |
| A library, API or platform behaviour | Its official documentation, with the version |
| A competing product (related work) | The product's own documentation or a review of it, with access date |

Common knowledge in the field ("HTTP is stateless") needs no citation. When unsure whether a
claim is common knowledge, cite it.

## IEEE (numbered, order of first citation)

In text: "...as LoRa trades data rate for range [3]." Several sources: [3], [5] or [3]-[5].
The number goes inside the sentence, before the period. Authors' initials come first.

```
[1] D. Kobak, R. González-Márquez, E.-Á. Horvát, and J. Lause, "Delving into LLM-assisted writing in biomedical publications through excess vocabulary," Sci. Adv., vol. 11, no. 27, Art. no. eadt3813, Jul. 2025, doi: 10.1126/sciadv.adt3813.
[2] G. D. Gopen and J. A. Swan, "The science of scientific writing," Amer. Scientist, vol. 78, no. 6, pp. 550–558, Nov.–Dec. 1990.
[3] Wikipedia contributors, "Wikipedia:Signs of AI writing," Wikipedia. Accessed: Nov. 7, 2026. [Online]. Available: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
```

Shapes:

| Type | Pattern |
|---|---|
| Journal | Initials. Surname, "Title in sentence case," *Abbrev. Journal*, vol. x, no. x, pp. x–y, Mon. year, doi: x. |
| Conference | Initials. Surname, "Title," in *Proc. Conf. Name*, City, Country, year, pp. x–y, doi: x. |
| Book | Initials. Surname, *Title*, xth ed. City, Country: Publisher, year. |
| Standard | *Title of Standard*, Standard number, year. |
| Web page or documentation | Author or organisation, "Title," Site. Accessed: Mon. day, year. [Online]. Available: URL |

Source: IEEE Periodicals, *IEEE Reference Guide*, https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf

## APA 7 (author-date, alphabetical)

In text: "(Liang et al., 2023)" or "Liang et al. (2023) found...". Three or more authors take
"et al." from the first citation.

```
Liang, W., Yuksekgonul, M., Mao, Y., Wu, E., & Zou, J. (2023). GPT detectors are biased against non-native English writers. Patterns, 4(7), Article 100779. https://doi.org/10.1016/j.patter.2023.100779
Weber-Wulff, D., Anohina-Naumeca, A., Bjelobaba, S., Foltýnek, T., Guerrero-Dib, J., Popoola, O., Šigut, P., & Waddington, L. (2023). Testing of detection tools for AI-generated text. International Journal for Educational Integrity, 19, Article 26. https://doi.org/10.1007/s40979-023-00146-z
```

Journal and volume are italic in the submitted document. Web pages that change carry a
retrieval date: "Retrieved November 7, 2026, from URL".

Source: American Psychological Association, "References," APA Style, https://apastyle.apa.org/style-grammar-guidelines/references

## Which style

Use the style the course template or supervisor names. If none is named, IEEE suits software
engineering reports. Never mix the two in one document.

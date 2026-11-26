# Historical documentation archive

[Italian original](README.it.md)

This local directory preserves earlier versions of the paper. The paper files are excluded from the public v1.0.0 commit because authorship and redistribution rights have not been confirmed. Their local hashes are recorded in [EXCLUDED_MATERIALS.md](../../EXCLUDED_MATERIALS.md). They do not authoritatively describe version v1.0.0.

## Local-only contents

- `complete_paper_v1.md`: Markdown source of the first complete paper;
- `complete_paper_v1.pdf`: PDF export from the same stage;
- `complete_paper_v1.docx`: Word export from the same stage;
- `revised_paper_v3.pdf`: a later revision, preceding the v170 protocol.

## Known limitations

These documents:

- still describe the Tkinter interface;
- do not include the complete GPU backend;
- do not formalize the `start` parameter;
- do not adequately distinguish the XY plane from Linear placement;
- do not specify all implemented metrics;
- contain experimental claims not yet supported by statistical intervals;
- are not the project's current paper.

The active v1.0.0 references are:

- [`../README.md`](../README.md);
- [`../software_manual.md`](../software_manual.md);
- [`../research_protocol.md`](../research_protocol.md).

A new paper should be generated only after carrying out the confirmatory study defined in the research protocol.

## Review before publication

The PDFs have Author metadata “ChatGPT Canvas” and Creator metadata “ChatGPT”; these do not identify the human author. Paper v1 interprets global entropy as spatial dispersion and describes the baseline as preserving hit counts exactly: these descriptions do not match the current metrics. Claims of empirical significance are not validated by software tests. The local originals remain unchanged and ignored.

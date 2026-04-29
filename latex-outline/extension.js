const vscode = require("vscode");
const path = require("path");
const fs = require("fs");

// Use in-memory document if open, otherwise from disk
async function openTextSynchronously(uri) {
  const openDoc = vscode.workspace.textDocuments.find(
    d => d.uri.toString() === uri.toString()
  );
  if (openDoc) {
    return openDoc;
  }
  return await vscode.workspace.openTextDocument(uri);
}

// Recursively expand \input/\include with file/line mapping
async function expandInputs(uri, visited = new Set(), rootUri = uri) {
  if (visited.has(uri.fsPath)) return [];
  visited.add(uri.fsPath);

  let expanded = [];

  try {
    const doc = await openTextSynchronously(uri);
    const lines = doc.getText().split(/\r?\n/);

    // accept \input{file} or \include{file}
    const inputCmd = /^\s*\\(?:input|include)\{([^}]+)\}/;

    // -- detection regexes (match the same cases extractLatexHierarchy cares about)
    const sectionRegex = /\\(part|chapter|section|subsection|subsubsection|annexture)(\*)?\{([^}]+)\}/;
    const appendixRegex = /\\appendix/;
    const frontmatterRegex = /\\frontmatter/;
    const mainmatterRegex = /\\mainmatter/;
    const tocRegex = /\\tableofcontents/;
    const lotRegex = /\\listoftables/;
    const lofRegex = /\\listoffigures/;
    const titlePageRegex = /\\begin\{titlepage\}/;
    const endTitlePageRegex = /\\end\{titlepage\}/;

    // Make captionsetup detection robust: allow spaces/options and other keys
    const captionSetupTableRegex = /\\captionsetup\{[^}]*\btype\s*=\s*table\b[^}]*\}/;
    const captionSetupFigureRegex = /\\captionsetup\{[^}]*\btype\s*=\s*figure\b[^}]*\}/;

    const captionRegex = /\\caption\{([^}]+)\}/;
    const bibliographyRegex = /\\bibliography\{[^}]+\}/;
    const titleRegex = /\\title\{([^}]+)\}/;
    const beginTheBibliographyRegex = /\\begin\{thebibliography\}\{[^}]*\}/;
    const renewBibNameRegex = /\\renewcommand\s*\{\\bibname\}\s*\{([^}]+)\}/;
    const renewRefNameRegex = /\\renewcommand\s*\{\\refname\}\s*\{([^}]+)\}/;
    const printBibliographyRegex = /\\printbibliography(?:\[(.*?)\])?/;

    // updated: match figure* and table* (begin)
    const beginFigureRegex = /^\s*\\begin\{figure\*?\}/;
    const beginTableRegex = /^\s*\\begin\{table\*?\}/;

    // unnamed table detection (avoid nested detection), support table*
    const unnamedTableRegex = /\\begin\{table\*?\}(?![\s\S]*?\\begin\{table\*?\}[\s\S]*?\\end\{table\*?\})/;

    function contributesOutline(srcLines) {
      // srcLines: array of { text, uri, lineNum, placeholder?, missing? }
      return srcLines.some(({ text, placeholder }) => {
        if (placeholder) return true;            // nested empty file placeholder -> counts as outline content
        if (!text) return false;
        const line = text.trim();
        if (line.startsWith("%")) return false;
        return sectionRegex.test(line) ||
          appendixRegex.test(line) ||
          frontmatterRegex.test(line) ||
          mainmatterRegex.test(line) ||
          tocRegex.test(line) ||
          lotRegex.test(line) ||
          lofRegex.test(line) ||
          titlePageRegex.test(line) ||
          endTitlePageRegex.test(line) ||
          captionSetupTableRegex.test(line) ||
          captionSetupFigureRegex.test(line) ||
          captionRegex.test(line) ||
          bibliographyRegex.test(line) ||
          titleRegex.test(line) ||
          beginTheBibliographyRegex.test(line) ||
          printBibliographyRegex.test(line) ||
          beginFigureRegex.test(line) ||
          beginTableRegex.test(line) ||
          unnamedTableRegex.test(line);
      });
    }

    // iterate lines and expand inputs recursively
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const m = inputCmd.exec(line); // already trimmed within regex
      if (m) {
        const relPath = m[1];
        const isDotRelative = relPath.startsWith("./");
        const basedir = isDotRelative
          ? path.dirname(rootUri.fsPath)   // use root for ./ paths
          : path.dirname(uri.fsPath);      // normal behavior
        const candidates = [
          path.resolve(basedir, relPath),
          path.resolve(basedir, relPath + ".tex"),
        ];
        let target;
        for (const p of candidates) {
          if (fs.existsSync(p)) {
            target = vscode.Uri.file(p);
            break;
          }
        }

        // Missing file → always add a placeholder inline at the current position
        if (!target) {
          const baseName = path.basename(candidates[1], ".tex");
          expanded.push({
            text: "",
            uri: vscode.Uri.file(candidates[1]), // would-be file
            lineNum: 0,
            placeholder: `[${baseName}]`,
            missing: true,
            topLevel: uri.fsPath === rootUri.fsPath,
          });
          continue;
        }

        // Existing file → expand recursively
        const baseName = path.basename(target.fsPath, ".tex");
        const childExpanded = await expandInputs(target, visited, rootUri);
        if (contributesOutline(childExpanded)) {
          expanded.push(...childExpanded);
        } else {
          // If the included file customizes \bibname but has no outline items,
          // use it to label the placeholder more helpfully (e.g., "Chapter References").
          let placeholderLabel = `[${baseName}]`;
          for (const ce of childExpanded) {
            if (!ce || !ce.text) continue;
            const t = (ce.text || "").trim();
            const mBib = renewBibNameRegex.exec(t) || renewRefNameRegex.exec(t);
            if (mBib) {
              const name = mBib[1].trim();
              placeholderLabel = `Chapter ${name}`;
              break;
            }
            const mPrint = printBibliographyRegex.exec(t);
            if (mPrint && mPrint[1]) {
              const opt = mPrint[1];
              const mTitle = /(?:^|,)\s*title\s*=\s*\{([^}]*)\}/.exec(opt);
              if (mTitle) {
                placeholderLabel = `Chapter ${mTitle[1].trim()}`;
                break;
              }
            }
          }
          // Inline placeholder so ordering matches the LaTeX source
          expanded.push({
            text: "",
            uri: target,
            lineNum: 0,
            placeholder: placeholderLabel,
            missing: false,
            topLevel: uri.fsPath === rootUri.fsPath,
          });
        }
        continue;
      }

      // normal non-\input line
      expanded.push({ text: line, uri, lineNum: i });
    }

  } catch (e) {
    // optionally console.error(e);
  } finally {
    visited.delete(uri.fsPath);
  }

  return expanded;
}


function extractLatexHierarchy(srcLines) {
  const symbols = [];
  const parents = {
    chapter: null, section: null, subsection: null, subsubsection: null,
    annexture: null, figure: null, table: null,
  };
  let insideTitlePage = false;
  let titlePageSymbol = null;
  let lastParent = null;

  // Appendix tracking
  let insideAppendix = false;
  let appendixNode = null;
  let appendixChapter = null;      // Track chapter inside appendix
  let currentAnnexure = null;      // Track annexture inside a chapter

  // Front matter tracking
  let insideFrontmatter = false;
  let frontmatterNode = null;
  let frontmatterChapter = null;   // Track chapter inside front matter

  // Setup (pre-document) tracking
  let beforeDocument = true;
  let setupNode = null;
  let bibNameOverride = null;
  let refNameOverride = null;

  const lines = srcLines.map(x => x.text);
  const sectionRegex = /\\(part|chapter|section|subsection|subsubsection|annexture)(\*)?\{([^}]+)\}/;
  const appendixRegex = /\\appendix/;
  const frontmatterRegex = /\\frontmatter/;
  const mainmatterRegex = /\\mainmatter/;
  const beginDocRegex = /\\begin\{document\}/;
  const tocRegex = /\\tableofcontents/;
  const lotRegex = /\\listoftables/;
  const lofRegex = /\\listoffigures/;
  const titlePageRegex = /\\begin\{titlepage\}/;
  const endTitlePageRegex = /\\end\{titlepage\}/;

  // robust captionsetup regexes (allow extra options / whitespace)
  const captionSetupTableRegex = /\\captionsetup\{[^}]*\btype\s*=\s*table\b[^}]*\}/;
  const captionSetupFigureRegex = /\\captionsetup\{[^}]*\btype\s*=\s*figure\b[^}]*\}/;

  const captionRegex = /\\caption\{([^}]+)\}/;
  const bibliographyRegex = /\\bibliography\{[^}]+\}/;
  const beginTheBibliographyRegex = /\\begin\{thebibliography\}\{[^}]*\}/;
  const renewBibNameRegex = /\\renewcommand\s*\{\\bibname\}\s*\{([^}]+)\}/;
  const renewRefNameRegex = /\\renewcommand\s*\{\\refname\}\s*\{([^}]+)\}/;
  const printBibliographyRegex = /\\printbibliography(?:\[(.*?)\])?/;
  const unnamedTableRegex = /\\begin\{table\*?\}(?![\s\S]*?\\begin\{table\*?\}[\s\S]*?\\end\{table\*?\})/;
  const titleRegex = /\\title\{([^}]+)\}/;

  // match begin / end with optional star
  const beginFigureRegex = /^\s*\\begin\{figure\*?\}/;
  const beginTableRegex = /^\s*\\begin\{table\*?\}/;
  const endFigureRegex = /^\s*\\end\{figure\*?\}/;
  const endTableRegex = /^\s*\\end\{table\*?\}/;

  function cleanLatexTitle(title) {
    return title.replace(/\\[a-zA-Z]+\{[^}]*\}/g, "").replace(/\\[a-zA-Z]+/g, "").trim();
  }
  let insideFigure = false, figureStartIdx = 0, figureCaption = null;
  let insideTable = false, tableStartIdx = 0, tableCaption = null;

  // Track if a figure env has inner captioned items (minipages + captionsetup)
  let insideFigureInnerCount = 0;

  // New: pending placeholders/items encountered inside figure/table envs
  let pendingFigureChildren = [];
  let pendingTableChildren = [];

  for (let idx = 0; idx < lines.length; idx++) {
    let line = (lines[idx] || "").trim();
    if (line.startsWith("%")) continue;
    const { uri, lineNum, placeholder, missing, topLevel } = srcLines[idx];

    // Detect start of document: end of "Setup" phase
    if (beforeDocument && beginDocRegex.test(line)) {
      beforeDocument = false;
      // do not 'continue' here — allow same-line constructs if ever present
    }

    // Handle placeholder directly (preserve missing flag)
    if (placeholder) {
      const item = {
        label: placeholder,
        file: uri,
        line: lineNum,
        kind: "file",
        children: [],
        missing: !!missing,
      };

      // If inside a figure/table environment, defer to that environment
      if (insideFigure) {
        pendingFigureChildren.push(item);
        continue;
      }
      if (insideTable) {
        pendingTableChildren.push(item);
        continue;
      }

      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(item);
        continue;
      }

      // If this placeholder comes directly from a top-level include in the root file,
      // show it at the top level (or within active frontmatter/appendix scopes),
      // not nested under the previous section/chapter.
      if (topLevel) {
        if (insideAppendix && appendixNode) {
          appendixNode.children.push(item);
        } else if (insideFrontmatter && frontmatterNode) {
          if (frontmatterChapter) frontmatterChapter.children.push(item);
          else frontmatterNode.children.push(item);
        } else {
          symbols.push(item);
        }
        continue;
      }

      let parent =
        parents.subsubsection ||
        parents.subsection ||
        parents.section ||
        parents.annexture ||
        parents.chapter;

      if (insideAppendix && appendixNode) {
        if (currentAnnexure) currentAnnexure.children.push(item);
        else if (appendixChapter) appendixChapter.children.push(item);
        else appendixNode.children.push(item);
      } else if (insideFrontmatter && frontmatterNode) {
        if (frontmatterChapter) frontmatterChapter.children.push(item);
        else frontmatterNode.children.push(item);
      } else if (parent) {
        parent.children.push(item);
      } else {
        symbols.push(item);
      }

      continue;
    }

    // Title / bibliography / titlepage / lists
    let titleMatch = titleRegex.exec(line);
    if (titleMatch) {
      const titleItem = {
        label: "Title",
        file: uri,
        line: lineNum,
        kind: "file",
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(titleItem);
      } else if (insideFrontmatter && frontmatterNode) {
        frontmatterNode.children.push(titleItem);
      } else {
        symbols.push(titleItem);
      }
      continue;
    }
    if (bibliographyRegex.test(line)) {
      const bibItem = {
        label: (bibNameOverride || refNameOverride || "References"),
        file: uri,
        line: lineNum,
        kind: "bibliography",
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(bibItem);
      } else {
        symbols.push(bibItem);
      }
      continue;
    }
    // Detect in-file label overrides for bibliography
    let bibnameMatch = renewBibNameRegex.exec(line);
    if (bibnameMatch) {
      bibNameOverride = bibnameMatch[1].trim();
      continue;
    }
    let refnameMatch = renewRefNameRegex.exec(line);
    if (refnameMatch) {
      refNameOverride = refnameMatch[1].trim();
      continue;
    }
    // Detect thebibliography environment
    if (beginTheBibliographyRegex.test(line)) {
      const bibItem = {
        label: (bibNameOverride || refNameOverride || "References"),
        file: uri,
        line: lineNum,
        kind: "bibliography",
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(bibItem);
      } else {
        symbols.push(bibItem);
      }
      continue;
    }
    // Detect biblatex's \printbibliography with optional [title={...}, ...]
    let printBibMatch = printBibliographyRegex.exec(line);
    if (printBibMatch) {
      let label = (bibNameOverride || refNameOverride || "References");
      const opts = printBibMatch[1];
      if (opts) {
        const titleMatch = /(?:^|,)\s*title\s*=\s*\{([^}]*)\}/.exec(opts);
        if (titleMatch) label = titleMatch[1].trim();
      }
      const bibItem = {
        label,
        file: uri,
        line: lineNum,
        kind: "bibliography",
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(bibItem);
      } else {
        symbols.push(bibItem);
      }
      continue;
    }
    if (titlePageRegex.test(line)) {
      insideTitlePage = true;
      titlePageSymbol = {
        label: "Title Page",
        file: uri,
        line: lineNum,
        kind: "file",
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(titlePageSymbol);
      } else if (insideFrontmatter && frontmatterNode) {
        frontmatterNode.children.push(titlePageSymbol);
      } else if (insideAppendix && appendixNode) {
        appendixNode.children.push(titlePageSymbol);
      } else {
        symbols.push(titlePageSymbol);
      }
      continue;
    }
    if (insideTitlePage && endTitlePageRegex.test(line)) {
      insideTitlePage = false;
      titlePageSymbol = null;
      continue;
    }
    if (tocRegex.test(line)) {
      const item = {
        label: "Table of Contents",
        file: uri,
        line: lineNum,
        kind: "toc",
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(item);
      } else if (insideFrontmatter && frontmatterNode) {
        frontmatterNode.children.push(item);
      } else {
        symbols.push(item);
      }
      continue;
    }
    if (lotRegex.test(line)) {
      const item = {
        label: "List of Tables",
        file: uri,
        line: lineNum,
        kind: "lot",
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(item);
      } else if (insideFrontmatter && frontmatterNode) {
        frontmatterNode.children.push(item);
      } else {
        symbols.push(item);
      }
      continue;
    }
    if (lofRegex.test(line)) {
      const item = {
        label: "List of Figures",
        file: uri,
        line: lineNum,
        kind: "lof",
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(item);
      } else if (insideFrontmatter && frontmatterNode) {
        frontmatterNode.children.push(item);
      } else {
        symbols.push(item);
      }
      continue;
    }
    if (frontmatterRegex.test(line)) {
      frontmatterNode = {
        label: "Front Matter",
        file: uri,
        line: lineNum,
        kind: "frontmatter",
        children: [],
      };
      symbols.push(frontmatterNode);
      insideFrontmatter = true;
      frontmatterChapter = null;
      continue;
    }
    if (mainmatterRegex.test(line)) {
      // End front matter if active
      insideFrontmatter = false;
      frontmatterChapter = null;
      continue;
    }
    if (appendixRegex.test(line)) {
      appendixNode = {
        label: "Appendix",
        file: uri,
        line: lineNum,
        kind: "appendix",
        children: [],
      };
      symbols.push(appendixNode);
      insideAppendix = true;
      appendixChapter = null;
      currentAnnexure = null;
      continue;
    }

    // Sections
    let sectionMatch = sectionRegex.exec(line);
    if (sectionMatch) {
      const sectionType = sectionMatch[1];
      let title = cleanLatexTitle(sectionMatch[3]);
      const item = {
        label: title,
        file: uri,
        line: lineNum,
        kind: sectionType,
        children: [],
      };
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(item);
      } else if (insideAppendix && appendixNode) {
        if (sectionType === "chapter") {
          appendixNode.children.push(item);
          appendixChapter = item;
          currentAnnexure = null;
        } else if (sectionType === "annexture" && appendixChapter) {
          appendixChapter.children.push(item);
          currentAnnexure = item;
        } else if (sectionType === "annexture") {
          appendixNode.children.push(item);
          currentAnnexure = item;
        } else if (currentAnnexure) {
          currentAnnexure.children.push(item);
        } else if (appendixChapter) {
          appendixChapter.children.push(item);
        } else {
          appendixNode.children.push(item);
        }
      } else if (insideFrontmatter && frontmatterNode) {
        if (sectionType === "chapter") {
          frontmatterNode.children.push(item);
          frontmatterChapter = item;
        } else if (frontmatterChapter) {
          frontmatterChapter.children.push(item);
        } else {
          frontmatterNode.children.push(item);
        }
      } else {
        if (sectionType === "chapter") {
          symbols.push(item);
          parents.chapter = item;
          parents.section = null;
          parents.subsection = null;
          parents.subsubsection = null;
          parents.annexture = null;
        } else if (sectionType === "section") {
          if (parents.chapter) parents.chapter.children.push(item);
          else symbols.push(item);
          parents.section = item;
          parents.subsection = null;
          parents.subsubsection = null;
          parents.annexture = null;
        } else if (sectionType === "subsection") {
          if (parents.section) parents.section.children.push(item);
          else symbols.push(item);
          parents.subsection = item;
          parents.subsubsection = null;
          parents.annexture = null;
        } else if (sectionType === "subsubsection") {
          if (parents.subsection) parents.subsection.children.push(item);
          else symbols.push(item);
          parents.subsubsection = item;
          parents.annexture = null;
        } else if (sectionType === "annexture") {
          if (parents.section) parents.section.children.push(item);
          else symbols.push(item);
          parents.annexture = item;
        }
      }
      lastParent = item;
      parents.figure = null;
      parents.table = null;
      continue;
    }

    // ---- Environment starts: detect them early so nested things can be caught ----
    if (beginFigureRegex.test(line)) {
      insideFigure = true;
      figureStartIdx = idx;
      figureCaption = null;
      insideFigureInnerCount = 0;
      pendingFigureChildren = [];
      // don't `continue` here — allow processing of captionsetup/caption on same line
    }
    if (beginTableRegex.test(line)) {
      insideTable = true;
      tableStartIdx = idx;
      tableCaption = null;
      pendingTableChildren = [];
      // don't `continue` here — allow processing of caption on same line
    }

    // Handle captionsetup inside anything (including inside a figure)
    if (captionSetupTableRegex.test(line)) {
      const item = {
        label: "Table",
        file: uri,
        line: lineNum,
        kind: "table",
        children: [],
      };

            let parent =
        parents.subsubsection ||
        parents.subsection ||
        parents.section ||
        parents.annexture ||
        parents.chapter;
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(item);
      } else if (insideAppendix && appendixNode) {
        if (currentAnnexure) currentAnnexure.children.push(item);
        else if (appendixChapter) appendixChapter.children.push(item);
        else appendixNode.children.push(item);
      } else if (insideFrontmatter && frontmatterNode) {
        if (frontmatterChapter) frontmatterChapter.children.push(item);
        else frontmatterNode.children.push(item);
      } else if (parent) parent.children.push(item);
      else symbols.push(item);
      parents.table = item;
      if (insideFigure) insideFigureInnerCount++;
      // don't continue — caption might be on same line
    }

    if (captionSetupFigureRegex.test(line)) {
      const item = {
        label: "Figure",
        file: uri,
        line: lineNum,
        kind: "figure",
        children: [],
      };

            let parent =
        parents.subsubsection ||
        parents.subsection ||
        parents.section ||
        parents.annexture ||
        parents.chapter;
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: uri,
            line: lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(item);
      } else if (insideAppendix && appendixNode) {
        if (currentAnnexure) currentAnnexure.children.push(item);
        else if (appendixChapter) appendixChapter.children.push(item);
        else appendixNode.children.push(item);
      } else if (insideFrontmatter && frontmatterNode) {
        if (frontmatterChapter) frontmatterChapter.children.push(item);
        else frontmatterNode.children.push(item);
      } else if (parent) parent.children.push(item);
      else symbols.push(item);
      parents.figure = item;
      if (insideFigure) insideFigureInnerCount++;
      // don't continue — caption might be on same line
    }

    // Now allow normal caption handling — prefers a previously-created parents.table / parents.figure
    let captionMatch = captionRegex.exec(line);
    if (captionMatch) {
      let captionText = captionMatch[1];
      if (parents.table) {
        parents.table.label = captionText;
        parents.table = null;
      } else if (parents.figure) {
        parents.figure.label = captionText;
        parents.figure = null;
      } else if (insideTable) {
        // caption that belongs to table environment
        tableCaption = captionText;
      } else if (insideFigure) {
        // caption that belongs to the (outer) figure environment
        figureCaption = captionText;
      }
      // consume caption handling, move on
      continue;
    }

    // End figure: support both \end{figure} and \end{figure*}
    if (insideFigure && endFigureRegex.test(line)) {
      if (insideFigureInnerCount === 0 || pendingFigureChildren.length > 0) {
        const start = srcLines[figureStartIdx];
        const item = {
          label: figureCaption ? figureCaption : "Figure",
          file: start.uri,
          line: start.lineNum,
          kind: "figure",
          children: [],
        };

        if (pendingFigureChildren.length > 0) {
          item.children.push(...pendingFigureChildren);
        }


        let parent =
          parents.subsubsection ||
          parents.subsection ||
          parents.section ||
          parents.annexture ||
          parents.chapter;
        if (beforeDocument) {
          if (!setupNode) {
            setupNode = {
              label: "Setup",
              file: start.uri,
              line: start.lineNum,
              kind: "setup",
              children: [],
            };
            symbols.push(setupNode);
          }
          setupNode.children.push(item);
        } else if (insideAppendix && appendixNode) {
          if (currentAnnexure) currentAnnexure.children.push(item);
          else if (appendixChapter) appendixChapter.children.push(item);
          else appendixNode.children.push(item);
        } else if (insideFrontmatter && frontmatterNode) {
          if (frontmatterChapter) frontmatterChapter.children.push(item);
          else frontmatterNode.children.push(item);
        } else if (parent) parent.children.push(item);
        else symbols.push(item);
      }
      insideFigure = false;
      figureCaption = null;
      insideFigureInnerCount = 0;
      pendingFigureChildren = [];
      continue;
    }

    // End table: support both \end{table} and \end{table*}
    if (insideTable && endTableRegex.test(line)) {
      const start = srcLines[tableStartIdx];
      const item = {
        label: tableCaption ? tableCaption : "Table",
        file: start.uri,
        line: start.lineNum,
        kind: "table",
        children: [],
      };

      if (pendingTableChildren.length > 0) {
        item.children.push(...pendingTableChildren);
      }


            let parent =
        parents.subsubsection ||
        parents.subsection ||
        parents.section ||
        parents.annexture ||
        parents.chapter;
      if (beforeDocument) {
        if (!setupNode) {
          setupNode = {
            label: "Setup",
            file: start.uri,
            line: start.lineNum,
            kind: "setup",
            children: [],
          };
          symbols.push(setupNode);
        }
        setupNode.children.push(item);
      } else if (insideAppendix && appendixNode) {
        if (currentAnnexure) currentAnnexure.children.push(item);
        else if (appendixChapter) appendixChapter.children.push(item);
        else appendixNode.children.push(item);
      } else if (insideFrontmatter && frontmatterNode) {
        if (frontmatterChapter) frontmatterChapter.children.push(item);
        else frontmatterNode.children.push(item);
      } else if (parent) parent.children.push(item);
      else symbols.push(item);
      insideTable = false;
      tableCaption = null;
      pendingTableChildren = [];
      continue;
    }

    if (unnamedTableRegex.test(line)) {
      continue;
    }
  }
  return symbols;
}

class LatexTreeProvider {
  constructor() {
    this.rootUri = null;
    this.items = [];
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    this._treeView = null;
    this._isExpanded = false;
  }
  setTreeView(tv) {
    this._treeView = tv;
  }
  async buildTreeRoot(uri) {
    this.rootUri = uri;
    const expanded = await expandInputs(uri, new Set(), uri);
    this.items = extractLatexHierarchy(expanded);
    this._onDidChangeTreeData.fire();
  }
  async refresh() {
    if (this.rootUri) {
      await this.buildTreeRoot(this.rootUri);
    }
  }
  getTreeItem(element) {
    let collapsible = element.children && element.children.length > 0
      ? (this._isExpanded ? vscode.TreeItemCollapsibleState.Expanded
        : vscode.TreeItemCollapsibleState.Collapsed)
      : vscode.TreeItemCollapsibleState.None;

    const item = new vscode.TreeItem(element.label, collapsible);

    if (element.missing) {
      item.command = {
        command: 'latexOutline.createAndOpen',
        title: 'Create file',
        arguments: [element.file],
      };
      item.description = 'missing file';
      item.iconPath = new vscode.ThemeIcon("new-file");
    } else {
      // protect against missing file URIs (shouldn't happen if missing flag correct)
      if (element.file) {
        item.command = {
          command: 'latexOutline.goto',
          title: 'Go to section',
          arguments: [element.file, element.line],
        };
      }
      item.description = element.kind;
    }

    const codicons = {
      "part": "notebook",
      "chapter": "book",
      "section": "library",
      "subsection": "repo",
      "subsubsection": "root-folder",
      "annexture": "folder",
      "appendix": "archive",
      "frontmatter": "archive",
      "setup": "gear",
      "figure": "graph",
      "table": "table",
      "file": "file",
      "toc": "list-tree",
      "lot": "list-ordered",
      "lof": "list-ordered",
      "bibliography": "references",
    };
    if (!element.missing && codicons[element.kind]) {
      item.iconPath = new vscode.ThemeIcon(codicons[element.kind]);
    }
    return item;
  }

  getChildren(element) {
    if (!element) return this.items;
    return element.children;
  }
  getParent(element) {
    function findParent(nodes, child) {
      for (let node of nodes) {
        if ((node.children || []).includes(child)) return node;
        const result = findParent(node.children || [], child);
        if (result) return result;
      }
      return null;
    }
    return findParent(this.items, element);
  }
  async toggleExpandCollapse() {
    this._isExpanded = !this._isExpanded;
    this._onDidChangeTreeData.fire();
    await new Promise((resolve) => setTimeout(resolve, 0));
    if (this._treeView && this.items.length > 0) {
      if (this._isExpanded) {
        const flatten = (arr) => arr.reduce((acc, e) => acc.concat([e], flatten(e.children || [])), []);
        const all = flatten(this.items);
        await this._treeView.reveal(this.items[0], { expand: true, focus: false, select: false });
        for (const item of all) {
          if (item.children && item.children.length > 0) {
            await this._treeView.reveal(item, { expand: true, focus: false, select: false });
          }
        }
      } else {
        await vscode.commands.executeCommand("workbench.actions.treeView.latexOutlineView.collapseAll");
      }
    }
  }
}

let treeProvider;
let persistentRootUri = null;

async function findIfDocumentClass(uri) {
  try {
    const doc = await openTextSynchronously(uri);
    return /\\documentclass(\[.*\])?\{[^\}]+\}/.test(doc.getText());
  } catch {
    return false;
  }
}

function activate(context) {
  treeProvider = new LatexTreeProvider();
  const treeView = vscode.window.createTreeView("latexOutlineView", { treeDataProvider: treeProvider });
  treeProvider.setTreeView(treeView);

  context.subscriptions.push(
    vscode.commands.registerCommand("latexOutline.goto", async (uri, line) => {
      try {
        // If doc doesn't exist, openTextSynchronously will throw; guard against it.
        const doc = await openTextSynchronously(uri);
        const editor = await vscode.window.showTextDocument(doc, { preview: false });
        const pos = new vscode.Position(line, 0);
        editor.selection = new vscode.Selection(pos, pos);
        editor.revealRange(new vscode.Range(pos, pos), vscode.TextEditorRevealType.InCenter);
      } catch (err) {
        vscode.window.showErrorMessage(`Cannot open ${uri.fsPath}: ${err.message}`);
      }
    })
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("latexOutline.createAndOpen", async (uri) => {
      try {
        // Ensure parent directory exists
        await fs.promises.mkdir(path.dirname(uri.fsPath), { recursive: true });

        // Figure out the actual root file
        const rootUri = treeProvider.rootUri;
        let starter = "";
        if (rootUri) {
          const relPath = path.relative(path.dirname(uri.fsPath), rootUri.fsPath);
          starter = `% !TeX root = ${relPath.replace(/\\/g, "/")}\n\n`;
        }

        // Create the file only if it doesn’t already exist
        if (!fs.existsSync(uri.fsPath)) {
          await fs.promises.writeFile(uri.fsPath, starter, { flag: "wx" });
        }

        // Open it
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc);

        // Refresh the outline so placeholder becomes real node
        if (treeProvider && typeof treeProvider.refresh === "function") {
          await treeProvider.refresh();
        }
      } catch (err) {
        vscode.window.showErrorMessage(`Could not create file: ${err.message}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("latexOutline.toggleExpandCollapse", async () => {
      await treeProvider.toggleExpandCollapse();
    })
  );
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(async doc => {
      if (doc.languageId === "latex" || doc.fileName.endsWith(".tex")) {
        await treeProvider.refresh();
      }
    })
  );
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(async editor => {
      if (editor && editor.document && editor.document.languageId === "latex") {
        const uri = editor.document.uri;
        if (await findIfDocumentClass(uri)) {
          persistentRootUri = uri;
          await treeProvider.buildTreeRoot(persistentRootUri);
        }
      }
    })
  );
  (async () => {
    const editor = vscode.window.activeTextEditor;
    if (editor && editor.document.languageId === "latex") {
      if (await findIfDocumentClass(editor.document.uri)) {
        persistentRootUri = editor.document.uri;
        await treeProvider.buildTreeRoot(persistentRootUri);
      }
    }
  })();
}

function deactivate() { }

module.exports = { activate, deactivate };
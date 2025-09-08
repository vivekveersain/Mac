const vscode = require("vscode");

function activate(context) {
  const provider = vscode.languages.registerDocumentSymbolProvider(
    { language: "latex" },
    {
      provideDocumentSymbols(document) {
        const symbols = [];
        const parents = {
          chapter: null,
          section: null,
          subsection: null,
          subsubsection: null,
          annexture: null,
          figure: null,
          table: null,
        };

        let insideTitlePage = false;
        let titlePageSymbol = null;
        let lastParent = null; // Stores the last valid section/subsection

        const text = document.getText();
        const lines = text.split("\n");

        // 📌 Regular Expressions
        const sectionRegex = /\\(part|chapter|section|subsection|subsubsection|annexture)(\*)?\{([^}]+)\}/;
        const appendixRegex = /\\appendix/;
        const tocRegex = /\\tableofcontents/;
        const lotRegex = /\\listoftables/;
        const lofRegex = /\\listoffigures/;
        const titlePageRegex = /\\begin\{titlepage\}/;
        const endTitlePageRegex = /\\end\{titlepage\}/;
        const captionSetupTableRegex = /\\captionsetup\{type=table\}/;
        const captionSetupFigureRegex = /\\captionsetup\{type=figure\}/;
        const captionRegex = /\\caption\{([^}]+)\}/;
        const bibliographyRegex = /\\bibliography\{[^}]+\}/;
        const unnamedTableRegex = /\\begin\{table\}(?![\s\S]*?\\begin\{table\}[\s\S]*?\\end\{table\})/;
        const titleRegex = /\\title\{([^}]+)\}/; // 📌 Added regex for \title{}

        // 📌 Clean LaTeX commands from the title
        function cleanLatexTitle(title) {
          return title.replace(/\\[a-zA-Z]+\{[^}]*\}/g, '').replace(/\\[a-zA-Z]+/g, '').trim();
        }

        // --- New: For Figure detection ---
        let insideFigure = false;
        let figureStartLine = 0;
        let figureCaption = null;

        // 🔄 Process the document line by line
        for (let lineNum = 0; lineNum < lines.length; lineNum++) {
          let line = lines[lineNum].trim();
          if (line.startsWith("%")) continue;

          // 📌 Detect \title{}
          let titleMatch = titleRegex.exec(line);
          if (titleMatch) {
            const position = new vscode.Position(lineNum, titleMatch.index);
            symbols.push(
              new vscode.DocumentSymbol(
                " ", // Always display as "Title" in the outline
                "Title",
                vscode.SymbolKind.File,
                new vscode.Range(position, position),
                new vscode.Range(position, position)
              )
            );
            continue;
          }

          // 📚 Detect bibliography (References)
          if (bibliographyRegex.test(line)) {
            const position = new vscode.Position(lineNum, 0);
            symbols.push(
              new vscode.DocumentSymbol(
                "References",
                "Bibliography",
                vscode.SymbolKind.Enum,
                new vscode.Range(position, position),
                new vscode.Range(position, position)
              )
            );
            continue;
          }

          // 🎭 Title Page Handling
          if (titlePageRegex.test(line)) {
            insideTitlePage = true;
            const position = new vscode.Position(lineNum, 0);
            titlePageSymbol = new vscode.DocumentSymbol(
              " ",
              "Title Page",
              vscode.SymbolKind.File,
              new vscode.Range(position, position),
              new vscode.Range(position, position)
            );
            symbols.push(titlePageSymbol);
            continue;
          }
          if (insideTitlePage && endTitlePageRegex.test(line)) {
            insideTitlePage = false;
            titlePageSymbol = null;
            continue;
          }

          // 📑 Detect Table of Contents
          if (tocRegex.test(line)) {
            const position = new vscode.Position(lineNum, 0);
            symbols.push(
              new vscode.DocumentSymbol(
                "Table of Contents",
                "",
                vscode.SymbolKind.Number,
                new vscode.Range(position, position),
                new vscode.Range(position, position)
              )
            );
            continue;
          }

          // 📋 Detect List of Tables
          if (lotRegex.test(line)) {
            const position = new vscode.Position(lineNum, 0);
            symbols.push(
              new vscode.DocumentSymbol(
                "List of Tables",
                "",
                vscode.SymbolKind.Number,
                new vscode.Range(position, position),
                new vscode.Range(position, position)
              )
            );
            continue;
          }

          // 🖼️ Detect List of Figures
          if (lofRegex.test(line)) {
            const position = new vscode.Position(lineNum, 0);
            symbols.push(
              new vscode.DocumentSymbol(
                "List of Figures",
                "",
                vscode.SymbolKind.Number,
                new vscode.Range(position, position),
                new vscode.Range(position, position)
              )
            );
            continue;
          }

          // 🔖 Appendix Detection
          if (appendixRegex.test(line)) {
            const position = new vscode.Position(lineNum, 0);
            symbols.push(
              new vscode.DocumentSymbol(
                " ",
                "Appendix",
                vscode.SymbolKind.Enum,
                new vscode.Range(position, position),
                new vscode.Range(position, position)
              )
            );
            continue;
          }

          // 🔷 Section Detection
          let sectionMatch = sectionRegex.exec(line);
          if (sectionMatch) {
            const sectionType = sectionMatch[1];
            let title = sectionMatch[3];

            // Clean LaTeX commands like \centering from the title
            title = cleanLatexTitle(title);

            const kind = {
              part: vscode.SymbolKind.Enum,
              chapter: vscode.SymbolKind.Class,
              section: vscode.SymbolKind.Constant,
              subsection: vscode.SymbolKind.Interface,
              subsubsection: vscode.SymbolKind.String,
              annexture: vscode.SymbolKind.Interface,
            }[sectionType];

            const position = new vscode.Position(lineNum, sectionMatch.index);
            const symbol = new vscode.DocumentSymbol(
              title,  // Cleaned title
              sectionType,
              kind,
              new vscode.Range(position, position),
              new vscode.Range(position, position)
            );

            if (sectionType === "chapter") {
              symbols.push(symbol);
              parents.chapter = symbol;
              parents.section = null;
            } else if (sectionType === "section") {
              if (parents.chapter) parents.chapter.children.push(symbol);
              else symbols.push(symbol);
              parents.section = symbol;
            } else if (sectionType === "subsection") {
              if (parents.section) parents.section.children.push(symbol);
              else symbols.push(symbol);
              parents.subsection = symbol;
            } else if (sectionType === "subsubsection") {
              if (parents.subsection) parents.subsection.children.push(symbol);
              else symbols.push(symbol);
            } else if (sectionType === "annexture") {
              if (parents.section) parents.section.children.push(symbol);
              else symbols.push(symbol);
            }

            lastParent = symbol; // Store last valid parent for tables
            parents.figure = null;
            parents.table = null;
            continue;
          }

          // -------------------------------
          // 📦 Standard Figure Environment
          // -------------------------------
          if (line.startsWith("\\begin{figure")) {
            insideFigure = true;
            figureStartLine = lineNum;
            figureCaption = null;
            continue;
          }

          if (insideFigure) {
            let figureCaptionMatch = captionRegex.exec(line);
            if (figureCaptionMatch) {
              figureCaption = figureCaptionMatch[1];
            }
            if (line.startsWith("\\end{figure}")) {
              const position = new vscode.Position(figureStartLine, 0);
              const endPosition = new vscode.Position(lineNum, 0);
              const symbol = new vscode.DocumentSymbol(
                figureCaption ? figureCaption : "Figure",
                "Figure",
                vscode.SymbolKind.Image,
                new vscode.Range(position, endPosition),
                new vscode.Range(position, position)
              );
              let parent = parents.subsection || parents.section || parents.chapter;
              if (parent) parent.children.push(symbol);
              else symbols.push(symbol);

              insideFigure = false;
              figureCaption = null;
            }
            continue; // Skip other processing while inside figure
          }
          // -------------------------------

          // 📊 Named Table Detection
          if (captionSetupTableRegex.test(line)) {
            const position = new vscode.Position(lineNum, 0);
            const tableSymbol = new vscode.DocumentSymbol(
              " ",
              "Table",
              vscode.SymbolKind.Struct,
              new vscode.Range(position, position),
              new vscode.Range(position, position)
            );

            let parent = parents.subsection || parents.section || parents.chapter;
            if (parent) parent.children.push(tableSymbol);
            else symbols.push(tableSymbol);

            parents.table = tableSymbol;
            continue;
          }

          // 🔍 Detect Unnamed Tables
          if (unnamedTableRegex.test(line)) {
            const tableStartLine = lineNum;
            let tableEndLine = lineNum;
            let containsCaptionsetup = false;

            // Scan forward to find \end{table} and check for \captionsetup{type=table}
            for (let i = lineNum; i < lines.length; i++) {
              if (lines[i].includes("\\captionsetup{type=table}")) {
                containsCaptionsetup = true;
              }
              if (lines[i].includes("\\end{table}")) {
                tableEndLine = i;
                break;
              }
            }

            // ✅ Only mark it as an "Unnamed Table" if it DOES NOT contain \captionsetup{type=table}
            if (!containsCaptionsetup) {
              const position = new vscode.Position(tableStartLine, 0);
              const tableSymbol = new vscode.DocumentSymbol(
                " ",
                "Table ",
                vscode.SymbolKind.Struct,
                new vscode.Range(position, new vscode.Position(tableEndLine, 0)),
                new vscode.Range(position, position)
              );

              if (lastParent) {
                lastParent.children.push(tableSymbol);
              } else {
                symbols.push(tableSymbol);
              }
            }

            continue;
          }

          // 🖼️ Figure Detection (legacy/captionsetup style)
          if (captionSetupFigureRegex.test(line)) {
            const position = new vscode.Position(lineNum, 0);
            const figureSymbol = new vscode.DocumentSymbol(
              " ",
              "Figure",
              vscode.SymbolKind.Image,
              new vscode.Range(position, position),
              new vscode.Range(position, position)
            );

            let parent = parents.subsection || parents.section || parents.chapter;
            if (parent) parent.children.push(figureSymbol);
            else symbols.push(figureSymbol);

            parents.figure = figureSymbol;
            continue;
          }

          // 🎯 Caption Detection for tables and figures (only used by 'captionsetup' logic now)
          let captionMatch = captionRegex.exec(line);
          if (captionMatch) {
            let captionText = captionMatch[1];

            if (parents.table) {
              parents.table.name = captionText;
              parents.table = null;
            } else if (parents.figure) {
              parents.figure.name = captionText;
              parents.figure = null;
            }
            continue;
          }
        }

        return symbols;
      },
    }
  );
  context.subscriptions.push(provider);
}

function deactivate() {}

module.exports = { activate, deactivate };
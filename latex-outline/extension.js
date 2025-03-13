const vscode = require("vscode");

function activate(context) {
  const provider = vscode.languages.registerDocumentSymbolProvider(
    { language: "latex" },
    {
      provideDocumentSymbols(document) {
        const symbols = [];
        const parents = {
          part: null,
          chapter: null,
          section: null,
          subsection: null,
          subsubsection: null,
        };

        let insideAppendix = false;
        let appendixSymbol = null;
        let pendingFigure = false;
        let pendingFigurePosition = null;

        const text = document.getText();
        const lines = text.split("\n");

        const regex = /\\(part|chapter|section|subsection|subsubsection)\*?\{([^}]+)\}/;
        const specialRegex = /\\(title|maketitle|tableofcontents|listoftables|listoffigures)/;
        const titlePageRegex = /\\begin\{titlepage\}/;
        const endTitlePageRegex = /\\end\{titlepage\}/;
        const figureRegex = /\\begin\{figure\*?\}/;
        const tableRegex = /\\begin\{table\*?\}/;
        const captionRegex = /\\caption\{([^}]+)\}/;
        const endEnvRegex = /\\end\{(figure|figure\*|table|table\*)\}/;

        // New regex to detect bibliography
        const bibliographyRegex = /\\bibliography\{[^}]+\}/;

        let insideTitlePage = false;
        let insideFigureOrTable = false;
        let currentFigureOrTable = null;

        for (let lineNum = 0; lineNum < lines.length; lineNum++) {
          let line = lines[lineNum].trim();

          if (line.startsWith("%")) continue;

          // Detect \bibliography{...} and add "References" to outline
          if (bibliographyRegex.test(line)) {
            const position = new vscode.Position(lineNum, 0);
            const symbol = new vscode.DocumentSymbol(
              "References",
              "chapter",
              vscode.SymbolKind.Class,
              new vscode.Range(position, position),
              new vscode.Range(position, position)
            );
            symbols.push(symbol);
            continue;
          }

          // Handle \appendix
          if (line === "\\appendix") {
            insideAppendix = true;
            const position = new vscode.Position(lineNum, 0);
            appendixSymbol = new vscode.DocumentSymbol(
              "Appendix",
              "",
              vscode.SymbolKind.Namespace,
              new vscode.Range(position, position),
              new vscode.Range(position, position)
            );
            symbols.push(appendixSymbol);
            continue;
          }

          if (titlePageRegex.test(line)) {
            insideTitlePage = true;
            const position = new vscode.Position(lineNum, 0);
            const symbol = new vscode.DocumentSymbol(
              "Title Page",
              "",
              vscode.SymbolKind.File,
              new vscode.Range(position, position),
              new vscode.Range(position, position)
            );
            symbols.push(symbol);
            continue;
          }

          if (insideTitlePage && endTitlePageRegex.test(line)) {
            insideTitlePage = false;
            continue;
          }

          let match = regex.exec(line);
          if (match) {
            const sectionType = match[1];
            const isStarred = match[0].includes("*");
            const title = match[2];

            const kind = {
              part: vscode.SymbolKind.Package,
              chapter: vscode.SymbolKind.Class,
              section: vscode.SymbolKind.Namespace,
              subsection: vscode.SymbolKind.Module,
              subsubsection: vscode.SymbolKind.Method,
            }[sectionType];

            const position = new vscode.Position(lineNum, match.index);
            const symbol = new vscode.DocumentSymbol(
              title,
              isStarred ? sectionType + "*" : sectionType,
              kind,
              new vscode.Range(position, position),
              new vscode.Range(position, position)
            );

            if (sectionType === "chapter") {
              if (insideAppendix && appendixSymbol) {
                appendixSymbol.children.push(symbol);
              } else {
                symbols.push(symbol);
              }
              parents.chapter = symbol;
              parents.section = null;
              parents.subsection = null;
            } else if (sectionType === "section") {
              if (parents.chapter) {
                parents.chapter.children.push(symbol);
              } else {
                symbols.push(symbol);
              }
              parents.section = symbol;
              parents.subsection = null;
            } else if (sectionType === "subsection") {
              if (parents.section) {
                parents.section.children.push(symbol);
              } else {
                symbols.push(symbol);
              }
              parents.subsection = symbol;
            } else if (sectionType === "subsubsection") {
              if (parents.subsection) {
                parents.subsection.children.push(symbol);
              } else {
                symbols.push(symbol);
              }
            }
          }

          let specialMatch = specialRegex.exec(line);
          if (specialMatch) {
            const command = specialMatch[1];
            let kind = vscode.SymbolKind.File;
            let title = "";

            if (command === "maketitle") {
              title = "Title Page";
            } else if (command === "tableofcontents") {
              title = "Table of Contents";
            } else if (command === "listoftables") {
              title = "List of Tables";
            } else if (command === "listoffigures") {
              title = "List of Figures";
            }

            if (title) {
              const position = new vscode.Position(lineNum, specialMatch.index);
              const symbol = new vscode.DocumentSymbol(
                title,
                "",
                kind,
                new vscode.Range(position, position),
                new vscode.Range(position, position)
              );
              symbols.push(symbol);
            }
          }

          if (/\\captionsetup\{type=figure\}/.test(line)) {
            pendingFigure = true;
            pendingFigurePosition = new vscode.Position(lineNum, 0);
            continue;
          }

          if (figureRegex.test(line) || tableRegex.test(line)) {
            insideFigureOrTable = true;
            currentFigureOrTable = {
              type: figureRegex.test(line) ? "Figure" : "Table",
              title: "",
              position: new vscode.Position(lineNum, 0),
            };
            continue;
          }

          let captionMatch = captionRegex.exec(line);
          if (captionMatch) {
            let captionText = captionMatch[1];

            if (insideFigureOrTable) {
              currentFigureOrTable.title = captionText;
            } else if (pendingFigure) {
              const symbol = new vscode.DocumentSymbol(
                captionText,
                "Figure",
                vscode.SymbolKind.Image,
                new vscode.Range(pendingFigurePosition, pendingFigurePosition),
                new vscode.Range(pendingFigurePosition, pendingFigurePosition)
              );

              if (parents.subsection) {
                parents.subsection.children.push(symbol);
              } else if (parents.section) {
                parents.section.children.push(symbol);
              } else if (parents.chapter) {
                parents.chapter.children.push(symbol);
              } else {
                symbols.push(symbol);
              }

              pendingFigure = false;
            }
          }

          if (insideFigureOrTable && endEnvRegex.test(line)) {
            insideFigureOrTable = false;

            const kind =
              currentFigureOrTable.type === "Figure"
                ? vscode.SymbolKind.Image
                : vscode.SymbolKind.Struct;

            const symbol = new vscode.DocumentSymbol(
              currentFigureOrTable.title || " ",
              currentFigureOrTable.type,
              kind,
              new vscode.Range(currentFigureOrTable.position, currentFigureOrTable.position),
              new vscode.Range(currentFigureOrTable.position, currentFigureOrTable.position)
            );

            if (parents.subsection) {
              parents.subsection.children.push(symbol);
            } else if (parents.section) {
              parents.section.children.push(symbol);
            } else if (parents.chapter) {
              parents.chapter.children.push(symbol);
            } else {
              symbols.push(symbol);
            }
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


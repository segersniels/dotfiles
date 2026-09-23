const CONTROL_BLOCK_TYPES = new Set([
  "DoWhileStatement",
  "ForInStatement",
  "ForOfStatement",
  "ForStatement",
  "IfStatement",
  "SwitchStatement",
  "TryStatement",
  "WhileStatement",
]);

const CONTROL_TRANSFER_TYPES = new Set([
  "ContinueStatement",
  "ReturnStatement",
  "ThrowStatement",
]);

function getLines(context) {
  return context.sourceCode.text.split(/\r?\n/);
}

function isBlank(line) {
  return line === undefined || line.trim() === "";
}

function isClosingLine(line) {
  return /^[})\]]/.test(line.trim());
}

function hasBlankLineAfter(lines, lineNumber) {
  const nextLine = lines[lineNumber];

  return isBlank(nextLine) || isClosingLine(nextLine);
}

function hasBlankLineBefore(lines, lineNumber) {
  const previousLine = lines[lineNumber - 2];

  return (
    isBlank(previousLine) ||
    previousLine?.trim().endsWith("{") ||
    previousLine?.trim().endsWith(":")
  );
}

function hasBlankLineBetween(lines, previousNode, nextNode) {
  const previousEndLine = getEndLine(previousNode);
  const nextStartLine = getStartLine(nextNode);

  if (!previousEndLine || !nextStartLine) {
    return false;
  }

  return lines.slice(previousEndLine, nextStartLine - 1).some(isBlank);
}

function getStartLine(node) {
  return node.loc?.start.line ?? node.loc?.start.lineNumber;
}

function getEndLine(node) {
  return node.loc?.end.line ?? node.loc?.end.lineNumber;
}

function isLogicalBlock(node) {
  return Boolean(node && CONTROL_BLOCK_TYPES.has(node.type));
}

function isSingleLine(node) {
  if (!node) {
    return false;
  }

  const startLine = getStartLine(node);
  const endLine = getEndLine(node);

  return Boolean(startLine && endLine && startLine === endLine);
}

function isMultiline(node) {
  const startLine = getStartLine(node);
  const endLine = getEndLine(node);

  return Boolean(startLine && endLine && endLine > startLine);
}

function isDirectiveComment(comment) {
  return /^(eslint|oxlint|biome|prettier|@ts-|ts-|\/\/)/.test(
    comment.value.trim(),
  );
}

function isDividerComment(comment) {
  const value = comment.value.trim();

  return value.length >= 3 && /^[-=_*/]+$/.test(value);
}

function isCommentGroupContinuation(previousComment, comment) {
  const previousEndLine = getEndLine(previousComment);
  const startLine = getStartLine(comment);

  return Boolean(previousEndLine && startLine && startLine === previousEndLine + 1);
}

const blankLineAfterLogicalBlock = {
  create(context) {
    const lines = getLines(context);

    function check(node) {
      const endLine = getEndLine(node);

      if (!endLine || hasBlankLineAfter(lines, endLine)) {
        return;
      }

      context.report({
        node,
        message: "Expected a blank line after this logical block.",
      });
    }

    return Object.fromEntries(
      [...CONTROL_BLOCK_TYPES].map((type) => [type, check]),
    );
  },
};

const blankLineBeforeControlTransfer = {
  create(context) {
    const lines = getLines(context);

    function check(node) {
      const startLine = getStartLine(node);

      if (!startLine || hasBlankLineBefore(lines, startLine)) {
        return;
      }

      context.report({
        node,
        message: "Expected a blank line before this control-transfer statement.",
      });
    }

    return Object.fromEntries(
      [...CONTROL_TRANSFER_TYPES].map((type) => [type, check]),
    );
  },
};

const blankLineBetweenSwitchCases = {
  create(context) {
    const lines = getLines(context);

    return {
      SwitchStatement(node) {
        for (const switchCase of node.cases.slice(1)) {
          const startLine = getStartLine(switchCase);

          if (!startLine || hasBlankLineBefore(lines, startLine)) {
            continue;
          }

          context.report({
            node: switchCase,
            message: "Expected a blank line before this switch case.",
          });
        }
      },
    };
  },
};

const blankLineBeforeLogicalBlockAfterMultiline = {
  create(context) {
    const lines = getLines(context);

    function checkStatements(statements) {
      for (let index = 1; index < statements.length; index++) {
        const previousNode = statements[index - 1];
        const nextNode = statements[index];

        if (
          isLogicalBlock(previousNode) ||
          !isMultiline(previousNode) ||
          !isLogicalBlock(nextNode) ||
          hasBlankLineBetween(lines, previousNode, nextNode)
        ) {
          continue;
        }

        context.report({
          node: nextNode,
          message:
            "Expected a blank line between the multi-line statement and this logical block.",
        });
      }
    }

    return {
      BlockStatement(node) {
        checkStatements(node.body);
      },
      Program(node) {
        checkStatements(node.body);
      },
      SwitchCase(node) {
        checkStatements(node.consequent);
      },
    };
  },
};

const useJsdocForMultilineBlockComments = {
  create(context) {
    return {
      Program(node) {
        for (const comment of context.sourceCode.getAllComments()) {
          if (comment.type !== "Block" || isSingleLine(comment)) {
            continue;
          }

          if (comment.value.startsWith("*")) {
            continue;
          }

          context.report({
            node,
            loc: comment.loc.start,
            message: "Expected multi-line block comments to use JSDoc syntax.",
          });
        }
      },
    };
  },
};

const useJsdocForMultilineLineComments = {
  create(context) {
    return {
      Program(node) {
        const comments = context.sourceCode.getAllComments();
        let group = [];

        function reportGroup() {
          if (group.length < 2 || group.some(isDirectiveComment) || group.some(isDividerComment)) {
            return;
          }

          context.report({
            node,
            loc: {
              start: group[0].loc.start,
              end: group.at(-1).loc.end,
            },
            message:
              "Expected multi-line // comment groups to use JSDoc syntax.",
          });
        }

        for (const comment of comments) {
          if (comment.type !== "Line") {
            reportGroup();
            group = [];
            continue;
          }

          const previousComment = group.at(-1);

          if (previousComment && !isCommentGroupContinuation(previousComment, comment)) {
            reportGroup();
            group = [];
          }

          group.push(comment);
        }

        reportGroup();
      },
    };
  },
};

const useLineCommentForSingleLineComments = {
  create(context) {
    return {
      Program(node) {
        for (const comment of context.sourceCode.getAllComments()) {
          if (comment.type !== "Block" || !isSingleLine(comment)) {
            continue;
          }

          if (comment.value.startsWith("*")) {
            continue;
          }

          context.report({
            node,
            loc: comment.loc.start,
            message: "Expected single-line comments to use // syntax.",
          });
        }
      },
    };
  },
};

export default {
  meta: {
    name: "human-code-style",
  },
  rules: {
    "blank-line-after-logical-block": blankLineAfterLogicalBlock,
    "blank-line-before-control-transfer": blankLineBeforeControlTransfer,
    "blank-line-between-switch-cases": blankLineBetweenSwitchCases,
    "blank-line-before-logical-block-after-multiline":
      blankLineBeforeLogicalBlockAfterMultiline,
    "use-jsdoc-for-multiline-block-comments":
      useJsdocForMultilineBlockComments,
    "use-jsdoc-for-multiline-line-comments":
      useJsdocForMultilineLineComments,
    "use-line-comment-for-single-line-comments":
      useLineCommentForSingleLineComments,
  },
};

"use strict";

const cm_instances = new Map();

async function main() {
  // let indexURL = my_host + "livro/pyodide-core/";
  let indexURL = "https://heitorchang.github.io/programopy/livro/pyodide-core/";
  const urlParams = new URLSearchParams(window.location.search);
  const buildParam = urlParams.get("build");
  if (buildParam) {
    if (["full", "debug", "pyc"].includes(buildParam)) {
      indexURL = indexURL.replace(
        "/full/",
        "/" + urlParams.get("build") + "/",
      );
    } else {
      console.warn(
        'Invalid URL parameter: build="' +
        buildParam +
        '". Using default "full".',
      );
    }
  }
  const { loadPyodide } = await import(indexURL + "pyodide.mjs");
  // to facilitate debugging
  globalThis.loadPyodide = loadPyodide;

  let term;
  globalThis.pyodide = await loadPyodide({
    stdin: () => {
      let result = prompt();
      echo(result);
      return result;
    },
  });
  let namespace = pyodide.globals.get("dict")();
  pyodide.runPython(
    `
            import sys
            from pyodide.ffi import to_js
            from pyodide.console import PyodideConsole, repr_shorten
            import __main__
            pyconsole = PyodideConsole(__main__.__dict__)
            import builtins
            async def await_fut(fut):
              res = await fut
              if res is not None:
                builtins._ = res
              return to_js([res], depth=1)
            def clear_console():
              pyconsole.buffer = []
    `,
    { globals: namespace },
  );
  let repr_shorten = namespace.get("repr_shorten");

  let await_fut = namespace.get("await_fut");
  let pyconsole = namespace.get("pyconsole");
  let clear_console = namespace.get("clear_console");
  const echo = (msg, ...opts) =>
    term.echo(
      msg
        .replaceAll("]]", "&rsqb;&rsqb;")
        .replaceAll("[[", "&lsqb;&lsqb;"),
      ...opts,
    );
  namespace.destroy();

  let ps1 = ">>> ",
      ps2 = "... ";

  async function lock() {
    let resolve;
    let ready = term.ready;
    term.ready = new Promise((res) => (resolve = res));
    await ready;
    return resolve;
  }

  async function interpreter(command) {
    let unlock = await lock();
    term.pause();
    // multiline should be split (useful when pasting)
    for (const c of command.split("\n")) {
      const escaped = c.replaceAll(/\u00a0/g, " ");
      let fut = pyconsole.push(escaped);
      term.set_prompt(fut.syntax_check === "incomplete" ? ps2 : ps1);
      switch (fut.syntax_check) {
        case "syntax-error":
          term.error(fut.formatted_error.trimEnd());
          continue;
        case "incomplete":
          continue;
        case "complete":
          break;
        default:
          throw new Error(`Unexpected type ${ty}`);
      }
      // In JavaScript, await automatically also awaits any results of
      // awaits, so if an async function returns a future, it will await
      // the inner future too. This is not what we want so we
      // temporarily put it into a list to protect it.
      let wrapped = await_fut(fut);
      // complete case, get result / error and print it.
      try {
        let [value] = await wrapped;
        if (value !== undefined) {
          echo(
            repr_shorten.callKwargs(value, {
              separator: "\n<long output truncated>\n",
            }),
          );
        }
        if (value instanceof pyodide.ffi.PyProxy) {
          value.destroy();
        }
      } catch (e) {
        if (e.constructor.name === "PythonError") {
          const message = fut.formatted_error || e.message;
          term.error(message.trimEnd());
        } else {
          throw e;
        }
      } finally {
        fut.destroy();
        wrapped.destroy();
      }
    }
    term.resume();
    await sleep(10);
    unlock();
  }

  term = $("body").terminal(interpreter, {
    greetings: 'Interpretador Python 3.11.3 (Pyodide Core)',
    prompt: ps1,
    completionEscape: false,
    completion: function (command, callback) {
      callback(pyconsole.complete(command).toJs()[0]);
    },
    keymap: {
      "CTRL+C": async function (event, original) {
        clear_console();
        term.enter();
        echo("KeyboardInterrupt");
        term.set_command("");
        term.set_prompt(ps1);
      },
      TAB: (event, original) => {
        const command = term.before_cursor();
        // Disable completion for whitespaces.
        if (command.trim() === "") {
          term.insert("\t");
          return false;
        }
        return original(event);
      },
      "CTRL+Q": (event, original) => {
         term.disable();
      },
    },
  });
  window.term = term;
  pyconsole.stdout_callback = (s) => echo(s, { newline: false });
  pyconsole.stderr_callback = (s) => {
    term.error(s.trimEnd());
  };
  term.ready = Promise.resolve();
  $("#loading").hide();
  $("#content").show();
  // hide the blinking cursor
  term.disable();

  const textareas = $('#content textarea')
  textareas.each((index, ta) => {
    cm_instances.set(ta.id, CodeMirror.fromTextArea(ta, codemirrorOptions));
  });

  pyodide._api.on_fatal = async (e) => {
    if (e.name === "Exit") {
      term.error(e);
      term.error("Pyodide exited and can no longer be used.");
    } else {
      term.error(
        "Pyodide has suffered a fatal error. Please report this to the Pyodide maintainers.",
      );
      term.error("The cause of the fatal error was:");
      term.error(e);
      term.error("Look in the browser console for more details.");
    }
    await term.ready;
    term.pause();
    await sleep(15);
    term.pause();
  };

  const searchParams = new URLSearchParams(window.location.search);
  if (searchParams.has("noblink")) {
    $(".cmd-cursor").addClass("noblink");
  }
}
window.console_ready = main();

function sleep(s) {
  return new Promise((resolve) => setTimeout(resolve, s));
}

function sendToInterpreter(py) {
  py = py.trim();
  // remove blank lines
  py = py.replace(/^\s*$(?:\r\n?|\n)/gm, "");

  // separate entire text into logical blocks
  // otherwise, a def ... followed by the function call doesn't work

  const logical_blocks = [];

  const lines = py.split(/\r?\n|\r|\n/g);
  let current_line = '';
  let current_block = '';

  for (let i = 0; i < lines.length; i++) {
    current_line = lines[i];
    // replace tabs with 4 spaces
    current_line = current_line.replaceAll('\t', '    ');
    if (i > 0 && current_line.substring(0, 1) !== ' ') {
      logical_blocks.push(current_block);
      current_block = '';
    }
    current_block += current_line + '\n';
  }

  // add whatever remains
  if (current_block !== '') {
    logical_blocks.push(current_block);
  }
  console.log(logical_blocks);
  logical_blocks.forEach((block) => {
    term.exec(block);
  });
  // window.setTimeout(term.focus, 150);
}

function sendTextarea(id) {
  cm_instances.get(id).save();
  const py = $("#" + id).val();
  sendToInterpreter(py);
}

/*
function captureShiftEnter(event) {
  if (event.shiftKey && event.keyCode === 13) {
    event.preventDefault();
    sendTextarea(event.target.id);
  }
}
*/
